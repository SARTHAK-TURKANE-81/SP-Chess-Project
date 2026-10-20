# ♚ Terminal Chess

### A two-player, menu-driven chess game for the terminal, written in Python

---

## Project Information

| | |
|---|---|
| **Project Title** | Terminal Chess (Two-Player Chess Game) |
| **Project Type** | Mini Project (Terminal-Based) |
| **Submitted By** | Sarthak Turkane |
| **PRN** | `2125UIDM1080` |
| **Project Given By** | Prof. Supratim Paul |
| **Language** | Python 3 |
| **Interface** | Terminal only (no GUI, web or database server) |
| **External Libraries** | None (uses only the standard `json` and `os` modules) |
| **Main File** | `chess.py` |

---

## Table of Contents

1. [Overview](#overview)
2. [Objectives](#objectives)
3. [Features](#features)
4. [Concepts Practised](#concepts-practised)
5. [Requirements](#requirements)
6. [How to Run](#how-to-run)
7. [How to Play](#how-to-play)
8. [Sample Screen](#sample-screen)
9. [Program Design](#program-design)
10. [How the Rules Are Checked](#how-the-rules-are-checked)
11. [Data Storage](#data-storage)
12. [Input Validation](#input-validation)
13. [Project Structure](#project-structure)
14. [Known Limitations](#known-limitations)
15. [Future Improvements](#future-improvements)
16. [Acknowledgement](#acknowledgement)

---

## Overview

Terminal Chess is a complete two-player chess game that runs entirely in the terminal using keyboard input.
Two players take turns on the same computer. The program draws the board with Unicode piece icons,
checks that every move follows the rules of chess, and announces check, checkmate and stalemate.
A game can be saved to a file and continued later.

## Objectives

- Build a working terminal game with a menu-driven design
- Apply functions, lists, dictionaries and loops to a real problem
- Handle wrong input without crashing the program
- Save and load data using a plain JSON file
- Keep the code organised, readable and well commented

## Features

| Feature | Description |
|---|---|
| Piece icons | Pieces shown as ♚ ♛ ♜ ♝ ♞ ♟ on a coloured 8x8 board |
| Menu-driven | New Game, Load Game, How to Play, Piece Style toggle, Exit |
| Complete piece movement | Pawn, knight, bishop, rook, queen and king |
| Check detection | Shows `CHECK!` and rejects any move that leaves your own king in check |
| Game-ending conditions | Detects checkmate and stalemate |
| Castling | King side and queen side, with all standard conditions |
| Pawn promotion | Choose queen, rook, bishop or knight |
| Save and load | Stores the game in `chess_save.json` |
| Move hints | `moves e2` lists every legal move of a piece |
| Move history | `history` shows all moves played |
| Resign | A player can give up the game |
| Letter mode | Plain letters instead of icons for terminals without Unicode support |

## Concepts Practised

- Lists and 2D lists (the chessboard)
- Dictionaries (game state, icon mapping)
- Functions and modular code
- Loops and conditionals
- String handling and input parsing
- File handling with JSON
- Exception handling (`try` / `except`)
- Simulation of moves on a copy of the board

## Requirements

- Python 3.8 or newer
- A terminal with colour and Unicode support (Windows Terminal, VS Code terminal, macOS Terminal and most Linux terminals)

## How to Run

1. Download or clone the project.
2. Open a terminal inside the project folder.
3. Run:

```bash
python chess.py
```

On some systems use `python3 chess.py`.

> If the icons look broken (for example in old Windows `cmd`), choose **4. Piece Style** in the main menu to switch to letters.

## How to Play

White moves first. Type the square you are moving **from**, followed by the square you are moving **to**.

### Commands

| Input | Action |
|---|---|
| `e2e4` or `e2 e4` | Move the piece on e2 to e4 |
| `moves e2` | Show all legal moves for the piece on e2 |
| `history` | Show every move played so far |
| `save` | Save the current game |
| `resign` | Current player gives up |
| `menu` | Return to the main menu (asks whether to save) |
| `help` | Show the command list |

### Special moves

- **Castling:** move the king two squares, for example `e1g1` (king side) or `e1c1` (queen side).
- **Promotion:** when a pawn reaches the last row, choose `q`, `r`, `b` or `n`. Pressing Enter gives a queen.

### Board notation

- Columns (files) are the letters `a` to `h`, from left to right.
- Rows (ranks) are the numbers `1` to `8`, from White's side at the bottom.
- White pieces are the white icons; Black pieces are the black icons.
- In letter mode: UPPERCASE letters are White and lowercase letters are Black
  (`K` king, `Q` queen, `R` rook, `B` bishop, `N` knight, `P` pawn).

## Sample Screen

Letter mode is shown below because it works in any text file. In icon mode the same board is drawn with piece icons on coloured squares.

```
===== TERMINAL CHESS =====
1. New Game
2. Load Game
3. How to Play
4. Piece Style: Letters (toggle)
5. Exit
Enter your choice: 1

    a b c d e f g h
8 | r n b q k b n r | 8
7 | p p p p p p p p | 7
6 | . . . . . . . . | 6
5 | . . . . . . . . | 5
4 | . . . . . . . . | 4
3 | . . . . . . . . | 3
2 | P P P P P P P P | 2
1 | R N B Q K B N R | 1
    a b c d e f g h

White to move (help for commands): e2e4
```

Example of a rejected move:

```
White to move (help for commands): e2e5
Illegal move. Try 'moves e2' to see your options.
```

Example of a game ending:

```
CHECKMATE! White wins!
```

## Program Design

The program is written as small functions, each with one job.

| Function | Purpose |
|---|---|
| `new_game()` | Creates the starting game state |
| `save_game(game)` | Writes the game to a JSON file |
| `load_game()` | Reads and validates a saved game |
| `show_board(game)` | Prints the board (icons or letters) |
| `square_name(r, c)` | Converts row and column to a name such as `e4` |
| `parse_square(text)` | Converts a name such as `e4` to row and column |
| `pseudo_moves(...)` | Movement pattern of each piece, ignoring check |
| `attacked(...)` | Tells whether a square is attacked by a colour |
| `in_check(...)` | Tells whether a king is in check |
| `make_move(...)` | Returns a new board after a move (handles castling and promotion) |
| `legal_moves(...)` | Keeps only moves that do not expose the own king; adds castling |
| `all_legal(game)` | Lists every legal move for the side to move |
| `apply_move(...)` | Plays a move on the real game, updates castling rights and history |
| `show_help()` | Prints the command list |
| `play(game)` | Main game loop for one game |
| `main()` | Main menu |

### Game state

The whole game is one dictionary:

| Key | Meaning |
|---|---|
| `board` | 8x8 list of characters; `.` is an empty square |
| `turn` | `"w"` for White or `"b"` for Black |
| `castle` | Remaining castling rights, for example `"KQkq"` |
| `history` | List of moves played, for example `["e2e4", "e7e5"]` |

## How the Rules Are Checked

1. `pseudo_moves` lists where a piece can go according to its movement pattern.
2. `legal_moves` tries each of those moves on a **copy** of the board. If the player's own king is attacked afterwards, the move is discarded.
3. If the side to move has **no legal moves**:
   - king in check: **checkmate**
   - king not in check: **stalemate** (draw)
4. Castling is allowed only when:
   - the king and the rook have not moved before
   - the squares between them are empty
   - the king is not in check
   - the king does not pass through or land on an attacked square

## Data Storage

Saved games are stored in a plain JSON file named `chess_save.json`. No database is used.

```json
{
  "board": [["r","n","b","q","k","b","n","r"], "... 8 rows in total ..."],
  "turn": "w",
  "castle": "KQkq",
  "history": ["e2e4", "e7e5"]
}
```

- The file is created when the player uses `save` or chooses to save on leaving.
- The file is deleted when a game finishes (checkmate or stalemate).
- A missing or damaged save file is handled with a message, not a crash.

## Input Validation

| Situation | Result |
|---|---|
| Letters or wrong number in the menu | "Please enter a number from 1 to 5." |
| Invalid move format (for example `hello`) | "Invalid input. Type a move like e2e4, or 'help'." |
| Move that breaks the rules | "Illegal move. Try 'moves e2' to see your options." |
| Moving the opponent's piece or an empty square | Rejected as an illegal move |
| Invalid promotion choice | Asked again until `q`, `r`, `b` or `n` is given |
| No save file or damaged save file | Message shown and the menu continues |
| Ctrl+C or end of input | Program exits cleanly |

## Project Structure

```
chess-project/
├── chess.py        # the complete game (single file)
├── README.md       # project documentation (this file)
├── .gitignore      # ignores the save file and Python cache
└── docs/           # extra screenshots and demo of the game
```

## Known Limitations

- En passant is not implemented
- No draw by repetition, 50-move rule or insufficient material
- Two human players only (no computer opponent)

## Future Improvements

- Computer opponent that plays a random legal move, then a smarter one
- En passant and automatic draw rules
- Captured pieces list and move numbers
- Undo last move
- Game timer for each player

## Acknowledgement

This project was developed as a mini project assignment given by **Prof. Supratim Paul**.

**Developed by:** Sarthak Turkane
