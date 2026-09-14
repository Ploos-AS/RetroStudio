"""Native Linux creator shell.

Uses tkinter from the Python standard library so the first visible editor shell has
no third-party GUI dependency. Target-specific rendering remains in backends.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from .model import Project, load_project
from .workspace import WORKSPACES, WorkspaceState


WORKSPACE_LABELS = {
    "project": "Project",
    "assets": "Asset Library",
    "scene": "Scene Composer",
    "inspector": "Inspector",
    "animation": "Animation",
    "target_preview": "Target Preview",
    "quality": "Quality & Budget",
}


class CreatorShell:
    def __init__(self, root: tk.Tk, project: Project | None = None) -> None:
        self.root = root
        self.root.title("RetroStudio")
        self.root.minsize(960, 600)
        project = project or Project("Untitled", "untitled", "", [])
        self.state = WorkspaceState(project)
        self.status = tk.StringVar(value="Ready — create beautiful assets.")
        self.workspace_title = tk.StringVar()
        self._build_menu()
        self._build_ui()
        self.activate("scene")

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open Project…", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=8)
        outer.pack(fill="both", expand=True)

        nav = ttk.Frame(outer)
        nav.pack(side="left", fill="y", padx=(0, 8))
        ttk.Label(nav, text="RetroStudio", font=("TkDefaultFont", 14, "bold")).pack(anchor="w", pady=(0, 10))
        for workspace in WORKSPACES:
            ttk.Button(
                nav,
                text=WORKSPACE_LABELS[workspace],
                command=lambda name=workspace: self.activate(name),
            ).pack(fill="x", pady=2)

        content = ttk.Frame(outer)
        content.pack(side="left", fill="both", expand=True)
        ttk.Label(content, textvariable=self.workspace_title, font=("TkDefaultFont", 18, "bold")).pack(anchor="w")
        self.subtitle = ttk.Label(content, wraplength=720)
        self.subtitle.pack(anchor="w", pady=(4, 12))

        self.canvas = tk.Canvas(content, highlightthickness=1, background="white")
        self.canvas.pack(fill="both", expand=True)

        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w", padding=4).pack(fill="x", side="bottom")

    def activate(self, workspace: str) -> None:
        self.state.activate(workspace)
        self.workspace_title.set(WORKSPACE_LABELS[workspace])
        descriptions = {
            "project": "Project structure and target choices.",
            "assets": "Import and organize high-quality source assets non-destructively.",
            "scene": "Compose the game visually; engine internals stay out of the way.",
            "inspector": "Edit the selected creator-facing properties.",
            "animation": "Build animation from source artwork and reusable clips.",
            "target_preview": "Preview how source material maps to the selected classic target.",
            "quality": "See quality and resource guidance with concrete optimization suggestions.",
        }
        self.subtitle.configure(text=descriptions[workspace])
        self.canvas.delete("all")
        self.canvas.create_text(24, 24, anchor="nw", text=f"{WORKSPACE_LABELS[workspace]} workspace", font=("TkDefaultFont", 13))
        self.status.set(f"{self.state.project.name} — {WORKSPACE_LABELS[workspace]}")

    def open_project(self) -> None:
        filename = filedialog.askopenfilename(
            title="Open RetroStudio project",
            filetypes=(("RetroStudio project", "*.json"), ("All files", "*")),
        )
        if not filename:
            return
        try:
            self.state = WorkspaceState(load_project(Path(filename)))
        except (OSError, ValueError, KeyError) as exc:
            self.status.set(f"Could not open project: {exc}")
            return
        self.root.title(f"RetroStudio — {self.state.project.name}")
        self.activate("scene")


def main() -> None:
    root = tk.Tk()
    CreatorShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()
