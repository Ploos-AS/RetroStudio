# Creator-first product principles

RetroStudio is a game studio for creators, artists and asset makers targeting classic hardware. Its purpose is to let creators spend most of their time making beautiful art, animation, levels, music and game design while the toolchain handles hardware constraints.

## Product promise

A creator should be able to import high-quality source assets, compose a scene visually, choose a target and receive a useful preview plus actionable optimization guidance without first learning planar graphics, memory maps or target-specific build systems.

## Principles

1. **Assets first.** Images, sprite sheets, tiles, palettes, animation, audio and music are first-class project material.
2. **Non-destructive sources.** Original high-quality assets are preserved. Target-specific derivatives belong to the build/cache pipeline.
3. **Beautiful by default.** Conversion should seek the best visual/audio result that fits the selected target, not merely the easiest conversion.
4. **Visual composition first.** Scene composition, animation, collision, layers and common behaviours should not require source code.
5. **Hardware expertise in the tool.** The UI explains constraints in creator language and offers concrete remedies.
6. **Live target awareness.** Creators can inspect how the same source material maps to different target profiles without modifying the originals.
7. **Progressive complexity.** No-code workflows are the default; scripting and native extensions remain available for advanced projects.
8. **Backend ownership.** RetroStudio presents generic capabilities and diagnostics. AmiStudio, AtariStudio and future backends own hardware-specific conversion and advice.

## Creator workspace

The editor is organized around workflows rather than engine internals:

- Project Browser
- Asset Library
- Scene Composer
- Inspector
- Animation Workspace
- Target Preview
- Quality & Budget panel

A later Visual Game Creation milestone will add reusable behaviours and event workflows for common game mechanics.

## Diagnostic UX

Raw diagnostics remain stable and machine-readable, but the editor may attach creator-facing guidance. For example, a backend can report a palette or memory limit while the editor presents suggested actions such as reducing a layer's color budget, enabling tile reuse or moving an asset to another target-specific strategy.

The editor must never silently destroy or overwrite source assets while applying these suggestions.
