import unittest

from retrostudio.creator import edit_entity, entity_by_id, move_entity, rename_entity
from retrostudio.model import Component, Entity, Scene


class InspectorEditingTests(unittest.TestCase):
    def test_lookup_entity(self):
        scene = Scene("main", "Main", [Entity("hero", "Hero")])
        self.assertEqual(entity_by_id(scene, "hero").name, "Hero")
        with self.assertRaises(ValueError):
            entity_by_id(scene, "missing")

    def test_rename_rejects_empty_names(self):
        entity = Entity("hero", "Hero")
        rename_entity(entity, " Player ")
        self.assertEqual(entity.name, "Player")
        with self.assertRaises(ValueError):
            rename_entity(entity, "   ")

    def test_move_updates_existing_transform(self):
        entity = Entity("hero", "Hero", [Component("transform", {"x": 1, "y": 2})])
        move_entity(entity, 100, -24)
        self.assertEqual(entity.components[0].data, {"x": 100, "y": -24})

    def test_move_adds_missing_transform(self):
        entity = Entity("hero", "Hero")
        move_entity(entity, 4, 8)
        self.assertEqual(entity.components[0].type, "transform")
        self.assertEqual(entity.components[0].data, {"x": 4, "y": 8})

    def test_edit_is_creator_facing_baseline(self):
        entity = Entity("hero", "Hero", [Component("visual.asset", {"path": "assets/hero.png"})])
        edit_entity(entity, name="Main Hero", x="32", y="64")
        self.assertEqual(entity.name, "Main Hero")
        transform = next(c for c in entity.components if c.type == "transform")
        self.assertEqual(transform.data, {"x": 32, "y": 64})

    def test_invalid_edit_does_not_change_name(self):
        entity = Entity("hero", "Hero")
        with self.assertRaises(ValueError):
            edit_entity(entity, name="Renamed", x="not-a-number", y="2")
        self.assertEqual(entity.name, "Hero")


if __name__ == "__main__":
    unittest.main()
