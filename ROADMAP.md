# RetroStudio Roadmap

## Product north star

RetroStudio is a creator-first game studio for producing high-quality games for retro platforms. Artists, designers and other creators should be able to focus on beautiful assets, animation, level design and game feel while RetroStudio handles platform constraints, conversion, validation and deterministic builds.

RetroStudio supports two first-class authoring paths over the same platform-neutral project model and toolchain:

1. **RetroStudio Native Editor** — a Linux-first, retro-specific creator workspace.
2. **Godot integration** — a Godot 4 authoring frontend/export bridge for creators who prefer Godot.

Godot is an authoring frontend, not the runtime shipped to classic machines. Target builds use small/native runtimes appropriate to each platform. The canonical project/IR belongs to RetroStudio, and builds must remain deterministic and headless-capable.

## M0 — Foundation

- [x] Establish repository structure, licensing and basic documentation.
- [x] Define platform-neutral architecture and dependency invariant.
- [x] Add host-side static qualification.
- [x] Add GitHub Actions CI.

## M1 — Core project model

- [x] Define project, scene, entity and component model.
- [x] JSON loading/saving and validation.
- [x] Deterministic project serialization.
- [x] Minimal checked-in project fixture.

## M2 — Target plugin API

- [x] Define stable target/backend interface.
- [x] Capability and diagnostic contracts.
- [x] Dummy/reference backend.
- [x] Keep RetroStudio independent of product frontends/backends.

## M3 — Asset pipeline

- [x] Platform-neutral asset metadata and registry.
- [x] Deterministic asset conversion/cache foundation.
- [x] Target-aware diagnostics and budgets.
- [x] Preserve creator source assets non-destructively.

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
- [x] Collision editor/overlay foundation with toolkit-neutral scene-space overlays, box/circle collider editing, box trigger editing, removal operations and a reusable creator-facing Tk panel.
- [x] Direct-manipulation collision geometry foundation: normalized canvas drags, entity-local conversion, scene-space resize geometry and collider/trigger painting operations with host tests.
- [x] Scene Composer collision mouse interaction with visible paint previews, mounted box resize handles, metadata-preserving resize gestures and headless qualification.
- [x] Consolidate collision canvas interaction on the mounted Scene Composer layer; remove the obsolete parallel Tk collision-canvas implementation.
- [x] Visual event graph with creator node palette, direct node/link manipulation, node inspector, diagnostics and per-entity project persistence.
- [x] Prefab foundation with platform-neutral starter objects for platformer, adventure and action games.
- Prefab/template browser and richer common game-genre starter sets.
- Progressive scripting/runtime interface for advanced creators.

Current M5 foundation stores behaviours as `behaviour.<Name>` entity components so projects remain ordinary scene data. Backends translate these authoring components into target/runtime-specific implementations; RetroStudio owns only the creator-facing semantics, defaults and validation. The behaviour editor is schema-driven (`number`, `boolean`, `choice`, text and multiline fields), so new behaviours can expose creator-friendly controls without hand-written raw component editors. Animation state machines remain platform-neutral: creator states reference reusable clip IDs and transitions use named parameters and simple conditions that backends can translate later. Collision authoring follows the same rule: canonical collider/trigger components describe creator intent while each target backend remains responsible for an efficient native implementation. Toolkit-neutral overlay and painting geometry keeps collision visualization and direct manipulation reusable by the native Scene Composer and future frontends instead of embedding project semantics in Tk canvas code. The native editor now has one mounted collision interaction path, avoiding divergent duplicate canvas implementations. Event graphs use the canonical `logic.event_graph` entity component, so creator-authored nodes, links, positions and properties survive project save/load without frontend-specific data. Prefabs compose the same ordinary behaviours, collision and transform components rather than introducing a parallel runtime model.

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

## M13 — Native Editor as a first-class frontend

- Formalize the native Linux editor as a consumer of the same frontend contract used by Godot.
- Move frontend-only concerns out of the canonical project/compiler core.
- Improve creator workflows for scene composition, animation, events, behaviours, assets and target previews.
- Preserve editor state separately from portable project semantics where appropriate.
- Keep headless builds independent of GUI toolkit availability.

Exit criterion: Native Editor and Godot frontend can independently edit the same supported project subset without changing target build semantics.

## M14 — Multi-frontend interoperability

- Round-trip fixtures between Native Editor, Godot and canonical RetroStudio IR.
- Detect unsupported frontend constructs explicitly.
- Preserve unknown/forward-compatible metadata where safe.
- Add migration/version compatibility tests.
- Document mixed-workflow recommendations for artists, designers and programmers.

Exit criterion: a reference project can move Native Editor → Godot → Native Editor while retaining all supported gameplay and asset semantics and producing the same target build inputs.

## M15 — Expanded retro target families

- Add capability profiles and backend contracts for additional families without weakening stronger targets to a lowest common denominator.
- Planned families include Amiga A500/OCS/ECS/AGA variants, Atari ST/STE/Falcon, DOS, and later C64, Mega Drive, SNES and selected 8-bit systems.
- Surface target-specific resource budgets and feature availability in authoring frontends.
- Allow richer assets/features on stronger targets from the same canonical project where capability profiles permit them.

Exit criterion: one creator project can target multiple materially different retro systems with deterministic builds, explicit capability diagnostics and no frontend-specific target logic.
