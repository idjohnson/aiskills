#!/usr/bin/env python3
"""
ASD-STE100 Issue 9 Text Validation Checker
Checks technical text against key ASD-STE100 Issue 9 writing rules.
"""

import sys
import os
import re
import json
import argparse

CONTRACTIONS = [
    r"\bcan't\b", r"\bdon't\b", r"\bdoesn't\b", r"\bwon't\b", r"\bisn't\b",
    r"\baren't\b", r"\bwasn't\b", r"\bweren't\b", r"\bhasn't\b", r"\bhaven't\b",
    r"\bhadn't\b", r"\bshouldn't\b", r"\bcouldn't\b", r"\bmightn't\b", r"\bit's\b"
]

FORBIDDEN_MODALS = ["should", "could", "might", "may", "shall", "would"]

PHRASAL_VERBS = [
    "carry out", "put off", "take off", "set up", "blow up", "go through",
    "point out", "turn off", "turn on", "bring about", "rule out"
]

def check_ste_compliance(text, text_type="procedure"):
    max_words = 20 if text_type == "procedure" else 25
    script_dir = os.path.dirname(os.path.realpath(__file__))
    map_path = os.path.join(script_dir, "../references/unapproved_words_map.json")

    unapproved_map = {}
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            unapproved_map = json.load(f)

    # Split into sentences
    raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    issues = []

    for idx, sentence in enumerate(sentences, 1):
        # 1. Check Semicolons (Rule 8.1)
        if ";" in sentence:
            issues.append({
                "sentence_num": idx,
                "rule": "Rule 8.1 (No Semicolons)",
                "message": "Semicolon ';' detected. Semicolons are prohibited in STE. Replace with a period or comma.",
                "sentence": sentence
            })

        # 2. Check Word Count (Rule 5.1 / Rule 6.3)
        # Parentheses count as 1 word (Rule 8.5)
        clean_s = re.sub(r"\([^)]*\)", "PAREN_ITEM", sentence)
        words = clean_s.split()
        word_count = len(words)

        if word_count > max_words:
            issues.append({
                "sentence_num": idx,
                "rule": f"Rule {'5.1' if text_type == 'procedure' else '6.3'} (Sentence Length)",
                "message": f"Sentence has {word_count} words (Exceeds maximum limit of {max_words} words).",
                "sentence": sentence
            })

        # 3. Check Contractions (Rule 4.2)
        for c_pat in CONTRACTIONS:
            if re.search(c_pat, sentence, re.IGNORECASE):
                issues.append({
                    "sentence_num": idx,
                    "rule": "Rule 4.2 (No Contractions)",
                    "message": f"Contraction detected matching '{c_pat}'. Write words out in full.",
                    "sentence": sentence
                })

        # 4. Check Forbidden Modals (Rule 3.4)
        for modal in FORBIDDEN_MODALS:
            if re.search(rf"\b{modal}\b", sentence, re.IGNORECASE):
                issues.append({
                    "sentence_num": idx,
                    "rule": "Rule 3.4 (No Complex Auxiliaries)",
                    "message": f"Forbidden modal verb '{modal}' detected. Use 'must', 'can', or imperative command.",
                    "sentence": sentence
                })

        # 5. Check Phrasal Verbs (Rule 9.3)
        for pv in PHRASAL_VERBS:
            if re.search(rf"\b{pv}\b", sentence, re.IGNORECASE):
                issues.append({
                    "sentence_num": idx,
                    "rule": "Rule 9.3 (No Phrasal Verbs)",
                    "message": f"Phrasal verb '{pv}' detected. Replace with an approved simple verb.",
                    "sentence": sentence
                })

        # 6. Check Unapproved Words
        words_in_s = re.findall(r"\b[a-zA-Z]+\b", sentence)
        for w in words_in_s:
            w_lower = w.lower()
            if w_lower in unapproved_map:
                entry = unapproved_map[w_lower]
                issues.append({
                    "sentence_num": idx,
                    "rule": "Rule 1.1 (Unapproved Word)",
                    "message": f"Unapproved word '{w}' ({entry['pos']}) detected. Approved Alternative: '{entry['approved_alternative']}'",
                    "sentence": sentence
                })

    return sentences, issues

def main():
    parser = argparse.ArgumentParser(description="Validate text against ASD-STE100 Issue 9 rules")
    parser.add_argument("text", nargs="?", help="Text string to analyze")
    parser.add_argument("--file", help="Path to text file to analyze")
    parser.add_argument("--type", choices=["procedure", "description"], default="procedure", help="Text type (procedure or description)")
    args = parser.parse_args()

    content = ""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.text:
        content = args.text
    else:
        print("Usage: python3 ste_checker.py \"text\" OR --file filename.txt")
        sys.exit(1)

    sentences, issues = check_ste_compliance(content, args.type)

    print(f"\n=======================================================")
    print(f" ASD-STE100 Issue 9 Compliance Report ({args.type.title()})")
    print(f"=======================================================")
    print(f"Total Sentences Analyzed: {len(sentences)}")
    print(f"Total STE Rule Violations Found: {len(issues)}\n")

    if not issues:
        print("\033[92mSUCCESS: No major ASD-STE100 rule violations detected!\033[0m\n")
        return

    for issue in issues:
        print(f"\033[91m[Sentence #{issue['sentence_num']}] {issue['rule']}\033[0m")
        print(f"   Violation: {issue['message']}")
        print(f"   Text: \"{issue['sentence']}\"")
        print("-" * 55)

if __name__ == "__main__":
    main()
