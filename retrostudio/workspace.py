"""Creator-first editor workspace model.

This module intentionally contains no GUI toolkit code. It defines stable editor
state and commands so a native Linux frontend can be thin and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .model import Diagnostic, Project


WORKSPACES = (
    "project",
    "assets",
    "scene",
    "event_graph",
    "inspector",
    "animation",
    "target_preview",
    "quality",
)


@dataclass(frozen=True)
class Selection:
    kind: str
    item_id: str


@dataclass(frozen=True)
class CreatorGuidance:
    diagnostic_code: str
    summary: str
    suggestions: tuple[str, ...] = ()


@dataclass
class WorkspaceState:
    project: Project
    active_workspace: str = "scene"
    selection: Selection | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)
    guidance: list[CreatorGuidance] = field(default_factory=list)
    target: str = ""

    def activate(self, workspace: str) -> None:
        if workspace not in WORKSPACES:
            raise ValueError(f"unknown workspace: {workspace}")
        self.active_workspace = workspace

    def select(self, kind: str, item_id: str) -> None:
        self.selection = Selection(kind, item_id)

    def clear_selection(self) -> None:
        self.selection = None

    def set_feedback(self, diagnostics: list[Diagnostic], guidance: list[CreatorGuidance] | None = None) -> None:
        self.diagnostics = list(diagnostics)
        self.guidance = list(guidance or [])


class EditorCommand(Protocol):
    label: str

    def apply(self, state: WorkspaceState) -> Any: ...

    def undo(self, state: WorkspaceState, token: Any) -> None: ...


@dataclass
class CommandHistory:
    undo_stack: list[tuple[EditorCommand, Any]] = field(default_factory=list)
    redo_stack: list[tuple[EditorCommand, Any]] = field(default_factory=list)

    def execute(self, command: EditorCommand, state: WorkspaceState) -> None:
        token = command.apply(state)
        self.undo_stack.append((command, token))
        self.redo_stack.clear()

    def undo(self, state: WorkspaceState) -> bool:
        if not self.undo_stack:
            return False
        command, token = self.undo_stack.pop()
        command.undo(state, token)
        self.redo_stack.append((command, token))
        return True

    def redo(self, state: WorkspaceState) -> bool:
        if not self.redo_stack:
            return False
        command, _old_token = self.redo_stack.pop()
        token = command.apply(state)
        self.undo_stack.append((command, token))
        return True


@dataclass
class SetTargetCommand:
    target: str
    label: str = "Change target"

    def apply(self, state: WorkspaceState) -> str:
        previous = state.target
        state.target = self.target
        return previous

    def undo(self, state: WorkspaceState, token: str) -> None:
        state.target = token
