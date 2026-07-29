---
name: ste100
description: ASD-STE100 Simplified Technical English (Issue 9, January 2025) specification skill. Enforces controlled language writing rules (Part 1, Sections 1–9), vocabulary dictionary lookups (Part 2), procedural & descriptive sentence constraints, safety warnings, and automated compliance checks.
---

# ASD-STE100 Issue 9 (Simplified Technical English) AI Skill

This skill equips AI assistants with the complete **ASD-STE100 Issue 9 (January 2025)** specification for preparing technical documentation in controlled English.

## Overview & Core Principles

ASD-STE100 Simplified Technical English (STE) is an international standard designed to make technical manuals clear, easy to read, unambiguous, and simple to translate.

### Key ASD-STE100 Rules Summary
1. **Vocabulary (Section 1)**: Use approved STE dictionary words strictly as their designated Part of Speech and approved meaning. Use Technical Nouns (TN) and Technical Verbs (TV) only from approved categories.
2. **Noun Clusters (Section 2)**: Limit multi-word noun clusters to a maximum of **3 words** unless it is an official registered technical name.
3. **Verb Forms (Section 3)**: Use only simple tenses (Present Simple active, Past Simple active, Future Simple with "will", Imperative, Past Participle as adjective). **NO passive voice in procedural writing**. **NO present continuous (-ing gerunds) except as approved TN/modifiers**. **NO complex modal auxiliaries** (avoid *should*, *could*, *may*, *might*, *shall*).
4. **Sentence Limits (Section 4, 5, 6)**:
   - **Procedural text**: Maximum **20 words** per sentence. One instruction per sentence (unless simultaneous).
   - **Descriptive text**: Maximum **25 words** per sentence. Maximum **6 sentences** per paragraph. Maximum **1 topic** per paragraph.
   - **No omitted words or contractions**: Always include articles (*the*, *a*, *an*) and demonstrative adjectives (*this*, *these*). Never use contractions (*don't*, *can't*).
5. **Procedural Writing (Section 5)**: Start procedural instructions with imperative (command) verbs. Place conditional clauses (*If...*, *When...*) **at the beginning** of the instruction.
6. **Safety Instructions (Section 7)**: Use signal words `WARNING` (risk of personal injury/death), `CAUTION` (risk of equipment damage), or `NOTE` (information only). Always state safety warnings **BEFORE** the step to which they apply.
7. **Punctuation & Word Count (Section 8)**: Standard English punctuation is permitted **EXCEPT the semicolon (;)**. Hyphenated words count as one word. Text in parentheses counts as one word in the sentence word count.
8. **Writing Practices (Section 9)**: Eliminate phrasal verbs (*carry out*, *put off*, *take off*). Rewrite using approved simple verbs (*do*, *delay*, *remove*).

---

## Directory Structure

```
ste100/
├── SKILL.md                               # Main Skill documentation & usage instructions
├── rules/                                 # Complete Part 1 rules (Sections 1–9)
│   ├── 01_words.md                        # Rules 1.1 – 1.14 (Dictionary, TNs, TVs, Spelling)
│   ├── 02_multi_word_nouns.md             # Rules 2.1 – 2.3 (Max 3-word noun clusters)
│   ├── 03_verbs.md                        # Rules 3.1 – 3.7 (Allowed tenses, active voice, -ing rules)
│   ├── 04_sentences.md                    # Rules 4.1 – 4.5 (Sentence length, no contractions/omissions)
│   ├── 05_procedural_writing.md           # Rules 5.1 – 5.5 (Max 20 words, imperative, condition first)
│   ├── 06_descriptive_writing.md          # Rules 6.1 – 6.6 (Max 25 words, max 6 sentences/paragraph)
│   ├── 07_safety_instructions.md          # Rules 7.1 – 7.3 (WARNING, CAUTION, NOTE formatting)
│   ├── 08_punctuation_and_word_count.md   # Rules 8.1 – 8.7 (No semicolons, word counting rules)
│   └── 09_writing_practices.md            # Rules 9.1 – 9.4 (No phrasal verbs, consistency)
├── references/                            # Lookup tables & dictionary references
│   ├── quick_reference.md                 # Summary cheat sheet
│   ├── approved_words_list.md             # List of approved STE words by part of speech
│   ├── unapproved_words_map.json          # Common unapproved words mapped to STE alternatives
│   ├── technical_categories.md            # Allowed Technical Noun & Technical Verb categories
│   └── dictionary.json                    # Complete 1,870+ term dictionary database
├── examples/                              # Practical rewrite examples
│   ├── procedural_examples.md             # Before / After procedural rewriting examples
│   ├── descriptive_examples.md            # Before / After descriptive rewriting examples
│   └── safety_examples.md                 # Correct WARNING / CAUTION / NOTE formats
└── scripts/                               # CLI scripts & Python validation tools
    ├── dictionary_lookup.py               # CLI tool to check words in the STE dictionary
    └── ste_checker.py                     # CLI tool to validate text against STE Issue 9 rules
```

---

## Skill Execution Workflows

### Workflow 1: Check & Validate Text against ASD-STE100
When requested to review or audit documentation for STE compliance:
1. Run the Python validation script:
   ```bash
   python3 scripts/ste_checker.py "Your technical text here"
   ```
2. Review rule violations:
   - Check sentence word counts (max 20 for procedure, max 25 for description).
   - Flag forbidden punctuation (semicolons `;`).
   - Flag contractions (*don't*, *it's*, *can't*).
   - Check for unapproved modal verbs (*should*, *could*, *might*, *may*, *shall*).
   - Check for gerunds ending in `-ing` that are not approved TNs/modifiers.
   - Look up words using `python3 scripts/dictionary_lookup.py <word>`.
3. Highlight non-compliant passages with exact rule references (e.g. `[Rule 3.6: Active voice required]`, `[Rule 5.1: Sentence exceeds 20 words]`).

### Workflow 2: Rewrite Technical Content into ASD-STE100
When asked to rewrite technical manuals or documentation into STE:
1. **Analyze Structure**: Separate procedural steps from descriptive explanations and safety warnings.
2. **Apply Vocabulary Restrictions**:
   - Replace unapproved words using [dictionary.json](file:///home/builder/Workspaces/makeMyOwnSkill/ste100/references/dictionary.json) or [unapproved_words_map.json](file:///home/builder/Workspaces/makeMyOwnSkill/ste100/references/unapproved_words_map.json).
   - Example: Change *utilize* -> *use*, *prior to* -> *before*, *ensure* -> *make sure*, *terminate* -> *stop*, *accomplish* -> *do* or *complete*.
3. **Format Procedures**:
   - Limit sentences to <= 20 words.
   - Use imperative mood: `Remove the cover.`, `Clean the filter.`
   - Place conditions first: `If the pressure is higher than 5 bar, open the relief valve.`
4. **Format Descriptive Text**:
   - Limit sentences to <= 25 words.
   - Limit paragraphs to <= 6 sentences, focusing on 1 clear topic per paragraph.
5. **Format Safety Warnings**:
   - Place `WARNING` or `CAUTION` **before** procedural steps.
   - Structure: Signal word + clear hazard statement + consequence/prevention command.

---

## Python Tools Reference

### Dictionary Lookup (`scripts/dictionary_lookup.py`)
```bash
python3 scripts/dictionary_lookup.py utilize
# Output:
# Word: utilize (v)
# Status: UNAPPROVED
# Approved Alternative: USE (v)
# STE Example: USE THE CORRECT TOOL TO REMOVE THE COVER.
```

### STE Rule Checker (`scripts/ste_checker.py`)
```bash
python3 scripts/ste_checker.py --file manual.txt --type procedure
# Output: Detailed report of word counts, unapproved words, verb forms, and passive voice.
```
