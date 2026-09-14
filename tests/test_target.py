import unittest

from retrostudio.dummy_backend import DummyBackend
from retrostudio.model import Project, Scene
from retrostudio.target import BackendDescriptor, load_backend, negotiate_backend


class TargetApiTests(unittest.TestCase):
    def setUp(self):
        self.project = Project(
            name="Target API Fixture",
            project_id="org.ploos.retrostudio.target-fixture",
            default_scene="scenes/main.scene.json",
            scenes=[Scene("main", "Main", source_path="scenes/main.scene.json")],
            targets=["dummy"],
        )

    def test_descriptor_negotiation(self):
        descriptor = negotiate_backend(DummyBackend())
        self.assertEqual(descriptor.id, "dummy")
        self.assertEqual(descriptor.api_version, 1)
        self.assertEqual({cap.id for cap in descriptor.capabilities}, {"validate", "build", "package", "launch"})

    def test_module_discovery(self):
        backend = load_backend("retrostudio.dummy_backend")
        self.assertEqual(backend.describe().id, "dummy")

    def test_validate_supported_target(self):
        backend = DummyBackend()
        self.assertEqual(backend.validate(self.project, "dummy"), [])

    def test_validate_unsupported_target(self):
        backend = DummyBackend()
        diagnostics = backend.validate(self.project, "other")
        self.assertEqual(diagnostics[0].code, "target.unsupported")

    def test_build_package_and_launch_hooks(self):
        backend = DummyBackend()
        build = backend.build(self.project, "dummy", "build")
        self.assertTrue(build.ok)
        self.assertEqual(build.artifacts[0].kind, "executable")

        package = backend.package(self.project, "dummy", "dist")
        self.assertTrue(package.ok)
        self.assertEqual(package.artifacts[0].kind, "package")

        launch = backend.launch(self.project, "dummy", build.artifacts[0])
        self.assertTrue(launch.ok)
        self.assertEqual(launch.artifacts[0], build.artifacts[0])

    def test_rejects_wrong_api_version(self):
        class WrongVersionBackend(DummyBackend):
            def describe(self):
                return BackendDescriptor("wrong", "Wrong", "0", api_version=99)

        with self.assertRaises(ValueError):
            negotiate_backend(WrongVersionBackend())


if __name__ == "__main__":
    unittest.main()
