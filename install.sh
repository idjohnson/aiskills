#!/usr/bin/env bash
# install.sh — Install AI skills from this repository to $HOME/.agents/skills/
#
# Usage:
#   ./install.sh              # Install all skills
#   ./install.sh <skill>...   # Install specific skill(s) by name
#
# Each skill in ./skills/<skill name>/ is copied to $HOME/.agents/skills/<skill name>/.
# Existing skill directories are backed up before being overwritten.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="${SCRIPT_DIR}/skills"
SKILLS_DEST="${HOME}/.agents/skills"

# ── helpers ──────────────────────────────────────────────────────────────────

info()    { printf '\033[1;34m[info]\033[0m  %s\n' "$*"; }
success() { printf '\033[1;32m[ok]\033[0m    %s\n' "$*"; }
warn()    { printf '\033[1;33m[warn]\033[0m  %s\n' "$*"; }
error()   { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; }

# ── validation ───────────────────────────────────────────────────────────────

if [[ ! -d "${SKILLS_SRC}" ]]; then
  error "Skills source directory not found: ${SKILLS_SRC}"
  exit 1
fi

# ── skill installer ──────────────────────────────────────────────────────────

install_skill() {
  local skill_name="$1"
  local src="${SKILLS_SRC}/${skill_name}"
  local dest="${SKILLS_DEST}/${skill_name}"

  if [[ ! -d "${src}" ]]; then
    error "Skill not found: ${skill_name}"
    return 1
  fi

  # Back up an existing installation before overwriting
  if [[ -d "${dest}" ]]; then
    local backup="${dest}.bak.$(date +%Y%m%d%H%M%S)"
    warn "Backing up existing '${skill_name}' to ${backup}"
    mv "${dest}" "${backup}"
  fi

  mkdir -p "${SKILLS_DEST}"
  cp -r "${src}" "${dest}"
  success "Installed '${skill_name}' → ${dest}"
}

# ── main ─────────────────────────────────────────────────────────────────────

if [[ $# -eq 0 ]]; then
  # Install all skills found in the skills directory
  mapfile -t skills < <(find "${SKILLS_SRC}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)

  if [[ ${#skills[@]} -eq 0 ]]; then
    warn "No skills found in ${SKILLS_SRC}"
    exit 0
  fi

  info "Installing ${#skills[@]} skill(s) to ${SKILLS_DEST} ..."
  for skill in "${skills[@]}"; do
    install_skill "${skill}"
  done
else
  # Install only the requested skill(s)
  info "Installing ${#}  skill(s) to ${SKILLS_DEST} ..."
  for skill in "$@"; do
    install_skill "${skill}"
  done
fi

info "Done."
