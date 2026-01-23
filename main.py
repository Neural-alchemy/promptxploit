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
    parser = argparse.ArgumentParser(description="PromptXploit — LLM Pentesting Tool")
    parser.add_argument("--target", required=True, help="Path to target module")
    parser.add_argument("--attacks", default="attacks", help="Path to attacks directory")
    parser.add_argument("--output", required=True, help="Output JSON file")
    
    args = parser.parse_args()

    console.print(f"\n[bold cyan]PromptXploit starting...[/bold cyan]\n")
    timing["start"] = time.perf_counter()

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
