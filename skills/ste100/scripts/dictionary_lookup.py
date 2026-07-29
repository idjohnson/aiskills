#!/usr/bin/env python3
"""
ASD-STE100 Issue 9 Dictionary Lookup Tool
Searches words in the official ASD-STE100 dictionary dataset.
"""

import sys
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Lookup words in ASD-STE100 Issue 9 Dictionary")
    parser.add_argument("word", nargs="?", help="Word to lookup")
    parser.add_argument("--json", action="store_true", help="Output raw JSON format")
    args = parser.parse_args()

    if not args.word:
        print("Usage: python3 dictionary_lookup.py <word>")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    dict_path = os.path.join(script_dir, "../references/dictionary.json")

    if not os.path.exists(dict_path):
        print(f"Error: Dictionary database not found at {dict_path}")
        sys.exit(1)

    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    target = args.word.strip().lower()
    matches = [item for item in data if item["word"].lower() == target]

    if not matches:
        # Try substring match
        matches = [item for item in data if target in item["word"].lower()]

    if not matches:
        print(f"No entry found for '{args.word}' in ASD-STE100 Issue 9 Dictionary.")
        sys.exit(0)

    if args.json:
        print(json.dumps(matches, indent=2))
        return

    print(f"\n==========================================")
    print(f" ASD-STE100 Issue 9 Lookup: '{args.word}'")
    print(f"==========================================\n")

    for item in matches:
        status = "APPROVED" if item["is_approved"] else "UNAPPROVED"
        color = "\033[92m" if item["is_approved"] else "\033[91m"
        reset = "\033[0m"

        print(f"Word: {item['word']} ({item['pos']})")
        print(f"Status: {color}{status}{reset}")
        print(f"Approved Meaning / Alternatives: {item['meaning_or_alternatives']}")
        if item["ste_example"]:
            print(f"STE Example: {item['ste_example']}")
        if item["non_ste_example"]:
            print(f"Non-STE Example: {item['non_ste_example']}")
        print("-" * 42)

if __name__ == "__main__":
    main()
