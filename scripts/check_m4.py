#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
desktop = (root / "retrostudio/desktop.py").read_text(encoding="utf-8")
creator = (root / "docs/CREATOR_FIRST.md").read_text(encoding="utf-8")
workspace = (root / "retrostudio/workspace.py").read_text(encoding="utf-8")

required = [
    "Asset Library",
    "Scene Composer",
    "Inspector",
    "Animation",
    "Target Preview",
    "Quality & Budget",
]

for label in required:
    assert label in desktop, f"missing desktop workspace: {label}"

assert "tkinter" in desktop, "native Linux shell toolkit missing"
assert "load_project" in desktop, "project opening not wired"
assert "Non-destructive sources" in creator, "creator source policy missing"
assert "CommandHistory" in workspace, "undo/redo model missing"
assert "CreatorGuidance" in workspace, "creator guidance model missing"

print("M4 STATIC: PASS")
print("  PASS: native desktop shell present")
print("  PASS: creator workspaces present")
print("  PASS: project open path wired")
print("  PASS: non-destructive source policy documented")
print("  PASS: guidance and undo/redo models present")
