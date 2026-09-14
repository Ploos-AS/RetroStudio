import tempfile
import unittest
from pathlib import Path

from retrostudio.animation import AnimationClip, AnimationFrame, load_clip, save_clip


class AnimationTests(unittest.TestCase):
    def test_default_fps_drives_frame_duration(self):
        frame = AnimationFrame("assets/hero-1.png")
        self.assertEqual(frame.effective_duration_ms(10), 100)

    def test_per_frame_timing_override(self):
        frame = AnimationFrame("assets/hero-1.png", 175)
        self.assertEqual(frame.effective_duration_ms(60), 175)

    def test_clip_duration_and_loop(self):
        clip = AnimationClip("walk", "Walk", fps=10, loop=True)
        clip.add_frame("assets/walk-1.png")
        clip.add_frame("assets/walk-2.png", 150)
        self.assertEqual(clip.duration_ms(), 250)
        self.assertTrue(clip.loop)

    def test_validation_rejects_invalid_fps_and_duration(self):
        with self.assertRaises(ValueError):
            AnimationClip("walk", "Walk", fps=0).validate()
        with self.assertRaises(ValueError):
            AnimationClip("walk", "Walk", frames=[AnimationFrame("assets/a.png", 0)]).validate()

    def test_round_trip(self):
        clip = AnimationClip("idle", "Idle", fps=8, loop=False)
        clip.add_frame("assets/idle-1.png")
        clip.add_frame("assets/idle-2.png", 220)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "animations" / "idle.animation.json"
            save_clip(clip, path)
            loaded = load_clip(path)
        self.assertEqual(loaded.clip_id, "idle")
        self.assertEqual(loaded.name, "Idle")
        self.assertEqual(loaded.fps, 8)
        self.assertFalse(loaded.loop)
        self.assertEqual([f.asset for f in loaded.frames], ["assets/idle-1.png", "assets/idle-2.png"])
        self.assertEqual(loaded.frames[1].duration_ms, 220)


if __name__ == "__main__":
    unittest.main()
