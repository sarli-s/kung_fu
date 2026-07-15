# Kung Fu Chess

A command-driven chess engine written in Python.

> 🚧 Work in progress

This project explores chess movement, captures, promotions, and command-based gameplay in a modular Python structure.

## Project Structure

- main.py — entry point
- chess/
  - core/ — GameEngine and session management
  - entities/ — Board, pieces, and piece factory
  - rules/ — ChessBoardRules and game logic
  - config/ — ChessConfig and constants
- tests/ — unit tests
- assets/ — fonts, images, and sounds

## Features

- **GameEngine** — Core engine managing board state, piece movement, and game logic
- **Movement System** — Request-based movement with duration-based execution
- **Jump Mechanics** — Airborne state management for pieces
- **Captures** — Automatic enemy piece capture with event emission
- **Pawn Promotion** — Automatic promotion to Queen upon reaching the opposite end
- **Event System** — Subscribe to game events (on_capture, on_promotion, on_game_over)
- **Game Over Detection** — Automatic detection when a King is captured

## Run the Tests

```bash
python -m pytest tests/
```

## GitHub

https://github.com/sarli-s/kung_fu

