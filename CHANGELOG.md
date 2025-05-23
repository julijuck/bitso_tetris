# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2] - 2025-05-20

### Added
- Smooth entry animation for each new piece.
- Support for vertical pixel offset in `draw_piece` to allow animation.
- Visual feedback on line clears (white flash effect).
- Handling for repeated key presses after locking a piece.
- Time tracking displayed in MM:SS format.
- Compliance with PEP 8: line length limited to 79 characters.

### Fixed
- Bug where pieces were falling too fast by default.
- Bug where holding the DOWN key blocked the next piece from falling.
- Corrected spacing and alignment of game UI elements (Score, Level, etc.).

### Improved
- Better alignment of UI components in the info panel.
- Refactored several functions for readability and separation of concerns.
- Updated `reset_piece` to manage fall timer and animation more precisely.
