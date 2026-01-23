# main.py
# SecurePrompt — LLM Pentesting Tool (CLI)

import argparse
import importlib.util
import json
import os
import time
import sys
from pathlib import Path

from attacker.loader import load_attacks
from evaluator.rules import apply_rules
from evaluator.openai_judge import judge_batch  # Use OpenAI judge instead of local
from scoring.risk import compute_risk

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

JUDGE_BATCH_SIZE = 10
JUDGE_INTERVAL = 10  # seconds between HF calls

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

console = Console()


# ─────────────────────────────────────────────────────────────
# TIMING
# ─────────────────────────────────────────────────────────────

timing = {
    "start": 0.0,
    "end": 0.0,
    "attacks": 0,
    "target_time": 0.0,
    "judge_time": 0.0,
}


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def load_target(path):
    path = os.path.abspath(path)

    spec = importlib.util.spec_from_file_location("secureprompt_target", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load target module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "run"):
        raise RuntimeError("Target must define run(prompt: str)")

    return module.run


def print_attack_result(attack_id, category, verdict, risk):
    color = {
        "pass": "green",
        "partial": "yellow",
        "fail": "red",
    }.get(verdict["verdict"], "white")

    console.print(
        f"[bold]{attack_id}[/bold] "
        f"{category:<22} → "
        f"[{color}]{verdict['verdict'].upper():<7}[/{color}] "
        f"({risk['risk_level']})"
    )


def print_summary(report):
    console.print("\n[bold cyan]=== Scan Summary ===[/bold cyan]")
    console.print(f"Total attacks: {len(report)}")
    console.print(f"Fails: {sum(r['verdict']['verdict']=='fail' for r in report)}")
    console.print(f"Partials: {sum(r['verdict']['verdict']=='partial' for r in report)}")
    console.print(f"Passes: {sum(r['verdict']['verdict']=='pass' for r in report)}")


def print_timing():
    total = timing["end"] - timing["start"]
    console.print("\n[bold cyan]=== Timing ===[/bold cyan]")
    console.print(f"Total scan time: {total:.2f}s")
    if timing["attacks"]:
        console.print(
            f"Avg model time: {timing['target_time']/timing['attacks']:.2f}s"
        )
        console.print(
            f"Avg judge time: {timing['judge_time']/timing['attacks']:.2f}s"
        )


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SecurePrompt — LLM Pentesting Tool")
    parser.add_argument("--target", required=True, help="Path to target module")
    parser.add_argument("--attacks", default="attacks", help="Path to attacks directory")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument(
        "--mode",
        choices=["static", "adaptive"],
        default="static",
        help="Attack mode: static (use attacks as-is) or adaptive (evolve attacks)"
    )
    parser.add_argument(
        "--adaptive-model",
        default=r"E:\SecurePrompt\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        help="Path to mini SLM for adaptive mode (local)"
    )
    parser.add_argument(
        "--adaptive-api",
        default=None,
        help="API key for adaptive mode (OpenAI/Claude). If provided, uses API instead of local LLM."
    )
    parser.add_argument(
        "--adaptive-provider",
        choices=["openai", "claude"],
        default="openai",
        help="API provider for adaptive mode (requires --adaptive-api)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Max iterations for adaptive mode"
    )
    parser.add_argument(
        "--adaptive-strategy",
        choices=["mutation", "recon"],
        default="mutation",
        help="Adaptive strategy: mutation (evolve attacks) or recon (intelligence-based)"
    )
    parser.add_argument(
        "--probe-diversity",
        type=int,
        default=3,
        help="Number of diverse probe attacks for recon mode (default: 3)"
    )
    args = parser.parse_args()

    console.print(f"\n[bold cyan]SecurePrompt starting… (mode: {args.mode})[/bold cyan]\n")
    timing["start"] = time.perf_counter()

    # Initialize adaptive engine if needed
    adaptive_attacker = None
    if args.mode == "adaptive":
        # Choose API or local based on flag
        if args.adaptive_api:
            # Use API-based mutation engine
            from adaptive.api_mutation_engine import APIMutationEngine
            
            console.print(f"[yellow]⚡ Initializing Adaptive Engine (API: {args.adaptive_provider})...[/yellow]")
            try:
                mutation_engine = APIMutationEngine(
                    api_key=args.adaptive_api,
                    provider=args.adaptive_provider,
                    verbose=False
                )
            except Exception as e:
                console.print(f"[red]✗ Failed to initialize API engine: {e}[/red]")
                console.print("[yellow]Tip: Check your API key and provider[/yellow]")
                sys.exit(1)
        else:
            # Use local LLM mutation engine
            from adaptive.mutation_engine import MutationEngine
            
            console.print("[yellow]⚡ Initializing Adaptive Engine (Local LLM)...[/yellow]")
            try:
                mutation_engine = MutationEngine(args.adaptive_model, verbose=False)
            except Exception as e:
                console.print(f"[red]✗ Failed to load local model: {e}[/red]")
                console.print("[yellow]Tip: Use --adaptive-api for API-based mode (no local LLM needed)[/yellow]")
                sys.exit(1)
        
        
        # Create adaptive attacker based on strategy
        if args.adaptive_strategy == "recon":
            from adaptive.intelligent_attacker import IntelligentAdaptiveAttacker
            
            adaptive_attacker = IntelligentAdaptiveAttacker(
                mutation_engine=mutation_engine,
                max_craft_attempts=args.max_iterations,
                verbose=False
            )
            console.print(f"[green]✔ Adaptive engine ready (Recon strategy, {args.probe_diversity} probes)[/green]\n")
        else:  # mutation
            from adaptive.mutation_engine import AdaptiveAttacker
            
            adaptive_attacker = AdaptiveAttacker(
                mutation_engine=mutation_engine,
                max_iterations=args.max_iterations,
                verbose=False
            )
            console.print("[green]✔ Adaptive engine ready (Mutation strategy)[/green]\n")

    # Load target
    with Progress(SpinnerColumn(), TextColumn("Loading target…"), console=console):
        run_target = load_target(args.target)

    console.print("[green]✔ Target loaded[/green]\n")

    # Load attacks
    attacks = load_attacks(args.attacks)
    console.print(f"[bold]Loaded {len(attacks)} attacks[/bold]\n")

    report = []

    # Judge batching state
    pending = []
    judge_results = {}
    last_judge_time = 0.0

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Running attacks…", total=len(attacks))

        for attack in attacks:
            progress.update(task, description=f"{attack['id']} ({attack['category']})")

            # ADAPTIVE MODE - Use mutation engine
            if args.mode == "adaptive" and adaptive_attacker:
                result = adaptive_attacker.attack(
                    original_attack=attack,
                    target_func=run_target,
                    evaluator_func=lambda p, r: apply_rules(p, r)
                )
                
                # Use final iteration result
                response = result["final_response"]
                verdict = apply_rules(attack["prompt"], response)
                
                if verdict is None:
                    # Still uncertain after adaptive attempts
                    verdict = {
                        "verdict": "partial",
                        "confidence": 0.0,
                        "severity": 0.0,
                        "rationale": f"adaptive_uncertain_after_{result['iterations']}_iterations",
                    }
                
                # Add adaptive metadata
                attack_record = {
                    "attack_id": attack["id"],
                    "category": attack["category"],
                    "verdict": verdict,
                    "risk": compute_risk(verdict),
                    "adaptive_metadata": {
                        "iterations": result["iterations"],
                        "success": result["success"],
                        "final_payload": result["final_payload"][:100],
                        "mutation_history": result["mutation_history"]
                    }
                }
            
            # STATIC MODE - Original behavior
            else:
                # Run model
                t0 = time.perf_counter()
                response = run_target(attack["prompt"])
                t1 = time.perf_counter()

                # RULES FIRST
                t2 = time.perf_counter()
                verdict = apply_rules(attack["prompt"], response)
                t3 = time.perf_counter()

                if verdict is None:
                    verdict = {
                        "verdict": "partial",
                        "confidence": 0.0,
                        "severity": 0.0,
                        "rationale": "requires_judge",
                    }
                    pending.append({
                        "id": attack["id"],
                        "attack_prompt": attack["prompt"],
                        "model_response": response,
                    })

            # Batch judge when ready
            if len(pending) >= JUDGE_BATCH_SIZE:
                wait = max(0, JUDGE_INTERVAL - (time.time() - last_judge_time))
                if wait:
                    time.sleep(wait)

                t4 = time.perf_counter()
                batch = judge_batch(pending)
                t5 = time.perf_counter()

                judge_results.update(batch)
                pending.clear()
                last_judge_time = time.time()
                timing["judge_time"] += (t5 - t4)

            # Merge judge result if exists (static mode only)
            if attack["id"] in judge_results:
                verdict = judge_results[attack["id"]]

            risk = compute_risk(verdict)

            timing["attacks"] += 1
            if args.mode == "static":
                timing["target_time"] += (t1 - t0)
                timing["judge_time"] += (t3 - t2)

            print_attack_result(attack["id"], attack["category"], verdict, risk)

            # Build report entry
            if args.mode == "adaptive" and adaptive_attacker:
                report.append(attack_record)  # Already built in adaptive block
            else:
                report.append({
                    "attack_id": attack["id"],
                    "category": attack["category"],
                    "verdict": verdict,
                    "risk": risk,
                })

            progress.advance(task)

    # Flush remaining judge cases
    if pending:
        time.sleep(JUDGE_INTERVAL)
        batch = judge_batch(pending)
        for entry in report:
            if entry["attack_id"] in batch:
                entry["verdict"] = batch[entry["attack_id"]]
                entry["risk"] = compute_risk(entry["verdict"])

    timing["end"] = time.perf_counter()

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print_summary(report)
    print_timing()

    console.print(
        f"\n[green bold]✔ Scan complete[/green bold] → {args.output}\n"
    )

    sys.exit(0)


if __name__ == "__main__":
    main()
