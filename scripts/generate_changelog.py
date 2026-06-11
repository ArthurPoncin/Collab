#!/usr/bin/env python3
"""Génération automatique du CHANGELOG.md depuis l'historique git.

Parse les messages de commit au format Conventional Commits
(feat, fix, perf, refactor...) entre chaque tag de version et produit
un CHANGELOG.md au format Keep a Changelog.

Usage :
    python scripts/generate_changelog.py                  # versions taguées
    python scripts/generate_changelog.py --version 2.2.0  # inclut les commits
                                                          # non tagués sous 2.2.0

Auteur : Arthur Poncin
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date

# Mapping type de commit -> section Keep a Changelog
SECTIONS = {
    "feat": "Ajouté",
    "fix": "Corrigé",
    "perf": "Modifié",
    "refactor": "Modifié",
    "revert": "Supprimé",
}

# Types ignorés dans le changelog (maintenance interne)
IGNORED = {"docs", "test", "chore", "style", "ci", "build"}

COMMIT_RE = re.compile(
    r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<desc>.+)$"
)

HEADER = """# Changelog

Historique des versions, généré par scripts/generate_changelog.py
à partir des messages de commit.
"""


def git(*args: str) -> str:
    """Exécute une commande git et renvoie sa sortie."""
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def get_tags() -> list[str]:
    """Tags de version triés du plus récent au plus ancien."""
    out = git("tag", "--list", "v*", "--sort=-v:refname")
    return out.splitlines() if out else []


def get_commits(rev_range: str) -> list[dict]:
    """Commits parsés (type, scope, description, breaking) d'un intervalle."""
    out = git("log", rev_range, "--pretty=format:%s%x00%b%x01")
    commits = []
    for entry in out.split("\x01"):
        entry = entry.strip()
        if not entry:
            continue
        subject, _, body = entry.partition("\x00")
        match = COMMIT_RE.match(subject.strip())
        if not match:
            continue
        commits.append(
            {
                "type": match.group("type"),
                "scope": match.group("scope"),
                "desc": match.group("desc").strip(),
                "breaking": bool(match.group("breaking"))
                or "BREAKING CHANGE:" in body,
            }
        )
    return commits


def tag_date(tag: str) -> str:
    """Date (YYYY-MM-DD) d'un tag."""
    return git("log", "-1", "--format=%ad", "--date=short", tag)


def render_version(title: str, day: str, commits: list[dict]) -> str:
    """Bloc markdown d'une version."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for c in commits:
        if c["type"] in IGNORED:
            continue
        section = SECTIONS.get(c["type"])
        if section is None:
            continue
        prefix = "**BREAKING** : " if c["breaking"] else ""
        scope = f"{c['scope']} : " if c["scope"] else ""
        grouped[section].append(f"- {prefix}{scope}{c['desc']}")

    if not grouped:
        return ""

    lines = [f"## [{title}] - {day}", ""]
    for section in ("Ajouté", "Modifié", "Corrigé", "Supprimé"):
        if section in grouped:
            lines.append(f"### {section}")
            lines.append("")
            lines.extend(grouped[section])
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        help="Version à attribuer aux commits non encore tagués (ex: 2.2.0)",
    )
    parser.add_argument(
        "--output", default="CHANGELOG.md", help="Fichier de sortie"
    )
    args = parser.parse_args()

    tags = get_tags()
    blocks = []

    # Commits non tagués (version en préparation)
    if args.version:
        rev = f"{tags[0]}..HEAD" if tags else "HEAD"
        pending = get_commits(rev)
        block = render_version(args.version, date.today().isoformat(), pending)
        if block:
            blocks.append(block)

    # Une section par tag existant
    for i, tag in enumerate(tags):
        prev = tags[i + 1] if i + 1 < len(tags) else None
        rev = f"{prev}..{tag}" if prev else tag
        version = tag.lstrip("v")
        block = render_version(version, tag_date(tag), get_commits(rev))
        if block:
            blocks.append(block)

    content = HEADER + "\n" + "\n".join(blocks)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"{args.output} généré ({len(blocks)} version(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
