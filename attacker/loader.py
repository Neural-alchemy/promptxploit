# attacker/loader.py
# Loads all attack JSON files recursively from the attacks directory

import json
import glob
import os


def load_attacks(path="attacks"):
    """
    Recursively load all JSON attack files under the given path.
    """

    attacks = []

    # Match all .json files in all subdirectories
    pattern = os.path.join(path, "**", "*.json")

    for file_path in glob.glob(pattern, recursive=True):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Each file must contain a list of attacks
            if isinstance(data, list):
                attacks.extend(data)
            else:
                raise ValueError(
                    f"Attack file {file_path} does not contain a JSON list"
                )

    return attacks
