import tempfile
import unittest
from pathlib import Path

from retrostudio.animation_state import (
    AnimationCondition,
    AnimationStateMachine,
    load_state_machine,
    save_state_machine,
)


class AnimationStateTests(unittest.TestCase):
    def test_first_state_becomes_initial(self):
        machine = AnimationStateMachine("player", "Player", "")
        machine.add_state("idle", "idle")
        self.assertEqual(machine.initial_state, "idle")

    def test_creator_states_reference_animation_clips(self):
        machine = AnimationStateMachine("player", "Player", "")
        idle = machine.add_state("idle", "player-idle", "Idle")
        run = machine.add_state("run", "player-run", "Run")
        self.assertEqual(idle.clip_id, "player-idle")
        self.assertEqual(run.clip_id, "player-run")

    def test_transition_conditions_are_platform_neutral(self):
        machine = AnimationStateMachine("player", "Player", "")
        machine.add_state("idle", "idle")
        machine.add_state("run", "run")
        transition = machine.add_transition(
            "idle", "run", (AnimationCondition("speed", ">", 0),)
        )
        self.assertEqual(transition.conditions[0].parameter, "speed")
        self.assertEqual(transition.conditions[0].operator, ">")

    def test_transition_rejects_unknown_state(self):
        machine = AnimationStateMachine("player", "Player", "")
        machine.add_state("idle", "idle")
        with self.assertRaisesRegex(ValueError, "existing states"):
            machine.add_transition("idle", "run")

    def test_exit_time_is_normalized_fraction(self):
        machine = AnimationStateMachine("player", "Player", "")
        machine.add_state("idle", "idle")
        machine.add_state("run", "run")
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            machine.add_transition("idle", "run", exit_time=1.5)

    def test_duplicate_state_is_rejected_without_mutation(self):
        machine = AnimationStateMachine("player", "Player", "")
        machine.add_state("idle", "idle")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            machine.add_state("idle", "other")
        self.assertEqual(len(machine.states), 1)

    def test_json_round_trip(self):
        machine = AnimationStateMachine("player", "Player", "")
        machine.add_state("idle", "player-idle", "Idle")
        machine.add_state("run", "player-run", "Run")
        machine.add_transition("idle", "run", (AnimationCondition("moving", "==", True),), 0.8)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "player.states.json"
            save_state_machine(machine, path)
            loaded = load_state_machine(path)
        self.assertEqual(loaded.machine_id, "player")
        self.assertEqual(loaded.initial_state, "idle")
        self.assertEqual([state.state_id for state in loaded.states], ["idle", "run"])
        self.assertEqual(loaded.transitions[0].conditions[0].value, True)
        self.assertEqual(loaded.transitions[0].exit_time, 0.8)


if __name__ == "__main__":
    unittest.main()
