"""Reference backend used to qualify the RetroStudio M2 target API."""

from __future__ import annotations

from .model import Diagnostic, Project
from .target import BackendDescriptor, BackendResult, BuildArtifact, Capability


class DummyBackend:
    def describe(self) -> BackendDescriptor:
        return BackendDescriptor(
            id="dummy",
            display_name="RetroStudio Dummy Backend",
            backend_version="0.0.0-m2",
            capabilities=(
                Capability("validate"),
                Capability("build"),
                Capability("package"),
                Capability("launch"),
            ),
        )

    def validate(self, project: Project, target: str) -> list[Diagnostic]:
        diagnostics = list(project.diagnostics())
        if target != "dummy":
            diagnostics.append(
                Diagnostic("error", "target.unsupported", f"dummy backend does not support target: {target}", "targets")
            )
        return diagnostics

    def build(self, project: Project, target: str, output_dir: str) -> BackendResult:
        diagnostics = self.validate(project, target)
        artifacts = [] if any(item.level == "error" for item in diagnostics) else [
            BuildArtifact("executable", f"{output_dir.rstrip('/')}/{project.project_id}.dummy")
        ]
        return BackendResult(diagnostics=diagnostics, artifacts=artifacts)

    def package(self, project: Project, target: str, output_dir: str) -> BackendResult:
        diagnostics = self.validate(project, target)
        artifacts = [] if any(item.level == "error" for item in diagnostics) else [
            BuildArtifact("package", f"{output_dir.rstrip('/')}/{project.project_id}.dummy-package")
        ]
        return BackendResult(diagnostics=diagnostics, artifacts=artifacts)

    def launch(self, project: Project, target: str, artifact: BuildArtifact | None = None) -> BackendResult:
        diagnostics = self.validate(project, target)
        if artifact is None and not any(item.level == "error" for item in diagnostics):
            diagnostics.append(Diagnostic("warning", "launch.no_artifact", "launch called without an artifact"))
        return BackendResult(diagnostics=diagnostics, artifacts=[artifact] if artifact else [])


def retrostudio_backend() -> DummyBackend:
    return DummyBackend()
