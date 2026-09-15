# RetroStudio

RetroStudio is an open-source, Linux-first **creator-first game studio and toolchain** for building high-quality games for classic systems.

The primary users are creators, pixel artists, animators, level designers, musicians and asset makers. RetroStudio should let them spend most of their time making beautiful assets and designing the game while the studio handles target constraints, conversion, optimization, builds and technical diagnostics.

Source assets are non-destructive: creators keep their high-quality originals while target backends derive optimized representations for each machine.

RetroStudio is intentionally both **frontend-independent** and **platform-neutral**. It provides one canonical project/IR, asset pipeline, compiler/toolchain and target API. Creators can use the purpose-built RetroStudio Native Editor or a supported external authoring frontend such as Godot. Product frontends/backends such as **AmiStudio** and **AtariStudio** supply machine-specific support without placing hardware assumptions in the core.

## Product direction

- Purpose-built RetroStudio Native Editor for retro creators.
- First-class Godot 4 addon/integration using the same RetroStudio core and build pipeline.
- Canonical frontend-neutral RetroStudio project/IR.
- Asset-first workflows and a visual Scene Composer.
- Animation, palette and target-preview workspaces.
- Creator-facing quality guidance instead of requiring hardware expertise.
- Automatic target conversion and optimization without modifying source assets.
- Visual workflows for common game creation, with scripting/native extensions available progressively.
- Live resource/quality feedback supplied by target backends.
- Headless CLI builds independent of any editor.
- No Godot runtime requirement on retro targets.

A permanent Godot fork is not a near-term goal. RetroStudio will first use Godot's addon/integration interfaces. A dedicated Godot-derived distribution should only be considered later if those interfaces materially prevent the desired creator experience.

See `docs/CREATOR_FIRST.md` for the product principles.

## Architecture

```text
        Godot 4 + RetroStudio addon
                   |
                   v
RetroStudio Native Editor ---> Canonical RetroStudio Project / IR
                               |
                               v
                    RetroStudio Core / Toolchain
                               |
                 +-------------+-------------+
                 |                           |
             AmiStudio                  AtariStudio
           target backend              target backend
```

Both authoring frontends use the same core semantics. RetroStudio owns shared concepts such as projects, scenes, assets, behaviours/events, build graphs, scripting interfaces, preview/runtime abstractions, diagnostics, creator guidance and backend discovery.

Platform frontends/backends own hardware-specific constraints, asset conversion, runtime code, packaging, emulator integration, target profiles and hardware-specific optimization advice.

The intended rule is simple: **edit anywhere supported, build through RetroStudio**.

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

The repository will grow explicit frontend/IR integration boundaries as the native editor and Godot integration mature.

## Checks

```sh
make check
```

Host-side checks do not require a target SDK.

## Status

**M0–M4:** implemented foundation and creator workspace.

**M5:** Visual Game Creation in progress.

AmiStudio is the first intended production backend. AtariStudio follows early to verify that the target abstraction remains genuinely platform-neutral. Later milestones formalize the canonical frontend IR, Godot integration, Native Editor conformance and multi-frontend interoperability.

## License

MIT. See `LICENSE`.
