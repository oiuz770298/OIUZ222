# Chaos Card Chess

A strategy game based on traditional Chess, but with randomized openings controlled by cards.

## How It Works

At the start of every match, a random **Chaos Card** (1–8) is drawn. Each number corresponds to one of the eight pawns:

| Card | Required First Pawn |
|------|-------------------|
| 1    | a-pawn            |
| 2    | b-pawn            |
| 3    | c-pawn            |
| 4    | d-pawn            |
| 5    | e-pawn            |
| 6    | f-pawn            |
| 7    | g-pawn            |
| 8    | h-pawn            |

The player **must** move that pawn first before normal chess rules continue.

### Example

If the card is **5**, the e-pawn must move first. Valid moves would be `e3` or `e4`.

After the forced opening move, the game becomes **standard chess**.

## Features

- Visual chess board with piece graphics
- Mouse controls for piece selection and movement
- Turn-based gameplay
- Basic AI opponent
- Randomized openings every match
- Legal move highlighting
- Game state detection (check, checkmate, stalemate)

## Purpose

The game aims to:

- Reduce repetitive openings
- Encourage creativity
- Make players adapt instead of memorizing theory

## Tech Stack

- **Python 3**
- **Pygame** for graphics
- **python-chess** for move logic

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python chaos_card_chess.py
```

## Controls

- **Click** a piece to select it
- **Click** a highlighted square to move
- **Click** elsewhere to deselect
- Press **R** to restart with a new Chaos Card
- Press **Q** or close the window to quit

## Future Plans

- Stronger AI with Stockfish integration
- Online multiplayer
- Special ability cards
- Ranked matchmaking
- Animations and sounds
- Steam support
