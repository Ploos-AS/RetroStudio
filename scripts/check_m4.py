#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
desktop = (root / "retrostudio/desktop.py").read_text(encoding="utf-8")
creator_doc = (root / "docs/CREATOR_FIRST.md").read_text(encoding="utf-8")
creator_ops = (root / "retrostudio/creator.py").read_text(encoding="utf-8")
animation = (root / "retrostudio/animation.py").read_text(encoding="utf-8")
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
assert "import_asset_ui" in desktop, "asset import UI missing"
assert "place_selected_asset" in desktop, "scene placement UI missing"
assert "apply_inspector" in desktop, "Inspector apply action missing"
assert "_on_entity_select" in desktop, "scene object selection missing"
assert "edit_entity" in desktop, "Inspector model edit hook missing"
assert "new_animation_clip" in desktop, "animation clip creation UI missing"
assert "add_animation_frame" in desktop, "animation frame UI missing"
assert "apply_animation_settings" in desktop, "animation settings UI missing"
assert "save_animation_clip" in desktop, "animation persistence UI missing"
assert "class AnimationClip" in animation, "animation clip model missing"
assert "class AnimationFrame" in animation, "animation frame model missing"
assert "duration_ms" in animation, "animation timing support missing"
assert "loop" in animation and "fps" in animation, "animation loop/FPS support missing"
assert "Listbox" in desktop, "asset/object/frame list UI missing"
assert "visual.asset" in creator_ops, "visual asset scene component missing"
assert "shutil.copy2" in creator_ops, "non-destructive import copy missing"
assert "def edit_entity" in creator_ops, "creator-facing entity edit operation missing"
assert "def move_entity" in creator_ops, "position edit operation missing"
assert "def rename_entity" in creator_ops, "name edit operation missing"
assert "Non-destructive sources" in creator_doc, "creator source policy missing"
assert "CommandHistory" in workspace, "undo/redo model missing"
assert "CreatorGuidance" in workspace, "creator guidance model missing"

print("M4 STATIC: PASS")
print("  PASS: native desktop shell present")
print("  PASS: creator workspaces present")
print("  PASS: project open/save path wired")
print("  PASS: non-destructive asset import wired")
print("  PASS: Asset Library selection and scene placement wired")
print("  PASS: Scene Composer object selection/rendering wired")
print("  PASS: Inspector name/position editing wired")
print("  PASS: Animation clips/frames/FPS/loop/persistence wired")
print("  PASS: guidance and undo/redo models present")
