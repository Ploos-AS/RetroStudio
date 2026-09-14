import json
from pathlib import Path
import tempfile
import unittest

from retrostudio.model import Component, Entity, Project, Scene, load_project, save_project


class ProjectModelTests(unittest.TestCase):
    def test_load_minimal_fixture(self):
        project = load_project("examples/minimal/project.json")
        self.assertEqual(project.project_id, "org.ploos.retrostudio.minimal")
        self.assertEqual(len(project.scenes), 1)
        self.assertEqual(project.scenes[0].scene_id, "main")
        self.assertEqual(project.diagnostics(), [])

    def test_round_trip_project(self):
        project = Project(
            name="Round Trip",
            project_id="org.ploos.roundtrip",
            default_scene="scenes/main.scene.json",
            scenes=[
                Scene(
                    scene_id="main",
                    name="Main",
                    source_path="scenes/main.scene.json",
                    entities=[
                        Entity(
                            entity_id="player",
                            name="Player",
                            components=[Component("transform", {"x": 1, "y": 2})],
                        )
                    ],
                )
            ],
            assets=["assets/player.png"],
            targets=["dummy"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "project.json"
            save_project(project, path)
            loaded = load_project(path)
            self.assertEqual(loaded.name, project.name)
            self.assertEqual(loaded.scenes[0].entities[0].entity_id, "player")
            self.assertEqual(loaded.scenes[0].entities[0].components[0].data["x"], 1)

    def test_duplicate_entity_diagnostic(self):
        scene = Scene(
            scene_id="main",
            name="Main",
            source_path="scenes/main.scene.json",
            entities=[Entity("x", "A"), Entity("x", "B")],
        )
        project = Project("P", "org.example.p", "scenes/main.scene.json", [scene])
        codes = [item.code for item in project.diagnostics()]
        self.assertIn("entity.duplicate_id", codes)

    def test_reject_parent_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.json").write_text(json.dumps({
                "format_version": 1,
                "name": "Bad",
                "project_id": "org.example.bad",
                "default_scene": "../outside.json",
                "scenes": [],
                "assets": [],
                "targets": []
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_project(root / "project.json")


if __name__ == "__main__":
    unittest.main()
