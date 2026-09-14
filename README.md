# RetroStudio

RetroStudio is an open-source, Linux-first development core for building games for classic 16/32-bit systems.

The project is intentionally platform-neutral. Product frontends such as **AmiStudio** and **AtariStudio** consume RetroStudio through a stable target/backend API rather than placing machine-specific logic in the core.

## M0 goals

- Define the project architecture and target boundary.
- Establish a minimal project manifest format.
- Provide a tiny host-side validation/smoke-test path.
- Document the roadmap and contribution rules.
- Keep the core free of Amiga-, Atari-, or emulator-specific assumptions.

## Architecture

```text
AmiStudio -----\
                > RetroStudio Core
AtariStudio ---/
```

RetroStudio owns shared editor/toolchain concepts such as projects, scenes, assets, build graphs, scripting interfaces, preview/runtime abstractions, diagnostics, and backend discovery.

Platform frontends/backends own hardware-specific constraints, asset conversion, runtime code, packaging, emulator integration, and target profiles.

See `docs/ARCHITECTURE.md`.

## Repository layout

```text
include/retrostudio/   Public C-facing contracts
src/                   Core implementation
schemas/               Project/schema definitions
examples/              Minimal sample projects
tests/                 Host-side tests
scripts/               Developer utilities
docs/                  Architecture and milestone docs
```

## M0 smoke test

```sh
make check
```

This validates the sample project manifest and core repository invariants. No target SDK is required for M0.

## Status

**M0 — Foundation:** implemented.

The first intended consumer/backend is AmiStudio. AtariStudio should follow early enough to verify that the target abstraction is genuinely platform-neutral.

## License

MIT. See `LICENSE`.
