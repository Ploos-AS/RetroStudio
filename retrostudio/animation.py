"""Creator-facing animation model.

Animation clips reference non-destructive project assets. Timing is expressed as a
clip FPS with optional per-frame millisecond overrides so creators can start simple
and refine timing only when needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class AnimationFrame:
    asset: str
    duration_ms: int | None = None

    def effective_duration_ms(self, fps: float) -> int:
        if self.duration_ms is not None:
            return self.duration_ms
        if fps <= 0:
            raise ValueError("fps must be greater than zero")
        return max(1, round(1000.0 / fps))

    def to_dict(self) -> dict[str, object]:
        raw: dict[str, object] = {"asset": self.asset}
        if self.duration_ms is not None:
            raw["duration_ms"] = self.duration_ms
        return raw

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AnimationFrame":
        duration = raw.get("duration_ms")
        return cls(str(raw["asset"]), None if duration is None else int(duration))


@dataclass
class AnimationClip:
    clip_id: str
    name: str
    fps: float = 12.0
    loop: bool = True
    frames: list[AnimationFrame] = field(default_factory=list)

    def validate(self) -> None:
        if not self.clip_id.strip():
            raise ValueError("clip_id must not be empty")
        if self.fps <= 0:
            raise ValueError("fps must be greater than zero")
        for frame in self.frames:
            if not frame.asset:
                raise ValueError("frame asset must not be empty")
            if frame.duration_ms is not None and frame.duration_ms <= 0:
                raise ValueError("frame duration_ms must be greater than zero")

    def add_frame(self, asset: str, duration_ms: int | None = None) -> AnimationFrame:
        frame = AnimationFrame(asset, duration_ms)
        self.frames.append(frame)
        self.validate()
        return frame

    def duration_ms(self) -> int:
        return sum(frame.effective_duration_ms(self.fps) for frame in self.frames)

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "format_version": 1,
            "clip_id": self.clip_id,
            "name": self.name,
            "fps": self.fps,
            "loop": self.loop,
            "frames": [frame.to_dict() for frame in self.frames],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AnimationClip":
        if raw.get("format_version") != 1:
            raise ValueError("unsupported animation format_version")
        clip = cls(
            clip_id=str(raw["clip_id"]),
            name=str(raw.get("name", raw["clip_id"])),
            fps=float(raw.get("fps", 12.0)),
            loop=bool(raw.get("loop", True)),
            frames=[AnimationFrame.from_dict(item) for item in raw.get("frames", [])],
        )
        clip.validate()
        return clip


def save_clip(clip: AnimationClip, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(clip.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_clip(path: str | Path) -> AnimationClip:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return AnimationClip.from_dict(raw)
