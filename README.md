# Kung Fu Chess

A command-driven chess engine written in Python.

> 🚧 Work in progress

## Project Structure

```
kung fu/
├── main.py              # Entry point
├── play/
│   ├── config.py        # Game configuration (cell size, piece tokens, etc.)
│   ├── core/
│   │   ├── parser.py    # Parses board layout and commands from stdin
│   │   └── commands.py  # Handles click, wait, jump, print board commands
│   ├── entities/
│   │   ├── board.py     # Board state and movement logic
│   │   ├── pieces.py    # Piece types and movement rules
│   │   ├── move.py      # Move data structure
│   │   ├── rules.py     # Game rules
│   │   └── game_commands.py
│   └── utils/
│       ├── event_emitter.py
│       └── token_format.py
├── tests/               # Unit tests
└── assets/              # Fonts, images, sounds
```

## How to Run

Input is read from stdin. The format is:

1. Board rows (using piece tokens like `wK`, `bQ`, `.` for empty)
2. A blank line
3. Commands (`click x y`, `wait ms`, `jump x y`, `print board`)

```bash
python main.py < input.txt
```

## Piece Tokens

| Token | Piece         |
|-------|---------------|
| `wK`  | White King    |
| `bK`  | Black King    |
| `wQ`  | White Queen   |
| `bQ`  | Black Queen   |
| `wR`  | White Rook    |
| `bR`  | Black Rook    |
| `wB`  | White Bishop  |
| `bB`  | Black Bishop  |
| `wN`  | White Knight  |
| `bN`  | Black Knight  |
| `wP`  | White Pawn    |
| `bP`  | Black Pawn    |
| `.`   | Empty cell    |

## Running Tests

```bash
python -m pytest tests/
```

## GitHub

https://github.com/sarli-s/kung_fu
