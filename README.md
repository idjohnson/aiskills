# aiskills

A collection of reusable AI agent skills.  Each skill lives in its own
directory under `skills/` and can be installed to
`$HOME/.agents/skills/<skill name>` with a single command.

## Skills

| Skill | Description |
|-------|-------------|
| [code-review](skills/code-review/skill.md) | Review code changes for correctness, security, and style issues |
| [summarize-pr](skills/summarize-pr/skill.md) | Summarize a pull request into a concise, human-readable description |

## Quick start

```bash
# Clone the repository
git clone https://github.com/idjohnson/aiskills.git
cd aiskills

# Install all skills
./install.sh

# Or install a specific skill
./install.sh code-review
```

Skills are copied to `$HOME/.agents/skills/<skill name>/`.

## Directory structure

```
aiskills/
├── install.sh            # Installer script
├── INSTALL.md            # Detailed installation instructions
├── README.md             # This file
└── skills/
    ├── code-review/
    │   ├── skill.md      # Skill description and prompt
    │   └── skill.yaml    # Metadata (name, version, tags)
    └── summarize-pr/
        ├── skill.md
        └── skill.yaml
```

## Adding a new skill

1. Create a directory: `skills/<your-skill-name>/`
2. Add `skill.md` — describe the skill and the prompt it uses.
3. Add `skill.yaml` — provide metadata (name, version, description, tags).
4. Run `./install.sh <your-skill-name>` to install it.

See [INSTALL.md](INSTALL.md) for full installation documentation.

## License

[MIT](LICENSE)
