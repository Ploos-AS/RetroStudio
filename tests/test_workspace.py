import unittest

from retrostudio.model import Diagnostic, Project
from retrostudio.workspace import (
    CommandHistory,
    CreatorGuidance,
    SetTargetCommand,
    WorkspaceState,
)


def project():
    return Project("Creator Demo", "creator-demo", "", [])


class WorkspaceTests(unittest.TestCase):
    def test_creator_workspaces_and_selection(self):
        state = WorkspaceState(project())
        state.activate("assets")
        state.select("asset", "hero-sprite")
        self.assertEqual(state.active_workspace, "assets")
        self.assertEqual(state.selection.item_id, "hero-sprite")
        with self.assertRaises(ValueError):
            state.activate("engine-internals")

    def test_feedback_keeps_raw_diagnostic_and_creator_guidance(self):
        state = WorkspaceState(project())
        diagnostic = Diagnostic("warning", "palette.limit", "palette exceeds target", "hero.png")
        guidance = CreatorGuidance(
            "palette.limit",
            "Hero artwork uses more colors than this target can display here.",
            ("Try a target-aware palette preview.", "Reserve colors for the hero before background conversion."),
        )
        state.set_feedback([diagnostic], [guidance])
        self.assertEqual(state.diagnostics[0].code, "palette.limit")
        self.assertEqual(state.guidance[0].diagnostic_code, "palette.limit")
        self.assertEqual(len(state.guidance[0].suggestions), 2)

    def test_target_change_is_undoable_and_redoable(self):
        state = WorkspaceState(project(), target="amiga-a500-ocs")
        history = CommandHistory()
        history.execute(SetTargetCommand("atari-ste"), state)
        self.assertEqual(state.target, "atari-ste")
        self.assertTrue(history.undo(state))
        self.assertEqual(state.target, "amiga-a500-ocs")
        self.assertTrue(history.redo(state))
        self.assertEqual(state.target, "atari-ste")

    def test_new_command_clears_redo_history(self):
        state = WorkspaceState(project(), target="a")
        history = CommandHistory()
        history.execute(SetTargetCommand("b"), state)
        history.undo(state)
        history.execute(SetTargetCommand("c"), state)
        self.assertFalse(history.redo(state))
        self.assertEqual(state.target, "c")


if __name__ == "__main__":
    unittest.main()
