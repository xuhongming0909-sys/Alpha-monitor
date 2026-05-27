#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent


DEFAULT_VALIDATIONS = [
    "npm run check",
    "npm run check:boundaries",
]

SCOPE_RULES = {
    "presentation": {
        "allow": ["presentation/"],
        "avoid": ["data_fetch/", "strategy/", "notification/", "shared/"],
    },
    "data_fetch": {
        "allow": ["data_fetch/"],
        "avoid": ["strategy/", "presentation/", "notification/", "shared/"],
    },
    "strategy": {
        "allow": ["strategy/"],
        "avoid": ["data_fetch/", "presentation/", "notification/", "shared/"],
    },
    "notification": {
        "allow": ["notification/"],
        "avoid": ["data_fetch/", "strategy/", "presentation/", "shared/"],
    },
    "shared": {
        "allow": ["shared/"],
        "avoid": ["data_fetch/", "strategy/", "presentation/", "notification/"],
    },
    "docs": {
        "allow": [
            "docs/",
            "specs/",
            "missions/",
            "CLAUDE.md",
            "INDEX.md",
        ],
        "avoid": [
            "data_fetch/",
            "strategy/",
            "presentation/",
            "notification/",
            "shared/",
        ],
    },
    "full_repo": {
        "allow": ["the smallest necessary set of files in the repository"],
        "avoid": [],
    },
}


def build_scope_text(scope: str) -> str:
    rule = SCOPE_RULES[scope]
    lines = ["Scope:"]
    lines.append("- Allowed edit area: " + ", ".join(rule["allow"]))
    if rule["avoid"]:
        lines.append(
            "- Do not modify these areas unless the task cannot be completed without "
            "approved contract/doc changes: " + ", ".join(rule["avoid"])
        )
    else:
        lines.append(
            "- Keep edits minimal and avoid cross-cutting changes unless the task "
            "explicitly requires them."
        )
    return "\n".join(lines)


def build_validation_text(validations: list[str]) -> str:
    return "Validation:\n" + "\n".join(f"- {command}" for command in validations)


def render_prompt(
    task: str,
    scope: str,
    validations: list[str],
    extra_rules: list[str],
) -> str:
    sections = [
        "Read CLAUDE.md and INDEX.md first.",
        dedent(
            """
            Repository workflow:
            - Read order: CLAUDE.md → INDEX.md → README.md → specs/spec.md → relevant specs/*.md → config/config.yaml → MEMORY.md
            - If behavior, config, API meaning, deployment behavior, or contract meaning changes, stop coding first and update:
              - specs/*.md (affected module specs)
              - specs/spec.md (project index)
            - Respect repository layering:
              - data_fetch/: fetch and normalize only
              - strategy/: business calculation and rule judgment only
              - presentation/: routes, view models, page rendering, and display logic only
              - notification/: push config and delivery only
              - shared/: reusable cross-domain support only
            - Never invent fake data.
            - Prefer the shortest clear change path and keep edits minimal.
            """
        ).strip(),
        build_scope_text(scope),
    ]

    if extra_rules:
        sections.append(
            "Extra rules:\n" + "\n".join(f"- {rule}" for rule in extra_rules)
        )

    sections.append("Task:\n- " + task.strip())
    sections.append(build_validation_text(validations))
    sections.append(
        dedent(
            """
            Deliverable:
            - Implement the change if it is inside the approved scope.
            - If contracts must change first, stop and say exactly which docs need updates before coding.
            - Summarize changed files and validation results at the end.
            """
        ).strip()
    )

    return "\n\n".join(sections).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an Alpha Monitor-specific task prompt for mini-SWE-agent."
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Concrete task description to send to mini-SWE-agent.",
    )
    parser.add_argument(
        "--scope",
        choices=sorted(SCOPE_RULES.keys()),
        default="full_repo",
        help="Narrow the allowed edit area.",
    )
    parser.add_argument(
        "--validate",
        action="append",
        default=[],
        help="Append a validation command. May be provided multiple times.",
    )
    parser.add_argument(
        "--extra-rule",
        action="append",
        default=[],
        help="Append an extra repository/task rule. May be provided multiple times.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the generated task text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validations = DEFAULT_VALIDATIONS + args.validate
    prompt = render_prompt(
        task=args.task,
        scope=args.scope,
        validations=validations,
        extra_rules=args.extra_rule,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(prompt, encoding="utf-8")
    else:
        print(prompt, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
