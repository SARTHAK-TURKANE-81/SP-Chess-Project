"""
Terminal Chess - two players, one keyboard.
Features: legal move checking, check / checkmate / stalemate, castling,
pawn promotion, save & load (JSON), menu-driven interface, piece icons.
Internally uppercase letters = White, lowercase letters = Black.
"""

import json
import os

SAVE_FILE = "chess_save.json"

START_BOARD = [
    "rnbqkbnr",
    "pppppppp",
    "........",
    "........",
    "........",
    "........",
    "PPPPPPPP",
    "RNBQKBNR",
]

KNIGHT = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
KING = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ROOK = [(-1, 0), (1, 0), (0, -1), (0, 1)]
BISHOP = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# Unicode chess icons (the same solid glyph is used for both sides;
# the colour of the icon tells White from Black).
ICONS = {"k": "\u265a", "q": "\u265b", "r": "\u265c",
         "b": "\u265d", "n": "\u265e", "p": "\u265f\ufe0e"}
LIGHT_SQ, DARK_SQ = 137, 94          # 256-colour codes for board squares
WHITE_PIECE, BLACK_PIECE = 231, 16   # 256-colour codes for the pieces
settings = {"icons": True}           # False = plain letters (old terminals)

# Squares that remove castling rights when a piece moves from / to them
RIGHTS_LOST = {(7, 4): "KQ", (0, 4): "kq", (7, 7): "K", (7, 0): "Q",
               (0, 7): "k", (0, 0): "q"}


# ---------------------------------------------------------------- game state
def new_game():
    """Return a fresh game dictionary."""
    return {"board": [list(row) for row in START_BOARD],
            "turn": "w", "castle": "KQkq", "history": []}


def save_game(game):
    """Write the game to a JSON file."""
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(game, f)
        print("Game saved to", SAVE_FILE)
    except OSError:
        print("Could not save the game.")


def load_game():
    """Read a game from the JSON file; return None if not possible."""
    if not os.path.exists(SAVE_FILE):
        print("No saved game found.")
        return None
    try:
        with open(SAVE_FILE) as f:
            game = json.load(f)
        if len(game["board"]) != 8 or game["turn"] not in ("w", "b"):
            raise ValueError
        return game
    except (OSError, ValueError, KeyError):
        print("Save file is damaged.")
        return None


# ------------------------------------------------------------------- display
def show_board(game):
    """Print the board with coordinates (icons on coloured squares, or
    plain letters when icons are switched off)."""
    board = game["board"]
    print("\n     a  b  c  d  e  f  g  h" if settings["icons"]
          else "\n    a b c d e f g h")
    for r in range(8):
        if settings["icons"]:
            cells = ""
            for c in range(8):
                p = board[r][c]
                bg = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                fg = WHITE_PIECE if p.isupper() else BLACK_PIECE
                glyph = " " if p == "." else ICONS[p.lower()]
                cells += f"\033[48;5;{bg}m\033[38;5;{fg}m {glyph} \033[0m"
            print(f" {8 - r} {cells} {8 - r}")
        else:
            print(f"{8 - r} | {' '.join(board[r])} | {8 - r}")
    print("     a  b  c  d  e  f  g  h\n" if settings["icons"]
          else "    a b c d e f g h\n")


def square_name(r, c):
    return "abcdefgh"[c] + str(8 - r)


def parse_square(text):
    """'e2' -> (row, col), or None if invalid."""
    if len(text) == 2 and text[0] in "abcdefgh" and text[1] in "12345678":
        return 8 - int(text[1]), "abcdefgh".index(text[0])
    return None


# --------------------------------------------------------------- move rules
def on_board(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def colour(piece):
    return "w" if piece.isupper() else "b"


def pseudo_moves(board, r, c, attacks_only=False):
    """Squares a piece can reach ignoring check. attacks_only is used to
    find which squares a piece attacks (pawns attack diagonally only)."""
    p = board[r][c]
    me, kind, out = colour(p), p.lower(), []

    def enemy(x):
        return x != "." and colour(x) != me

    if kind == "p":
        d = -1 if me == "w" else 1
        for dc in (-1, 1):
            r2, c2 = r + d, c + dc
            if on_board(r2, c2) and (attacks_only or enemy(board[r2][c2])):
                out.append((r2, c2))
        if not attacks_only and on_board(r + d, c) and board[r + d][c] == ".":
            out.append((r + d, c))
            start = 6 if me == "w" else 1
            if r == start and board[r + 2 * d][c] == ".":
                out.append((r + 2 * d, c))
    elif kind in "nk":
        for dr, dc in (KNIGHT if kind == "n" else KING):
            r2, c2 = r + dr, c + dc
            if on_board(r2, c2) and (board[r2][c2] == "." or enemy(board[r2][c2])):
                out.append((r2, c2))
    else:  # sliding pieces: rook, bishop, queen
        dirs = ROOK if kind == "r" else BISHOP if kind == "b" else ROOK + BISHOP
        for dr, dc in dirs:
            r2, c2 = r + dr, c + dc
            while on_board(r2, c2):
                if board[r2][c2] == ".":
                    out.append((r2, c2))
                else:
                    if enemy(board[r2][c2]):
                        out.append((r2, c2))
                    break
                r2, c2 = r2 + dr, c2 + dc
    return out


def attacked(board, r, c, by):
    """Is square (r, c) attacked by any piece of colour `by`?"""
    for i in range(8):
        for j in range(8):
            if board[i][j] != "." and colour(board[i][j]) == by:
                if (r, c) in pseudo_moves(board, i, j, True):
                    return True
    return False


def in_check(board, me):
    """Is the king of colour `me` in check?"""
    king = "K" if me == "w" else "k"
    for i in range(8):
        for j in range(8):
            if board[i][j] == king:
                return attacked(board, i, j, "b" if me == "w" else "w")
    return False


def make_move(board, r1, c1, r2, c2, promo="q"):
    """Return a NEW board after the move (handles castling & promotion)."""
    b = [row[:] for row in board]
    p = b[r1][c1]
    b[r2][c2], b[r1][c1] = p, "."
    if p.lower() == "k" and abs(c2 - c1) == 2:       # castling: move the rook
        if c2 > c1:
            b[r1][5], b[r1][7] = b[r1][7], "."
        else:
            b[r1][3], b[r1][0] = b[r1][0], "."
    if p.lower() == "p" and r2 in (0, 7):            # promotion
        b[r2][c2] = promo.upper() if p.isupper() else promo.lower()
    return b


def legal_moves(game, r, c):
    """Moves for the piece on (r, c) that do not leave own king in check."""
    board, p = game["board"], game["board"][r][c]
    me = colour(p)
    result = [(r2, c2) for r2, c2 in pseudo_moves(board, r, c)
              if not in_check(make_move(board, r, c, r2, c2), me)]
    row = 7 if me == "w" else 0
    if p.lower() == "k" and (r, c) == (row, 4) and not in_check(board, me):
        opp = "b" if me == "w" else "w"
        k, q = ("K", "Q") if me == "w" else ("k", "q")
        rights, line = game["castle"], board[row]
        if (k in rights and line[5] == line[6] == "."
                and not attacked(board, row, 5, opp)
                and not attacked(board, row, 6, opp)):
            result.append((row, 6))
        if (q in rights and line[1] == line[2] == line[3] == "."
                and not attacked(board, row, 3, opp)
                and not attacked(board, row, 2, opp)):
            result.append((row, 2))
    return result


def all_legal(game):
    """Every legal move for the side to move: list of (r1, c1, r2, c2)."""
    moves = []
    for r in range(8):
        for c in range(8):
            p = game["board"][r][c]
            if p != "." and colour(p) == game["turn"]:
                moves += [(r, c, r2, c2) for r2, c2 in legal_moves(game, r, c)]
    return moves


def apply_move(game, r1, c1, r2, c2):
    """Play a legal move on the real game (asks for promotion piece)."""
    p = game["board"][r1][c1]
    promo = "q"
    if p.lower() == "p" and r2 in (0, 7):
        while True:
            promo = input("Promote to (q/r/b/n) [q]: ").strip().lower() or "q"
            if promo in ("q", "r", "b", "n"):
                break
            print("Please type q, r, b or n.")
    for sq in ((r1, c1), (r2, c2)):                   # update castling rights
        for ch in RIGHTS_LOST.get(sq, ""):
            game["castle"] = game["castle"].replace(ch, "")
    game["board"] = make_move(game["board"], r1, c1, r2, c2, promo)
    game["history"].append(square_name(r1, c1) + square_name(r2, c2))
    game["turn"] = "b" if game["turn"] == "w" else "w"


# ------------------------------------------------------------------ gameplay
def show_help():
    print("""
Commands while playing:
  e2e4 (or e2 e4)  move the piece from e2 to e4
  moves e2         show legal moves for the piece on e2
  history          show all moves played so far
  save             save the game
  resign           give up (the other player wins)
  menu             go back to the main menu
White pieces are the light icons, Black pieces are the dark icons.
Castle by moving the king two squares (e.g. e1g1).
In letter mode: UPPERCASE = White, lowercase = Black.
""")


def play(game):
    """Main game loop. Returns when the game ends or player leaves."""
    names = {"w": "White", "b": "Black"}
    while True:
        show_board(game)
        me = game["turn"]
        moves = all_legal(game)
        check = in_check(game["board"], me)
        if not moves:
            if check:
                print(f"CHECKMATE! {names['b' if me == 'w' else 'w']} wins!")
            else:
                print("STALEMATE! The game is a draw.")
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            return
        if check:
            print("CHECK!")
        cmd = input(f"{names[me]} to move (help for commands): ").strip().lower()

        if cmd == "help":
            show_help()
        elif cmd == "menu":
            if input("Save before leaving? (y/n): ").strip().lower() == "y":
                save_game(game)
            return
        elif cmd == "save":
            save_game(game)
        elif cmd == "history":
            print(" ".join(game["history"]) or "No moves yet.")
        elif cmd == "resign":
            print(f"{names[me]} resigns. {names['b' if me == 'w' else 'w']} wins!")
            return
        elif cmd.startswith("moves"):
            sq = parse_square(cmd[5:].strip())
            if sq is None:
                print("Usage: moves e2")
                continue
            targets = [square_name(r2, c2) for (r1, c1, r2, c2) in moves
                       if (r1, c1) == sq]
            print("Legal moves:", ", ".join(targets) if targets else "none")
        else:
            text = cmd.replace(" ", "")
            src = parse_square(text[:2])
            dst = parse_square(text[2:])
            if len(text) != 4 or src is None or dst is None:
                print("Invalid input. Type a move like e2e4, or 'help'.")
            elif (*src, *dst) not in moves:
                print("Illegal move. Try 'moves e2' to see your options.")
            else:
                apply_move(game, *src, *dst)


def main():
    """Menu-driven entry point."""
    os.system("")   # lets Windows terminals show colours
    while True:
        print("\n===== TERMINAL CHESS =====")
        print("1. New Game\n2. Load Game\n3. How to Play")
        print("4. Piece Style:", "Icons" if settings["icons"] else "Letters",
              "(toggle)\n5. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            play(new_game())
        elif choice == "2":
            game = load_game()
            if game:
                play(game)
        elif choice == "3":
            show_help()
        elif choice == "4":
            settings["icons"] = not settings["icons"]
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please enter a number from 1 to 5.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
