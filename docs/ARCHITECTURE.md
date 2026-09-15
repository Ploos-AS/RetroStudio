# RetroStudio architecture

## Principle

RetroStudio is the shared, platform-neutral and frontend-independent development core. It must not know about Amiga custom chips, Atari Shifter/VIDEL, particular disk-image formats, specific emulators, or assumptions belonging to one authoring editor.

Machine support is supplied through target backends. Authoring experiences are supplied through frontends.

The architectural goal is:

> one project model, one toolchain, multiple editors, multiple retro targets.

## Frontends

RetroStudio has two intended first-class authoring paths.

### RetroStudio Native Editor

The native Linux editor is the purpose-built creator experience. It prioritizes visual game creation, asset workflows, scenes, animation, tile maps, collisions, events/behaviours, target preview and understandable hardware-budget guidance.

The editor is a client of RetroStudio core services. Core project semantics must not be hidden inside GUI code.

### Godot integration

A Godot 4 addon/integration provides an alternative authoring frontend for creators who prefer Godot. It maps the supported subset of Godot scenes/resources into canonical RetroStudio data and invokes the normal RetroStudio toolchain for validation and builds.

Godot is an authoring environment, not the retro target runtime. Exported games do not require the Godot engine on the target machine.

A permanent Godot fork is deliberately deferred. It should only be evaluated if addon/integration APIs later prove to be a material architectural limitation.

## Canonical authoring boundary

Neither frontend owns the target-independent game definition. Canonical RetroStudio project data / IR is the interchange boundary.

```text
                 +----------------------+
                 | Godot 4 + addon      |
                 +----------+-----------+
                            |
                            v
+--------------------+   RetroStudio   +----------------------+
| Native Editor      |<-> Project / IR <-> Headless CLI      |
+--------------------+        |        +----------------------+
                              v
                       Core / Toolchain
                              |
                    Target Backend API
                       /             \
                  AmiStudio       AtariStudio
```

Frontend-specific information may exist, but portable game semantics must have explicit canonical representations. If data cannot round-trip between frontends, that limitation must be detected and reported rather than silently discarded.

## Layers

1. **Project model / IR** — versioned project metadata, scenes, assets, entities, components, behaviours/events, animation and portable configuration.
2. **Frontend contract** — stable operations for loading, modifying, validating and exchanging canonical project data.
3. **Editor services** — commands, diagnostics, selection/workspace models and undoable operations usable by the native editor and other clients.
4. **Asset pipeline** — target-neutral, non-destructive source assets and conversion requests.
5. **Build graph** — deterministic build steps and artifacts, independent of the authoring frontend.
6. **Target API** — discovery, capabilities, validation, conversion, compilation, packaging and launch hooks.
7. **Preview API** — host preview contract, deliberately separate from target-accurate execution.

## Headless rule

Every production build must be possible without launching either the Native Editor or Godot. The CLI/core pipeline is authoritative for validation and target builds. This makes CI, reproducible releases and frontend equivalence practical.

Conceptually:

```text
retrostudio validate <project>
retrostudio build <project> --target <profile>
retrostudio run <project> --target <profile>
```

Exact CLI syntax may evolve while the contracts are being formalized.

## Target profiles

A target backend may expose multiple concrete hardware profiles rather than one broad platform name. Examples include A500/OCS versus A1200/AGA, or ST versus STE versus Falcon.

Profiles can supply limits and guidance for memory, palettes, graphics modes, sprites/objects, audio, storage and estimated runtime budgets. Frontends present this information to creators; the core does not encode machine-specific constants.

## Target boundary

A backend identifies itself and advertises capabilities. RetroStudio passes canonical project data plus source assets to the backend. The backend may:

- validate target-specific constraints;
- convert graphics/audio/data;
- compile or link target runtime code;
- package executable/disk/cartridge/CD artifacts;
- launch an emulator or physical-device workflow;
- return structured diagnostics and resource-budget information.

The core must never branch on target names such as `amiga` or `atari`.

## Initial products

### AmiStudio

First production consumer/backend. Intended targets include A500/OCS, A500+/ECS, A600/ECS, A1200/AGA and CD32. Amiga-specific hardware budgeting and emulator integration belong outside RetroStudio.

Existing Godot2Amiga experience can inform this integration, but RetroStudio's canonical contracts must not become Amiga- or Godot-specific.

### AtariStudio

Second consumer/backend and portability proof. Intended families include ST, STE, TT and Falcon. Atari-specific video, audio, memory and emulator behavior likewise belongs outside RetroStudio.

Supporting a second architecture early is intentionally used to expose accidental Amiga assumptions.

## Future target families

Additional targets such as DOS, Mega Drive, SNES and selected 8-bit platforms may be added after the first two backends prove the contracts. Sharing an editor does not imply sharing target runtimes; each backend remains free to generate the most appropriate native implementation for its hardware.

## Project format and IR

M0 began with a deliberately small JSON manifest and a versioned schema. As RetroStudio grows, this evolves into a canonical frontend-neutral authoring model/IR.

Important properties are:

- explicit schema/version migrations;
- deterministic serialization and stable IDs;
- non-destructive references to source assets;
- portable scene/gameplay semantics;
- explicit frontend-extension data where necessary;
- no generated target artifacts treated as source truth.

The IR is an authoring/build interchange representation, not a requirement that every target use the same runtime representation.

## Compatibility rules

- A target backend may depend on RetroStudio; RetroStudio must never depend on a product target backend.
- A frontend may depend on RetroStudio; RetroStudio core semantics must never depend on Godot or the native GUI toolkit.
- Target-specific constraints belong in backends and target profiles.
- Frontend-specific extensions must not silently alter portable semantics.
- Production builds must remain available headlessly.

## Creator-first consequence

Architecture exists to support the creator workflow rather than expose old hardware complexity. A creator should be able to choose a target profile and receive actionable guidance such as memory, palette or scene-budget pressure while keeping high-quality source assets intact. Expert users can progressively access scripting/native extensions without making those mechanisms prerequisites for ordinary game creation.
