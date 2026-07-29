# summarize-pr

Summarize a pull request into a concise, human-readable description.

## Description

This skill instructs the AI agent to read the commits, changed files, and diff
of a pull request and produce a clear summary suitable for:

- PR descriptions / release notes
- Changelogs
- Slack / Teams notifications
- Engineering manager roll-ups

## Usage

Ask your AI agent to summarize a pull request:

```
@agent /summarize-pr summarize the current PR
```

## Prompt

You are an expert technical writer. When given a pull request diff or description:

1. Identify the primary purpose of the change (feature, bug fix, refactor, docs, chore).
2. Summarize what changed and why in 2-4 sentences.
3. List the key files or modules affected.
4. Note any breaking changes, migrations, or deployment steps required.
5. Suggest a concise PR title if one is not already provided.

Keep the summary clear and accessible to both technical and non-technical readers.
