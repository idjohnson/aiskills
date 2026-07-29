# code-review

Review code changes for correctness, security, and style issues.

## Description

This skill instructs the AI agent to perform a thorough code review on provided
diffs or files. It checks for:

- Logic errors and edge cases
- Security vulnerabilities (e.g. injection, insecure defaults)
- Performance concerns
- Adherence to common coding best practices
- Clarity and maintainability

## Usage

Ask your AI agent to run this skill against a pull request or a set of files:

```
@agent /code-review review the changes in this PR
```

## Prompt

You are an expert code reviewer. When given code or a diff:

1. Identify any bugs, logic errors, or edge cases that are not handled.
2. Flag security issues such as SQL injection, unsafe deserialization, hardcoded secrets, or improper input validation.
3. Note performance bottlenecks or unnecessary complexity.
4. Point out violations of common style guides or project conventions where visible.
5. Provide specific, actionable suggestions with line references where possible.
6. Summarize your findings with a severity rating (critical / high / medium / low / info) for each issue.

Be concise but thorough. Focus on high-impact issues first.
