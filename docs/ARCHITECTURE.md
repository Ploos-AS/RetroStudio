# RetroStudio architecture

## Principle

RetroStudio is the shared, platform-neutral development core. It must not know about Amiga custom chips, Atari Shifter/VIDEL, particular disk-image formats, or specific emulators.

Machine support is supplied through target backends.

## Layers

1. **Project model** — project metadata, scenes, assets, entities and configuration.
2. **Editor services** — commands, diagnostics, undoable operations and future UI-facing models.
3. **Asset pipeline** — target-neutral source assets and conversion requests.
4. **Build graph** — deterministic build steps and artifacts.
5. **Target API** — discovery, capabilities, validation, conversion, compilation, packaging and launch hooks.
6. **Preview API** — host preview contract, deliberately separate from target-accurate execution.

## Target boundary

A backend identifies itself and advertises capabilities. RetroStudio passes a project plus source assets to the backend. The backend may:

- validate target-specific constraints;
- convert graphics/audio/data;
- compile or link target runtime code;
- package executable/disk/cartridge/CD artifacts;
- launch an emulator or physical-device workflow;
- return structured diagnostics and resource-budget information.

The core must never branch on target names such as `amiga` or `atari`.

## Initial products

### AmiStudio

First consumer. Intended targets include A500/OCS, A500+/ECS, A600/ECS, A1200/AGA and CD32. Amiga-specific hardware budgeting and emulator integration belong outside RetroStudio.

### AtariStudio

Second consumer and portability proof. Intended families include ST, STE, TT and Falcon. Atari-specific video, audio, memory and emulator behavior likewise belongs outside RetroStudio.

## Project format

M0 uses a deliberately small JSON manifest. The schema is versioned from day one. Future migrations must be explicit and deterministic.

## Compatibility rule

A backend may depend on RetroStudio. RetroStudio must never depend on a product frontend/backend.

## M0 non-goals

- graphical editor implementation;
- 68k runtime;
- real asset conversion;
- emulator launch;
- game scripting language;
- production schema completeness.

Those are intentionally deferred so the architecture can be tested before implementation weight accumulates.
