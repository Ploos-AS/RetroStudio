# RetroStudio roadmap

## M0 — Foundation

- [x] Define platform-neutral core responsibilities.
- [x] Define target/backend boundary.
- [x] Version the project manifest from day one.
- [x] Add minimal sample project.
- [x] Add host-side repository/schema checks.
- [x] Document AmiStudio as first consumer and AtariStudio as portability proof.

Exit criterion: `make check` validates the M0 repository and sample manifest without any retro target SDK.

## M1 — Core project model

- Parse/load/save project manifests.
- Stable diagnostics model.
- Scene/entity/component data model.
- Deterministic IDs and paths.
- Unit tests and round-trip tests.

## M2 — Target plugin API

- Backend discovery and version negotiation.
- Capability descriptors.
- Target-specific validation interface.
- Build/package/launch hooks.
- Dummy reference backend for CI.

## M3 — Asset pipeline

- Images, palettes, tile maps and audio source assets.
- Content hashing and build cache.
- Target conversion requests.
- Resource-budget diagnostics.

## M4 — Linux editor foundation

- Native Linux desktop application.
- Project browser.
- Scene canvas and inspector.
- Asset browser.
- Diagnostics/resource-budget panels.
- Undo/redo command model.

## M5 — Gameplay model

- Entities/components.
- Animation state.
- Collision and triggers.
- Event graph.
- Script/runtime interface.

## M6 — Host preview

- Fast Linux preview runtime.
- Input mapping.
- Debug overlays.
- Deterministic gameplay test fixtures.

## M7 — AmiStudio integration

- First production backend integration.
- OCS/ECS/AGA capability profiles.
- Amiga asset pipeline and runtime handoff.
- Build/package/emulator launch integration.
- Hardware-aware budgets and diagnostics.

## M8 — AtariStudio integration

- ST/STE/TT/Falcon capability profiles.
- Atari asset/runtime handoff.
- Hatari/ARAnyM integration where appropriate.
- Use the second architecture to remove any hidden Amiga assumptions from RetroStudio.

## M9 — Reproducible releases and SDK

- Stable backend SDK.
- Versioned project migrations.
- Reproducible release builds.
- Plugin documentation and examples.

## Long-term

RetroStudio may support additional classic targets, but only through clean backend contracts. Adding another platform must not make the core platform-specific.
