# RetroStudio roadmap

## Product north star

RetroStudio is creator-first. Artists and game designers should be able to focus on beautiful source assets, animation, levels, music and game design while the studio handles classic-hardware conversion, optimization and build complexity. Source assets remain non-destructive and target backends provide hardware-specific quality guidance.

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
- Native Linux desktop shell.
- Project Browser and Asset Library views.
- Visual Scene Composer and Inspector views.
- Animation Workspace foundation.
- Target Preview and Quality & Budget panels.

Exit criterion: host tests prove workspace navigation, selection, creator guidance and undo/redo independently of the GUI toolkit; a native Linux shell can then consume this model without moving target-specific logic into RetroStudio.

## M5 — Visual Game Creation

- Reusable visual behaviours for common mechanics: player movement, camera follow, patrols, collectibles, doors, projectiles and dialogue.
- Animation state and transitions.
- Collision painting and triggers.
- Visual event graph.
- Prefabs/templates for common game genres.
- Progressive scripting/runtime interface for advanced creators.

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

## Long-term

RetroStudio may support additional classic targets, but only through clean backend contracts. Adding another platform must not make the core platform-specific. Advanced native/script extension points must complement, not replace, the creator-first visual workflow.
