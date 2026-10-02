# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Analyze uploaded images with configurable Ollama or OpenAI-compatible vision models, preserving the original blob while storing descriptions, detected features, and extracted text for semantic search.
- Add automatic Markdown and JSON content drafting in the New Content modal via a configurable local or remote LLM.
- Make the Docker API container able to reach a locally hosted Ollama instance.
- Add a Settings tab to spaces with a confirmed option to permanently delete the space and its content.
- Add contributor setup, testing, pull-request, and changelog guidance.

### Changed

- Use official project logo on the frontend.

## [0.1.0] - 2026-10-01

### Added

- Initial release.

[Unreleased]: https://github.com/Ponup/app/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ponup/app/releases/tag/v0.1.0
