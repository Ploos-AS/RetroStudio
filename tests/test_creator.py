import tempfile
import unittest
from pathlib import Path

from retrostudio.creator import import_asset, place_asset
from retrostudio.model import Project, Scene


class CreatorOperationsTests(unittest.TestCase):
    def test_import_asset_copies_source_without_modifying_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "hero.png"
            source.write_bytes(b"source-art")
            project_dir = root / "project"
            project_dir.mkdir()
            project = Project("Demo", "demo", "", [], source_path=(project_dir / "project.json").as_posix())

            imported = import_asset(project, source)

            self.assertEqual(source.read_bytes(), b"source-art")
            self.assertEqual((project_dir / imported.project_path).read_bytes(), b"source-art")
            self.assertIn(imported.project_path, project.assets)

    def test_import_name_collision_keeps_both_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project_dir = root / "project"
            project_dir.mkdir()
            project = Project("Demo", "demo", "", [], source_path=(project_dir / "project.json").as_posix())
            first_dir = root / "one"
            second_dir = root / "two"
            first_dir.mkdir()
            second_dir.mkdir()
            (first_dir / "hero.png").write_bytes(b"one")
            (second_dir / "hero.png").write_bytes(b"two")

            first = import_asset(project, first_dir / "hero.png")
            second = import_asset(project, second_dir / "hero.png")

            self.assertNotEqual(first.project_path, second.project_path)
            self.assertEqual(len(project.assets), 2)

    def test_place_asset_creates_visual_entity(self):
        scene = Scene("main", "Main")
        entity = place_asset(scene, "assets/hero.png", 32, 48)
        self.assertEqual(entity.entity_id, "hero")
        self.assertEqual(entity.components[0].type, "transform")
        self.assertEqual(entity.components[0].data, {"x": 32, "y": 48})
        self.assertEqual(entity.components[1].type, "visual.asset")
        self.assertEqual(entity.components[1].data["path"], "assets/hero.png")

    def test_place_asset_generates_unique_ids(self):
        scene = Scene("main", "Main")
        self.assertEqual(place_asset(scene, "assets/hero.png").entity_id, "hero")
        self.assertEqual(place_asset(scene, "assets/hero.png").entity_id, "hero-2")


if __name__ == "__main__":
    unittest.main()
