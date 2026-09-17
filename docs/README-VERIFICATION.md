# InfoPulse PL README verification notes

This file records the evidence used for the SWIR README PRO v2 migration. It is not a product roadmap and does not change application behavior.

## Evidence reviewed

- `InfoPulse_PL.py`: current Python desktop source, local `infopulse_config.json` path handling, public RSS/API modules and keyboard/input automation dependencies.
- `requirements.txt`: requests, CustomTkinter, PyAutoGUI, Pyperclip, keyboard and pynput dependencies.
- `.github/workflows/release.yml`: Python 3.11 validation, PyInstaller Windows EXE build, ZIP/checksum packaging and release publication.
- `.github/workflows/assemble-source.yml`: source assembly/checksum/compile workflow driven only by `parts/READY` changes.
- GitHub release metadata: public `v3.2.0` with Windows x64 ZIP, SHA-256 sidecar and `InfoPulse-PL.exe`, published September 12, 2026.
- Open pull requests: none existed before this migration branch was created.

## Documentation decisions

- The main README is now English for repository-wide consistency while clearly stating that the application interface is Polish.
- Product readiness is **N/A** because there is no canonical measurable roadmap. The existence of release `v3.2.0` is tracked separately.
- External feeds/APIs are documented as network dependencies that can change or fail; no availability guarantee is made.
- AutoChat/input automation is documented conservatively: the user must choose and verify the intended destination and must not use it for spam/flooding or unwanted messages.
- No `LICENSE` file exists in the current tree, so no licensing terms are inferred.

## Verification scope

The migration changes only README/documentation artwork and deterministic documentation tooling. It does not change Python source, dependencies, external endpoints, input automation, build workflows, release assets, tags or licensing.

The existing workflows are not general pull-request documentation checks: the release workflow is tag/manual/workflow-file driven and the source-assembly workflow is `parts/READY` driven. A documentation-only PR may therefore have no GitHub Actions run. Documentation validation consists of read-back of branch/default-branch files, v2/Search Keywords and relative-link checks, consistent N/A progress data, valid self-contained SVG structure, and `tools/generate_readme_progress.py --check` when a local checkout is available.

No live third-party API sweep, Windows GUI session, keyboard-injection test or published EXE runtime test is claimed by this documentation migration.
