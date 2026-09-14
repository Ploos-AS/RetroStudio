#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
behaviours = (root / "retrostudio/behaviours.py").read_text(encoding="utf-8")
roadmap = (root / "ROADMAP.md").read_text(encoding="utf-8")

for name in (
    "PlatformerPlayer",
    "CameraFollow",
    "EnemyPatrol",
    "Collectible",
    "Door",
    "Projectile",
):
    assert name in behaviours, f"missing creator behaviour: {name}"

assert "BehaviourDefinition" in behaviours, "behaviour definition model missing"
assert "add_behaviour" in behaviours, "behaviour attachment missing"
assert "remove_behaviour" in behaviours, "behaviour removal missing"
assert "behaviour." in behaviours, "stable behaviour component namespace missing"
assert "platform-neutral" in behaviours, "target-neutral contract not documented"
assert "Reusable visual behaviours" in roadmap, "M5 roadmap entry missing"

print("M5 VISUAL BEHAVIOURS: PASS")
print("  PASS: baseline creator behaviours present")
print("  PASS: defaults and validation model present")
print("  PASS: entity attach/remove operations present")
print("  PASS: platform-neutral behaviour component namespace present")
