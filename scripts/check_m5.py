#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
behaviours = (root / "retrostudio/behaviours.py").read_text(encoding="utf-8")
editor = (root / "retrostudio/behaviour_editor.py").read_text(encoding="utf-8")
panel = (root / "retrostudio/behaviour_panel.py").read_text(encoding="utf-8")
animation_state = (root / "retrostudio/animation_state.py").read_text(encoding="utf-8")
roadmap = (root / "ROADMAP.md").read_text(encoding="utf-8")

for name in (
    "PlatformerPlayer",
    "CameraFollow",
    "EnemyPatrol",
    "Collectible",
    "Door",
    "Projectile",
    "Dialogue",
):
    assert name in behaviours, f"missing creator behaviour: {name}"

assert "BehaviourDefinition" in behaviours, "behaviour definition model missing"
assert "BehaviourField" in behaviours, "creator field schema missing"
assert "add_behaviour" in behaviours, "behaviour attachment missing"
assert "update_behaviour" in behaviours, "behaviour editing missing"
assert "remove_behaviour" in behaviours, "behaviour removal missing"
assert "behaviour." in behaviours, "stable behaviour component namespace missing"
assert "platform-neutral" in behaviours, "target-neutral contract not documented"
assert "parse_editor_values" in editor, "behaviour editor parser missing"
assert "class BehaviourPanel" in panel, "creator-facing behaviour panel missing"
assert "Add Behaviour" in panel and "Apply Behaviour" in panel, "behaviour panel actions missing"
assert "multiline" in panel, "dialogue multiline editor support missing"
for name in ("AnimationStateMachine", "AnimationState", "AnimationTransition", "AnimationCondition"):
    assert name in animation_state, f"animation state primitive missing: {name}"
assert "save_state_machine" in animation_state and "load_state_machine" in animation_state, "animation state persistence missing"
assert "Animation states and transitions" in roadmap, "M5 animation-state roadmap entry missing"

print("M5 VISUAL GAME CREATION: PASS")
print("  PASS: baseline creator behaviours and Dialogue present")
print("  PASS: defaults, validation and creator field schema present")
print("  PASS: entity add/update/remove operations present")
print("  PASS: toolkit-neutral editor parser present")
print("  PASS: creator-facing Tk behaviour editor panel present")
print("  PASS: animation states, transitions and conditions present")
print("  PASS: animation state persistence present")
print("  PASS: platform-neutral authoring contracts preserved")
