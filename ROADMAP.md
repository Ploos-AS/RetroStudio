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
