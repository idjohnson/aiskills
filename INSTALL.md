# Installing AI Skills

This document explains how to install the skills from this repository onto your
local machine so that AI agents can discover and use them.

## Prerequisites

- **Bash 4+** (macOS ships Bash 3; install a newer version via Homebrew: `brew install bash`)
- A Unix-like operating system (Linux, macOS, WSL)

## Default install location

Skills are installed to:

```
$HOME/.agents/skills/<skill name>/
```

For example, the `code-review` skill is installed to:

```
~/.agents/skills/code-review/
```

## Quick install

### Install all skills

Clone this repository and run the install script from the repository root:

```bash
git clone https://github.com/idjohnson/aiskills.git
cd aiskills
./install.sh
```

### Install a specific skill

Pass one or more skill names as arguments:

```bash
./install.sh code-review
./install.sh code-review summarize-pr
```

## What the install script does

1. Locates skills in the `./skills/` directory of this repository.
2. Creates `$HOME/.agents/skills/` if it does not already exist.
3. Copies each skill directory to `$HOME/.agents/skills/<skill name>/`.
4. If a skill is already installed, the existing directory is renamed to
   `<skill name>.bak.<timestamp>` before the new version is copied in.

## Uninstalling a skill

Remove the skill's directory from the install location:

```bash
rm -rf ~/.agents/skills/code-review
```

## Available skills

| Skill | Description |
|-------|-------------|
| [code-review](skills/code-review/skill.md) | Review code changes for correctness, security, and style issues |
| [summarize-pr](skills/summarize-pr/skill.md) | Summarize a pull request into a concise, human-readable description |

## Adding your own skills

1. Create a new directory under `skills/<your-skill-name>/`.
2. Add a `skill.md` file describing the skill and the prompt it uses.
3. Optionally add a `skill.yaml` metadata file (name, version, description, tags).
4. Run `./install.sh <your-skill-name>` to install it.

See [skills/code-review/](skills/code-review/) for a reference example.
