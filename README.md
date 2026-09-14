# RetroStudio

RetroStudio is an open-source, Linux-first **creator-first game studio** for building high-quality games for classic 16/32-bit systems.

The primary users are creators, pixel artists, animators, level designers, musicians and asset makers. RetroStudio should let them spend most of their time making beautiful assets and designing the game while the studio handles target constraints, conversion, optimization, builds and technical diagnostics.

Source assets are non-destructive: creators keep their high-quality originals while target backends derive optimized representations for each machine.

The project is intentionally platform-neutral. Product frontends such as **AmiStudio** and **AtariStudio** consume RetroStudio through a stable target/backend API rather than placing machine-specific logic in the core.

## Product direction

- Asset-first workflows and a visual Scene Composer.
- Animation, palette and target-preview workspaces.
- Creator-facing quality guidance instead of requiring hardware expertise.
- Automatic target conversion and optimization without modifying source assets.
- Visual workflows for common game creation, with scripting/native extensions available progressively.
- Live resource/quality feedback supplied by target backends.

See `docs/CREATOR_FIRST.md` for the product principles.

## Architecture

```text
AmiStudio -----\
                > RetroStudio Core
AtariStudio ---/
```

RetroStudio owns shared editor/toolchain concepts such as projects, scenes, assets, build graphs, scripting interfaces, preview/runtime abstractions, diagnostics, creator guidance and backend discovery.

Platform frontends/backends own hardware-specific constraints, asset conversion, runtime code, packaging, emulator integration, target profiles and hardware-specific optimization advice.

See `docs/ARCHITECTURE.md`.

## Repository layout

```text
include/retrostudio/   Public C-facing contracts
retrostudio/           Host-side core/editor models
schemas/               Project/schema definitions
examples/              Minimal sample projects
tests/                 Host-side tests
scripts/               Developer utilities
docs/                  Architecture and product/milestone docs
```

## Checks

```sh
make check
```

Host-side checks do not require a target SDK.

## Status

**M0–M3:** implemented.

**M4:** Creator Workspace Foundation in progress.

AmiStudio is the first intended production backend. AtariStudio follows early to verify that the target abstraction remains genuinely platform-neutral.

## License

MIT. See `LICENSE`.
