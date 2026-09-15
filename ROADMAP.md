# RetroStudio roadmap

## Product north star

RetroStudio is creator-first. Artists and game designers should be able to focus on beautiful source assets, animation, levels, music and game design while the studio handles classic-hardware conversion, optimization and build complexity. Source assets remain non-destructive and target backends provide hardware-specific quality guidance.

RetroStudio is not tied to one editor. The long-term product has two first-class authoring frontends over the same platform-neutral core and project model:

1. **RetroStudio Native Editor** — a Linux-first, retro-focused visual creator environment designed for artists, designers and asset makers.
2. **Godot integration** — an addon/export bridge for creators who prefer Godot's mature editor and workflows.

Both frontends must feed the same RetroStudio project/IR, compiler, asset pipeline and target backends. Target games do not require the Godot runtime. A Godot fork is explicitly deferred unless future editor requirements cannot reasonably be delivered through the addon/integration boundary.

## M0 — Foundation

- [x] Define platform-neutral core responsibilities.
- [x] Define target/backend boundary.
- [x] Version the project manifest from day one.
- [x] Add minimal sample project.
- [x] Add host-side repository/schema checks.
- [x] Document AmiStudio as first consumer and AtariStudio as portability proof.

Exit criterion: `make check` validates the M0 repository and sample manifest without any retro target SDK.

## M1 — Core project model

- [x] Parse/load/save project manifests.
- [x] Stable diagnostics model.
- [x] Scene/entity/component data model.
- [x] Deterministic project-relative paths and IDs.
- [x] Unit tests and round-trip tests.

Exit criterion: host-side tests load the checked-in minimal fixture, round-trip a project with entities/components, reject escaping paths, and report duplicate IDs deterministically.

## M2 — Target plugin API

- [x] Backend discovery and version negotiation.
- [x] Capability descriptors.
- [x] Target-specific validation interface.
- [x] Build/package/launch hooks.
- [x] Dummy reference backend for CI.

Exit criterion: the reference backend is discovered through the public API, API-version mismatches are rejected, capabilities are reported, and validate/build/package/launch hooks are covered by host-side tests.

## M3 — Asset pipeline

- [x] Images, palettes, tile maps and audio source assets.
- [x] Content hashing and build cache.
- [x] Target conversion requests.
- [x] Resource-budget diagnostics.

Exit criterion: host tests cover the four baseline asset classes, deterministic SHA-256 source hashing and conversion cache keys, cache round-trips, and generic resource-budget violations without embedding platform-specific conversion logic in RetroStudio.

## M4 — Creator Workspace Foundation

- [x] Define creator-first product principles and non-destructive source-asset policy.
- [x] Define stable Project, Asset, Scene, Inspector, Animation, Target Preview and Quality workspaces.
- [x] Add toolkit-neutral workspace state and selection model.
- [x] Add creator-facing guidance alongside stable machine-readable diagnostics.
- [x] Add undo/redo command model.
- [x] Native Linux desktop shell with project opening and all creator workspaces navigable.
- [x] Functional Project Browser foundation and Asset Library with non-destructive import.
- [x] Functional Scene Composer foundation with asset placement and visual scene-object layout.
- [x] Inspector editing for selected scene-object name and position with persistence.
- [x] Animation Workspace foundation with clips, frames, FPS, loop, per-frame timing overrides and JSON persistence.
- [x] Target Preview and Quality & Budget panels with target selection, backend facts, diagnostics, resource budgets and creator-facing guidance.

Current shell runs with `make run`. Creators can import source assets, compose scenes, inspect objects and build reusable animation clips. Target Preview accepts project target profiles and selected assets, while backend adapters can inject target-specific preview facts without adding platform assumptions to RetroStudio. Quality & Budget combines project/backend diagnostics, resource usage and backend-specific or generic creator guidance into actionable feedback.

Exit criterion: host tests prove workspace navigation, selection, creator guidance, non-destructive asset import, scene placement, Inspector editing, animation model/persistence, target preview/quality reporting and undo/redo independently of the GUI toolkit; static qualification verifies the native shell and full M4 creator workspace surface.

## M5 — Visual Game Creation

- [x] Reusable visual behaviours foundation for player movement, camera follow, patrols, collectibles, doors and projectiles, with stable platform-neutral components, creator defaults and validation.
- [x] Dialogue behaviour plus schema-driven creator-facing behaviour editor foundation with add/update/remove operations and a reusable Tk editor panel.
- [x] Animation states and transitions foundation with clip-referencing states, creator parameters/conditions, normalized exit timing, validation and JSON persistence.
- [x] Collision/trigger data-model foundation with platform-neutral box/circle shapes, collider layers, solid flags, trigger events/filters and structured validation.
- Collision painting/editor UX and scene overlays.
- Visual event graph.
- Prefabs/templates for common game genres.
- Progressive scripting/runtime interface for advanced creators.

Current M5 foundation stores behaviours as `behaviour.<Name>` entity components so projects remain ordinary scene data. Backends translate these authoring components into target/runtime-specific implementations; RetroStudio owns only the creator-facing semantics, defaults and validation. The behaviour editor is schema-driven (`number`, `boolean`, `choice`, text and multiline fields), so new behaviours can expose creator-friendly controls without hand-written raw component editors. Animation state machines remain platform-neutral: creator states reference reusable clip IDs and transitions use named parameters and simple conditions that backends can translate later. Collision authoring follows the same rule: canonical collider/trigger components describe creator intent while each target backend remains responsible for an efficient native implementation.

## M6 — Host Preview

- Fast Linux preview runtime.
- Input mapping.
- Debug and collision overlays.
- Live scene/animation iteration.
- Deterministic gameplay test fixtures.

## M7 — Creator Asset Tooling

- Sprite-sheet slicing and animation authoring.
- Tile-set/tile-map authoring and reuse analysis.
- Palette workspace and target-aware palette preview.
- Parallax/layer composition tools.
- Audio/music asset workflow.
- Non-destructive optimization suggestions.

## M8 — AmiStudio integration

- First production backend integration.
- OCS/ECS/AGA capability profiles.
- Amiga asset pipeline and runtime handoff.
- Build/package/emulator launch integration.
- Hardware-aware budgets and creator-facing optimization guidance.

## M9 — AtariStudio integration

- ST/STE/TT/Falcon capability profiles.
- Atari asset/runtime handoff.
- Hatari/ARAnyM integration where appropriate.
- Hardware-aware budgets and creator-facing optimization guidance.
- Use the second architecture to remove hidden Amiga assumptions from RetroStudio.

## M10 — Reproducible releases and SDK

- Stable backend SDK.
- Versioned project migrations.
- Reproducible Linux release builds.
- Plugin documentation and examples.
- Creator tutorials and starter templates.

## M11 — Canonical RetroStudio IR and frontend contract

- Formalize the platform-neutral RetroStudio intermediate representation (IR) used by every authoring frontend.
- Separate authoring documents from generated target artifacts.
- Define stable scene, animation, event, behaviour, asset and metadata interchange contracts.
- Define frontend capability/version negotiation.
- Add deterministic import/export and round-trip fixtures.
- Ensure CLI builds are independent of both the native editor and Godot.

Exit criterion: the same checked-in project/IR fixture can be produced/consumed without frontend-specific target logic and builds identically through the headless RetroStudio toolchain.

## M12 — Godot frontend foundation

- Godot 4 addon that connects to RetroStudio without embedding target-specific logic in Godot.
- Import/export mapping between Godot scenes/resources and RetroStudio IR.
- Map sprites, animations, tile maps, scenes, transforms and basic gameplay metadata.
- Surface RetroStudio target profiles and structured diagnostics inside Godot.
- Build/export commands invoke the same RetroStudio CLI/compiler used by the native editor.
- Preserve high-quality Godot source assets non-destructively.
- Document unsupported Godot features explicitly rather than silently approximating them.

Exit criterion: one reference game can be authored through Godot, exported to RetroStudio IR and built by the normal headless pipeline with deterministic output.

## M13 — Native Editor as first-class frontend

- Move the existing creator workspace onto the formal frontend/IR contract where needed.
- Visual scene, animation, tile, collision and event workflows operate directly on canonical RetroStudio data.
- Target profile selector with live hardware budgets and compatibility guidance.
- Creator-friendly build/run workflow without requiring Godot.
- Keep advanced scripting optional and progressive.

Exit criterion: the reference game can be authored entirely in the native editor and produces semantically equivalent RetroStudio IR to the Godot-authored fixture.

## M14 — Multi-frontend interoperability

- Define safe interchange rules between Native Editor and Godot workflows.
- Preserve stable IDs and portable metadata across frontend round trips.
- Detect frontend-specific data that cannot round-trip losslessly.
- Add conformance tests proving both frontends consume the same core semantics.
- Document recommended workflows for teams mixing Godot and RetroStudio Native Editor.

## M15 — Expanded retro target families

After Amiga and Atari prove the architecture, evaluate additional clean backends such as DOS, Mega Drive, SNES and selected 8-bit systems. New targets must use the same frontend-independent IR and backend contracts. Platform scope is driven by achievable quality and maintainability, not target count.

## Long-term

RetroStudio aims to become a frontend-independent creator platform for high-quality games on classic hardware: one project model, one asset/build pipeline and multiple authoring experiences and target backends.

The native RetroStudio Editor remains the purpose-built creator experience. Godot remains a first-class optional frontend for creators who prefer it. A dedicated Godot-derived RetroStudio distribution may be evaluated only if addon APIs become a material limitation; maintaining a permanent Godot fork is not a prerequisite or near-term goal.

Advanced native/script extension points must complement, not replace, the creator-first visual workflow. Adding another platform must not make the core platform-specific.