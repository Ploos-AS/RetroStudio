"""Native Linux creator shell.

Uses tkinter from the Python standard library so the first visible editor shell has
no third-party GUI dependency. Target-specific rendering remains in backends.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from .animation import AnimationClip, load_clip, save_clip
from .creator import edit_entity, entity_by_id, import_asset, place_asset
from .model import Project, Scene, load_project, save_project
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
        self.root.minsize(1024, 640)
        project = project or Project("Untitled", "untitled", "", [Scene("main", "Main")])
        self.state = WorkspaceState(project)
        self.status = tk.StringVar(value="Ready — create beautiful assets.")
        self.workspace_title = tk.StringVar()
        self.selected_asset: str | None = None
        self.current_clip: AnimationClip | None = None
        self._build_menu()
        self._build_ui()
        self.activate("scene")

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open Project…", command=self.open_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
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
            ttk.Button(nav, text=WORKSPACE_LABELS[workspace], command=lambda name=workspace: self.activate(name)).pack(fill="x", pady=2)

        self.content = ttk.Frame(outer)
        self.content.pack(side="left", fill="both", expand=True)
        ttk.Label(self.content, textvariable=self.workspace_title, font=("TkDefaultFont", 18, "bold")).pack(anchor="w")
        self.subtitle = ttk.Label(self.content, wraplength=760)
        self.subtitle.pack(anchor="w", pady=(4, 12))
        self.workspace_frame = ttk.Frame(self.content)
        self.workspace_frame.pack(fill="both", expand=True)
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w", padding=4).pack(fill="x", side="bottom")

    def activate(self, workspace: str) -> None:
        self.state.activate(workspace)
        self.workspace_title.set(WORKSPACE_LABELS[workspace])
        descriptions = {
            "project": "Project structure and target choices.",
            "assets": "Import and organize high-quality source assets non-destructively.",
            "scene": "Compose the game visually; engine internals stay out of the way.",
            "inspector": "Edit the selected creator-facing properties.",
            "animation": "Build clips from source artwork, tune timing and keep frame assets reusable.",
            "target_preview": "Preview how source material maps to the selected classic target.",
            "quality": "See quality and resource guidance with concrete optimization suggestions.",
        }
        self.subtitle.configure(text=descriptions[workspace])
        for child in self.workspace_frame.winfo_children():
            child.destroy()
        renderer = getattr(self, f"_render_{workspace}", self._render_placeholder)
        renderer()
        self.status.set(f"{self.state.project.name} — {WORKSPACE_LABELS[workspace]}")

    def _render_placeholder(self) -> None:
        ttk.Label(self.workspace_frame, text=f"{self.workspace_title.get()} workspace").pack(anchor="nw", padx=12, pady=12)

    def _render_project(self) -> None:
        project = self.state.project
        ttk.Label(self.workspace_frame, text=f"Name: {project.name}").pack(anchor="w", padx=12, pady=4)
        ttk.Label(self.workspace_frame, text=f"Project ID: {project.project_id}").pack(anchor="w", padx=12, pady=4)
        ttk.Label(self.workspace_frame, text=f"Scenes: {len(project.scenes)}").pack(anchor="w", padx=12, pady=4)
        ttk.Label(self.workspace_frame, text=f"Source assets: {len(project.assets)}").pack(anchor="w", padx=12, pady=4)

    def _render_assets(self) -> None:
        toolbar = ttk.Frame(self.workspace_frame)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Import Asset…", command=self.import_asset_ui).pack(side="left")
        ttk.Button(toolbar, text="Place in Scene", command=self.place_selected_asset).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Animate Asset", command=self.animate_selected_asset).pack(side="left")
        self.asset_list = tk.Listbox(self.workspace_frame, exportselection=False)
        self.asset_list.pack(fill="both", expand=True)
        for asset in sorted(self.state.project.assets):
            self.asset_list.insert("end", asset)
        self.asset_list.bind("<<ListboxSelect>>", self._on_asset_select)
        if self.selected_asset in self.state.project.assets:
            index = sorted(self.state.project.assets).index(self.selected_asset)
            self.asset_list.selection_set(index)

    def _render_scene(self) -> None:
        split = ttk.Panedwindow(self.workspace_frame, orient="horizontal")
        split.pack(fill="both", expand=True)
        entities_frame = ttk.Frame(split, padding=6)
        canvas_frame = ttk.Frame(split, padding=6)
        split.add(entities_frame, weight=1)
        split.add(canvas_frame, weight=4)
        ttk.Label(entities_frame, text="Scene Objects", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        entity_list = tk.Listbox(entities_frame, exportselection=False)
        entity_list.pack(fill="both", expand=True, pady=(6, 0))
        scene = self._active_scene()
        if scene is None:
            ttk.Label(canvas_frame, text="This project has no scene yet.").pack(anchor="center", expand=True)
            return
        for entity in scene.entities:
            entity_list.insert("end", f"{entity.name}  [{entity.entity_id}]")
        entity_list.bind("<<ListboxSelect>>", lambda _event: self._on_entity_select(entity_list, scene))
        current_id = self.state.selection.item_id if self.state.selection and self.state.selection.kind == "entity" else None
        if current_id:
            for index, entity in enumerate(scene.entities):
                if entity.entity_id == current_id:
                    entity_list.selection_set(index)
                    entity_list.see(index)
                    break
        self.scene_canvas = tk.Canvas(canvas_frame, background="white", highlightthickness=1)
        self.scene_canvas.pack(fill="both", expand=True)
        self.scene_canvas.create_text(16, 16, anchor="nw", text=scene.name, font=("TkDefaultFont", 12, "bold"))
        for entity in scene.entities:
            position = self._entity_position(entity)
            visual = self._entity_asset(entity)
            if position is None:
                continue
            x, y = position
            label = Path(visual).name if visual else entity.name
            tag = f"entity:{entity.entity_id}"
            self.scene_canvas.create_rectangle(x, y, x + 96, y + 48, tags=(tag,))
            self.scene_canvas.create_text(x + 48, y + 24, text=label, width=88, tags=(tag,))
            self.scene_canvas.tag_bind(tag, "<Button-1>", lambda _event, eid=entity.entity_id: self._select_entity_and_inspect(eid))

    def _render_inspector(self) -> None:
        scene = self._active_scene()
        selection = self.state.selection
        if scene is None or selection is None or selection.kind != "entity":
            ttk.Label(self.workspace_frame, text="Select an object in Scene Composer to edit it.").pack(anchor="nw", padx=12, pady=12)
            return
        try:
            entity = entity_by_id(scene, selection.item_id)
        except ValueError:
            ttk.Label(self.workspace_frame, text="The selected scene object no longer exists.").pack(anchor="nw", padx=12, pady=12)
            return
        position = self._entity_position(entity) or (0, 0)
        visual = self._entity_asset(entity)
        form = ttk.Frame(self.workspace_frame, padding=12)
        form.pack(anchor="nw", fill="x")
        ttk.Label(form, text=f"Object ID: {entity.entity_id}").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        ttk.Label(form, text="Name").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.inspector_name = tk.StringVar(value=entity.name)
        ttk.Entry(form, textvariable=self.inspector_name, width=36).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="X").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        self.inspector_x = tk.StringVar(value=str(position[0]))
        ttk.Entry(form, textvariable=self.inspector_x, width=16).grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Y").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.inspector_y = tk.StringVar(value=str(position[1]))
        ttk.Entry(form, textvariable=self.inspector_y, width=16).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Label(form, text="Visual asset").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(form, text=visual or "—").grid(row=4, column=1, sticky="w", pady=4)
        ttk.Button(form, text="Apply Changes", command=lambda: self.apply_inspector(entity)).grid(row=5, column=1, sticky="w", pady=(12, 0))
        form.columnconfigure(1, weight=1)

    def _render_animation(self) -> None:
        toolbar = ttk.Frame(self.workspace_frame)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="New Clip", command=self.new_animation_clip).pack(side="left")
        ttk.Button(toolbar, text="Open Clip…", command=self.open_animation_clip).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Add Selected Asset Frame", command=self.add_animation_frame).pack(side="left")
        ttk.Button(toolbar, text="Save Clip", command=self.save_animation_clip).pack(side="left", padx=6)

        if self.current_clip is None:
            ttk.Label(self.workspace_frame, text="Create a clip or choose an asset and use Animate Asset.").pack(anchor="nw", padx=12, pady=12)
            return

        form = ttk.Frame(self.workspace_frame)
        form.pack(fill="x", pady=(0, 8))
        self.animation_name = tk.StringVar(value=self.current_clip.name)
        self.animation_fps = tk.StringVar(value=str(self.current_clip.fps))
        self.animation_loop = tk.BooleanVar(value=self.current_clip.loop)
        ttk.Label(form, text=f"Clip ID: {self.current_clip.clip_id}").grid(row=0, column=0, columnspan=2, sticky="w", pady=4)
        ttk.Label(form, text="Name").grid(row=1, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(form, textvariable=self.animation_name, width=32).grid(row=1, column=1, sticky="w")
        ttk.Label(form, text="FPS").grid(row=2, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(form, textvariable=self.animation_fps, width=10).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(form, text="Loop", variable=self.animation_loop).grid(row=3, column=1, sticky="w")
        ttk.Button(form, text="Apply Clip Settings", command=self.apply_animation_settings).grid(row=4, column=1, sticky="w", pady=(6, 0))

        ttk.Label(self.workspace_frame, text=f"Frames — total {self.current_clip.duration_ms()} ms", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(8, 4))
        self.animation_frame_list = tk.Listbox(self.workspace_frame, exportselection=False)
        self.animation_frame_list.pack(fill="both", expand=True)
        for index, frame in enumerate(self.current_clip.frames, start=1):
            timing = frame.duration_ms if frame.duration_ms is not None else f"{frame.effective_duration_ms(self.current_clip.fps)} ms @ FPS"
            self.animation_frame_list.insert("end", f"{index:02d}  {frame.asset}  —  {timing}")

    def _render_target_preview(self) -> None:
        self._render_placeholder()

    def _render_quality(self) -> None:
        self._render_placeholder()

    def _active_scene(self) -> Scene | None:
        project = self.state.project
        if project.default_scene:
            for scene in project.scenes:
                if scene.source_path == project.default_scene:
                    return scene
        return project.scenes[0] if project.scenes else None

    @staticmethod
    def _entity_position(entity):
        for component in entity.components:
            if component.type == "transform":
                return int(component.data.get("x", 0)), int(component.data.get("y", 0))
        return None

    @staticmethod
    def _entity_asset(entity):
        for component in entity.components:
            if component.type == "visual.asset":
                return str(component.data.get("path", ""))
        return ""

    def _on_asset_select(self, _event=None) -> None:
        selection = self.asset_list.curselection()
        if selection:
            self.selected_asset = str(self.asset_list.get(selection[0]))
            self.state.select("asset", self.selected_asset)
            self.status.set(f"Selected asset: {self.selected_asset}")

    def _on_entity_select(self, widget: tk.Listbox, scene: Scene) -> None:
        selection = widget.curselection()
        if not selection:
            return
        entity = scene.entities[selection[0]]
        self.state.select("entity", entity.entity_id)
        self.status.set(f"Selected object: {entity.name}")

    def _select_entity_and_inspect(self, entity_id: str) -> None:
        self.state.select("entity", entity_id)
        self.activate("inspector")

    def apply_inspector(self, entity) -> None:
        try:
            edit_entity(entity, name=self.inspector_name.get(), x=self.inspector_x.get(), y=self.inspector_y.get())
            self.save_project()
        except (OSError, ValueError) as exc:
            self.status.set(f"Could not apply inspector changes: {exc}")
            return
        self.status.set(f"Updated {entity.name}")
        self.activate("inspector")

    def new_animation_clip(self) -> None:
        base = Path(self.selected_asset).stem if self.selected_asset else "new-clip"
        clip_id = base.replace(" ", "-").lower() or "new-clip"
        self.current_clip = AnimationClip(clip_id, base or "New Clip")
        if self.selected_asset:
            self.current_clip.add_frame(self.selected_asset)
        self.activate("animation")

    def animate_selected_asset(self) -> None:
        if not self.selected_asset:
            self.status.set("Select an asset first.")
            return
        self.new_animation_clip()

    def add_animation_frame(self) -> None:
        if self.current_clip is None:
            self.new_animation_clip()
        if not self.selected_asset:
            self.status.set("Select an asset in Asset Library before adding a frame.")
            return
        self.current_clip.add_frame(self.selected_asset)
        self.status.set(f"Added frame: {self.selected_asset}")
        self.activate("animation")

    def apply_animation_settings(self) -> None:
        if self.current_clip is None:
            return
        try:
            fps = float(self.animation_fps.get())
            if fps <= 0:
                raise ValueError("FPS must be greater than zero")
            self.current_clip.name = self.animation_name.get().strip() or self.current_clip.clip_id
            self.current_clip.fps = fps
            self.current_clip.loop = bool(self.animation_loop.get())
            self.current_clip.validate()
        except ValueError as exc:
            self.status.set(f"Could not apply animation settings: {exc}")
            return
        self.status.set(f"Updated animation clip {self.current_clip.name}")
        self.activate("animation")

    def _animation_path(self) -> Path:
        if self.current_clip is None:
            raise ValueError("no animation clip selected")
        if not self.state.project.source_path:
            raise ValueError("save the project before saving animations")
        root = Path(self.state.project.source_path).parent
        return root / "animations" / f"{self.current_clip.clip_id}.animation.json"

    def save_animation_clip(self) -> None:
        if self.current_clip is None:
            self.status.set("Create or open an animation clip first.")
            return
        try:
            save_clip(self.current_clip, self._animation_path())
        except (OSError, ValueError) as exc:
            self.status.set(f"Could not save animation: {exc}")
            return
        self.status.set(f"Saved animation: {self.current_clip.clip_id}")

    def open_animation_clip(self) -> None:
        filename = filedialog.askopenfilename(
            title="Open RetroStudio animation clip",
            filetypes=(("RetroStudio animation", "*.animation.json"), ("JSON", "*.json"), ("All files", "*")),
        )
        if not filename:
            return
        try:
            self.current_clip = load_clip(filename)
        except (OSError, ValueError, KeyError) as exc:
            self.status.set(f"Could not open animation: {exc}")
            return
        self.activate("animation")

    def import_asset_ui(self) -> None:
        filename = filedialog.askopenfilename(
            title="Import source asset",
            filetypes=(("Creator assets", "*.png *.gif *.jpg *.jpeg *.bmp *.wav *.aiff *.mod *.xm *.s3m *.it *.tmx *.json"), ("All files", "*")),
        )
        if not filename:
            return
        try:
            imported = import_asset(self.state.project, filename)
            self.selected_asset = imported.project_path
            self.save_project()
        except (OSError, ValueError) as exc:
            self.status.set(f"Could not import asset: {exc}")
            return
        self.status.set(f"Imported non-destructively: {imported.project_path}")
        self.activate("assets")

    def place_selected_asset(self) -> None:
        if not self.selected_asset:
            self.status.set("Select an asset first.")
            return
        scene = self._active_scene()
        if scene is None:
            scene = Scene("main", "Main", source_path="scenes/main.scene.json")
            self.state.project.scenes.append(scene)
            self.state.project.default_scene = scene.source_path
        offset = len(scene.entities) * 24
        entity = place_asset(scene, self.selected_asset, 64 + offset, 64 + offset)
        self.state.select("entity", entity.entity_id)
        self.save_project()
        self.status.set(f"Placed {self.selected_asset} as {entity.entity_id}")
        self.activate("scene")

    def open_project(self) -> None:
        filename = filedialog.askopenfilename(title="Open RetroStudio project", filetypes=(("RetroStudio project", "*.json"), ("All files", "*")))
        if not filename:
            return
        try:
            self.state = WorkspaceState(load_project(Path(filename)))
        except (OSError, ValueError, KeyError) as exc:
            self.status.set(f"Could not open project: {exc}")
            return
        self.selected_asset = None
        self.current_clip = None
        self.root.title(f"RetroStudio — {self.state.project.name}")
        self.activate("scene")

    def save_project(self) -> None:
        project = self.state.project
        if not project.source_path:
            filename = filedialog.asksaveasfilename(title="Save RetroStudio project", defaultextension=".json", filetypes=(("RetroStudio project", "*.json"),))
            if not filename:
                return
            project.source_path = Path(filename).as_posix()
        try:
            save_project(project, project.source_path)
        except (OSError, ValueError) as exc:
            self.status.set(f"Could not save project: {exc}")
            return
        self.status.set(f"Saved {project.name}")


def main() -> None:
    root = tk.Tk()
    CreatorShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()
