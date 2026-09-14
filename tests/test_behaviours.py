import unittest

from retrostudio.behaviour_editor import add_from_editor, editor_fields, editor_state, update_from_editor
from retrostudio.behaviours import (
    BEHAVIOUR_TYPES,
    BehaviourDefinition,
    add_behaviour,
    entity_behaviours,
    remove_behaviour,
)
from retrostudio.model import Entity


class BehaviourTests(unittest.TestCase):
    def test_baseline_behaviours_are_available(self):
        self.assertEqual(
            BEHAVIOUR_TYPES,
            (
                "PlatformerPlayer",
                "CameraFollow",
                "EnemyPatrol",
                "Collectible",
                "Door",
                "Projectile",
                "Dialogue",
            ),
        )

    def test_platformer_player_defaults_round_trip_through_component(self):
        entity = Entity("player", "Player")
        component = add_behaviour(entity, BehaviourDefinition("PlatformerPlayer"))
        self.assertEqual(component.type, "behaviour.PlatformerPlayer")
        self.assertEqual(component.data["speed"], 120)
        self.assertEqual(component.data["jump_speed"], 260)
        behaviours = entity_behaviours(entity)
        self.assertEqual(behaviours[0].behaviour_type, "PlatformerPlayer")
        self.assertEqual(behaviours[0].normalized_values()["gravity"], 700)

    def test_behaviour_values_can_be_customized(self):
        definition = BehaviourDefinition("EnemyPatrol", {"speed": 80, "axis": "y"})
        self.assertEqual(definition.validate(), [])
        values = definition.normalized_values()
        self.assertEqual(values["speed"], 80)
        self.assertEqual(values["axis"], "y")
        self.assertEqual(values["distance"], 96)

    def test_duplicate_behaviour_is_rejected(self):
        entity = Entity("door", "Door")
        add_behaviour(entity, BehaviourDefinition("Door"))
        with self.assertRaisesRegex(ValueError, "already has behaviour"):
            add_behaviour(entity, BehaviourDefinition("Door"))

    def test_invalid_behaviour_values_report_diagnostics(self):
        diagnostics = BehaviourDefinition("EnemyPatrol", {"axis": "diagonal"}).validate()
        self.assertEqual(diagnostics[0].code, "behaviour.axis_invalid")
        diagnostics = BehaviourDefinition("Projectile", {"lifetime_ms": 0}).validate()
        self.assertEqual(diagnostics[0].code, "behaviour.lifetime_invalid")
        diagnostics = BehaviourDefinition("Dialogue", {"text": "", "trigger": "interact"}).validate()
        self.assertEqual(diagnostics[0].code, "behaviour.dialogue_text_empty")

    def test_dialogue_defaults_and_trigger_validation(self):
        definition = BehaviourDefinition("Dialogue", {"speaker": "Guide", "text": "Welcome!"})
        self.assertEqual(definition.validate(), [])
        values = definition.normalized_values()
        self.assertEqual(values["speaker"], "Guide")
        self.assertEqual(values["trigger"], "interact")
        self.assertFalse(values["once"])
        diagnostics = BehaviourDefinition("Dialogue", {"text": "Hi", "trigger": "timer"}).validate()
        self.assertEqual(diagnostics[0].code, "behaviour.dialogue_trigger_invalid")

    def test_editor_schema_exposes_creator_fields(self):
        fields = editor_fields("Dialogue")
        self.assertEqual([field.key for field in fields], ["speaker", "text", "trigger", "once"])
        self.assertEqual(fields[1].field_type, "multiline")
        self.assertEqual(fields[2].choices, ("interact", "touch", "automatic"))

    def test_editor_add_and_update_round_trip(self):
        entity = Entity("npc", "NPC")
        add_from_editor(entity, "Dialogue")
        state = editor_state(entity)
        self.assertIn("Dialogue", state.available)
        self.assertEqual(state.attached[0].behaviour_type, "Dialogue")
        update_from_editor(
            entity,
            "Dialogue",
            {"speaker": "Captain", "text": "Ready?", "trigger": "touch", "once": "true"},
        )
        values = entity_behaviours(entity)[0].normalized_values()
        self.assertEqual(values["speaker"], "Captain")
        self.assertEqual(values["text"], "Ready?")
        self.assertEqual(values["trigger"], "touch")
        self.assertTrue(values["once"])

    def test_remove_behaviour(self):
        entity = Entity("coin", "Coin")
        add_behaviour(entity, BehaviourDefinition("Collectible"))
        self.assertTrue(remove_behaviour(entity, "Collectible"))
        self.assertEqual(entity_behaviours(entity), [])
        self.assertFalse(remove_behaviour(entity, "Collectible"))


if __name__ == "__main__":
    unittest.main()
