#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required = [
    "README.md",
    "ROADMAP.md",
    "LICENSE",
    "docs/ARCHITECTURE.md",
    "schemas/project.schema.json",
    "include/retrostudio/target.h",
    "examples/minimal/project.json",
    "examples/minimal/scenes/main.scene.json",
]

for rel in required:
    if not (ROOT / rel).is_file():
        errors.append(f"missing required file: {rel}")

try:
    project = json.loads((ROOT / "examples/minimal/project.json").read_text())
except Exception as exc:
    errors.append(f"cannot parse minimal project: {exc}")
    project = {}

if project.get("format_version") != 1:
    errors.append("minimal project format_version must be 1")
if not project.get("name"):
    errors.append("minimal project must have a name")
if not project.get("project_id"):
    errors.append("minimal project must have a project_id")
if not isinstance(project.get("scenes"), list):
    errors.append("minimal project scenes must be an array")
if not isinstance(project.get("assets"), list):
    errors.append("minimal project assets must be an array")

for scene in project.get("scenes", []):
    if not (ROOT / "examples/minimal" / scene).is_file():
        errors.append(f"referenced scene does not exist: {scene}")

architecture = (ROOT / "docs/ARCHITECTURE.md").read_text() if (ROOT / "docs/ARCHITECTURE.md").exists() else ""
if "RetroStudio must never depend on a product frontend/backend" not in architecture:
    errors.append("architecture dependency rule is missing")

header = (ROOT / "include/retrostudio/target.h").read_text() if (ROOT / "include/retrostudio/target.h").exists() else ""
if "RETROSTUDIO_TARGET_API_VERSION 1u" not in header:
    errors.append("target API version marker is missing")

if errors:
    print("M0 CHECK: FAIL")
    for error in errors:
        print(f"  FAIL: {error}")
    sys.exit(1)

print("M0 CHECK: PASS")
print("  PASS: repository foundation present")
print("  PASS: minimal project parses")
print("  PASS: scene references resolve")
print("  PASS: target API boundary versioned")
print("  PASS: platform dependency rule documented")
