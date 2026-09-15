"""Creator-facing animation states and transitions.

The state machine is platform-neutral authoring data. States reference animation
clip IDs; target backends decide how to implement playback at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path


CONDITION_OPERATORS = ("==", "!=", ">", ">=", "<", "<=")


@dataclass(frozen=True)
class AnimationCondition:
    parameter: str
    operator: str
    value: bool | int | float | str

    def validate(self) -> None:
        if not self.parameter.strip():
            raise ValueError("transition condition parameter must not be empty")
        if self.operator not in CONDITION_OPERATORS:
            raise ValueError(f"unsupported transition operator: {self.operator}")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return {"parameter": self.parameter, "operator": self.operator, "value": self.value}

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AnimationCondition":
        condition = cls(str(raw["parameter"]), str(raw.get("operator", "==")), raw.get("value", True))
        condition.validate()
        return condition


@dataclass(frozen=True)
class AnimationState:
    state_id: str
    clip_id: str
    name: str = ""

    def validate(self) -> None:
        if not self.state_id.strip():
            raise ValueError("animation state_id must not be empty")
        if not self.clip_id.strip():
            raise ValueError("animation state clip_id must not be empty")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return {"state_id": self.state_id, "clip_id": self.clip_id, "name": self.name or self.state_id}

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AnimationState":
        state = cls(str(raw["state_id"]), str(raw["clip_id"]), str(raw.get("name", "")))
        state.validate()
        return state


@dataclass(frozen=True)
class AnimationTransition:
    source: str
    target: str
    conditions: tuple[AnimationCondition, ...] = ()
    exit_time: float | None = None

    def validate(self) -> None:
        if not self.source.strip() or not self.target.strip():
            raise ValueError("transition source and target must not be empty")
        if self.source == self.target:
            raise ValueError("transition source and target must differ")
        if self.exit_time is not None and not 0.0 <= self.exit_time <= 1.0:
            raise ValueError("transition exit_time must be between 0 and 1")
        for condition in self.conditions:
            condition.validate()

    def to_dict(self) -> dict[str, object]:
        self.validate()
        raw: dict[str, object] = {
            "source": self.source,
            "target": self.target,
            "conditions": [condition.to_dict() for condition in self.conditions],
        }
        if self.exit_time is not None:
            raw["exit_time"] = self.exit_time
        return raw

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AnimationTransition":
        transition = cls(
            source=str(raw["source"]),
            target=str(raw["target"]),
            conditions=tuple(AnimationCondition.from_dict(item) for item in raw.get("conditions", [])),
            exit_time=None if raw.get("exit_time") is None else float(raw["exit_time"]),
        )
        transition.validate()
        return transition


@dataclass
class AnimationStateMachine:
    machine_id: str
    name: str
    initial_state: str
    states: list[AnimationState] = field(default_factory=list)
    transitions: list[AnimationTransition] = field(default_factory=list)

    def validate(self) -> None:
        if not self.machine_id.strip():
            raise ValueError("animation machine_id must not be empty")
        ids = [state.state_id for state in self.states]
        if len(ids) != len(set(ids)):
            raise ValueError("animation state IDs must be unique")
        for state in self.states:
            state.validate()
        if self.states and self.initial_state not in set(ids):
            raise ValueError("initial_state must reference an existing state")
        if not self.states and self.initial_state:
            raise ValueError("empty state machine must not define initial_state")
        known = set(ids)
        for transition in self.transitions:
            transition.validate()
            if transition.source not in known or transition.target not in known:
                raise ValueError("transition must reference existing states")

    def add_state(self, state_id: str, clip_id: str, name: str = "") -> AnimationState:
        candidate = AnimationState(state_id, clip_id, name)
        candidate.validate()
        if any(state.state_id == state_id for state in self.states):
            raise ValueError(f"duplicate animation state: {state_id}")
        self.states.append(candidate)
        if not self.initial_state:
            self.initial_state = state_id
        return candidate

    def add_transition(
        self,
        source: str,
        target: str,
        conditions: tuple[AnimationCondition, ...] = (),
        exit_time: float | None = None,
    ) -> AnimationTransition:
        transition = AnimationTransition(source, target, conditions, exit_time)
        transition.validate()
        known = {state.state_id for state in self.states}
        if source not in known or target not in known:
            raise ValueError("transition must reference existing states")
        self.transitions.append(transition)
        return transition

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "format_version": 1,
            "machine_id": self.machine_id,
            "name": self.name,
            "initial_state": self.initial_state,
            "states": [state.to_dict() for state in self.states],
            "transitions": [transition.to_dict() for transition in self.transitions],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AnimationStateMachine":
        if raw.get("format_version") != 1:
            raise ValueError("unsupported animation state format_version")
        machine = cls(
            machine_id=str(raw["machine_id"]),
            name=str(raw.get("name", raw["machine_id"])),
            initial_state=str(raw.get("initial_state", "")),
            states=[AnimationState.from_dict(item) for item in raw.get("states", [])],
            transitions=[AnimationTransition.from_dict(item) for item in raw.get("transitions", [])],
        )
        machine.validate()
        return machine


def save_state_machine(machine: AnimationStateMachine, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(machine.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_state_machine(path: str | Path) -> AnimationStateMachine:
    return AnimationStateMachine.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
