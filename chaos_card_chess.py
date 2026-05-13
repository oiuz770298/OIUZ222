"""Chaos Card Chess - A chess variant with randomized openings."""

import random
import sys

import chess
import pygame

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
CARD_PANEL_WIDTH = 220
WINDOW_WIDTH = BOARD_SIZE + CARD_PANEL_WIDTH + 60
WINDOW_HEIGHT = BOARD_SIZE + 100
BOARD_OFFSET_X = 30
BOARD_OFFSET_Y = 60
CARD_PANEL_X = BOARD_OFFSET_X + BOARD_SIZE + 20

FPS = 60

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_SELECTED = (186, 202, 68, 180)
HIGHLIGHT_MOVE = (130, 170, 100, 160)
HIGHLIGHT_CAPTURE = (200, 80, 80, 160)
HIGHLIGHT_CHECK = (255, 50, 50, 120)
HIGHLIGHT_LAST_MOVE = (205, 210, 106, 100)
CARD_BG = (30, 30, 60)
CARD_BORDER = (180, 160, 120)
CARD_FACE = (250, 245, 230)
CARD_RED = (180, 30, 30)
CARD_ACCENT = (255, 200, 60)
CARD_TEXT = (255, 255, 255)
STATUS_BG = (40, 40, 40)
INFO_PANEL_BG = (35, 35, 50)
OVERLAY_BG = (0, 0, 0, 180)

PAWN_FILES = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"}

# Unicode chess pieces
PIECE_UNICODE = {
    "K": "\u2654", "Q": "\u2655", "R": "\u2656", "B": "\u2657", "N": "\u2658", "P": "\u2659",
    "k": "\u265A", "q": "\u265B", "r": "\u265C", "b": "\u265D", "n": "\u265E", "p": "\u265F",
}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# Piece-square tables for positional evaluation (from White's perspective)
PST_PAWN = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

PST_KNIGHT = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

PST_BISHOP = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

PST_ROOK = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

PST_QUEEN = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

PST_KING_MIDDLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

PST = {
    chess.PAWN: PST_PAWN,
    chess.KNIGHT: PST_KNIGHT,
    chess.BISHOP: PST_BISHOP,
    chess.ROOK: PST_ROOK,
    chess.QUEEN: PST_QUEEN,
    chess.KING: PST_KING_MIDDLE,
}


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

def evaluate_board(board: chess.Board) -> float:
    """Evaluate the board position. Positive = good for White."""
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        value = PIECE_VALUES.get(piece.piece_type, 0)
        pst = PST.get(piece.piece_type)
        if pst:
            idx = sq if piece.color == chess.WHITE else chess.square_mirror(sq)
            value += pst[63 - idx]
        score += value if piece.color == chess.WHITE else -value
    return score


def order_moves(board: chess.Board):
    """Order moves: captures first (MVV-LVA), then non-captures."""
    moves = list(board.legal_moves)

    def move_score(m: chess.Move) -> int:
        s = 0
        if board.is_capture(m):
            captured = board.piece_at(m.to_square)
            mover = board.piece_at(m.from_square)
            if captured and mover:
                s += 10 * PIECE_VALUES.get(captured.piece_type, 0) - PIECE_VALUES.get(mover.piece_type, 0)
            else:
                s += 500
        if m.promotion:
            s += PIECE_VALUES.get(m.promotion, 0)
        return s

    moves.sort(key=move_score, reverse=True)
    return moves


def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximising: bool) -> float:
    """Alpha-beta minimax search."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximising:
        max_eval = -float("inf")
        for move in order_moves(board):
            board.push(move)
            val = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in order_moves(board):
            board.push(move)
            val = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval


def ai_choose_move(board: chess.Board, forced_file: str | None = None, depth: int = 3) -> chess.Move | None:
    """Pick the best move for the current side. If *forced_file* is set, only
    consider pawn moves from that file."""
    legal = list(board.legal_moves)
    if not legal:
        return None

    if forced_file is not None:
        file_idx = ord(forced_file) - ord("a")
        restricted = [
            m for m in legal
            if chess.square_file(m.from_square) == file_idx
            and board.piece_at(m.from_square) is not None
            and board.piece_at(m.from_square).piece_type == chess.PAWN
        ]
        if restricted:
            legal = restricted

    maximising = board.turn == chess.WHITE
    best_move = legal[0]
    best_val = -float("inf") if maximising else float("inf")

    for move in legal:
        board.push(move)
        val = minimax(board, depth - 1, -float("inf"), float("inf"), not maximising)
        board.pop()
        if maximising and val > best_val:
            best_val = val
            best_move = move
        elif not maximising and val < best_val:
            best_val = val
            best_move = move

    return best_move


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

class Renderer:
    """Handles all Pygame drawing."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.piece_font: pygame.font.Font | None = None
        self.ui_font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.card_number_font: pygame.font.Font | None = None
        self.card_label_font: pygame.font.Font | None = None
        self.card_pawn_font: pygame.font.Font | None = None
        self.title_font: pygame.font.Font | None = None
        self._init_fonts()

    def _init_fonts(self):
        pygame.font.init()
        self.piece_font = pygame.font.SysFont("dejavusans,segoeuisymbol,symbola,arial", SQUARE_SIZE - 12)
        self.ui_font = pygame.font.SysFont("dejavusans,arial,helvetica,sans", 20)
        self.small_font = pygame.font.SysFont("dejavusans,arial,helvetica,sans", 15)
        self.card_number_font = pygame.font.SysFont("dejavusans,arial,helvetica,sans", 72, bold=True)
        self.card_label_font = pygame.font.SysFont("dejavusans,arial,helvetica,sans", 18, bold=True)
        self.card_pawn_font = pygame.font.SysFont("dejavusans,segoeuisymbol,symbola,arial", 48)
        self.title_font = pygame.font.SysFont("dejavusans,arial,helvetica,sans", 26, bold=True)

    # -- Board ---------------------------------------------------------------

    def draw_board(self, board: chess.Board, selected_sq: int | None,
                   legal_targets: set[int], last_move: chess.Move | None):
        for sq in chess.SQUARES:
            file_i = chess.square_file(sq)
            rank_i = chess.square_rank(sq)
            x = BOARD_OFFSET_X + file_i * SQUARE_SIZE
            y = BOARD_OFFSET_Y + (7 - rank_i) * SQUARE_SIZE

            colour = LIGHT_SQUARE if (file_i + rank_i) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(self.screen, colour, (x, y, SQUARE_SIZE, SQUARE_SIZE))

            # Last-move highlight
            if last_move and sq in (last_move.from_square, last_move.to_square):
                surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                surf.fill(HIGHLIGHT_LAST_MOVE)
                self.screen.blit(surf, (x, y))

            # Check highlight
            if board.is_check():
                king_sq = board.king(board.turn)
                if sq == king_sq:
                    surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    surf.fill(HIGHLIGHT_CHECK)
                    self.screen.blit(surf, (x, y))

            # Selected piece highlight
            if sq == selected_sq:
                surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                surf.fill(HIGHLIGHT_SELECTED)
                self.screen.blit(surf, (x, y))

            # Legal-move dot / capture ring
            if sq in legal_targets:
                surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                if board.piece_at(sq) is not None:
                    surf.fill(HIGHLIGHT_CAPTURE)
                else:
                    cx, cy = SQUARE_SIZE // 2, SQUARE_SIZE // 2
                    pygame.draw.circle(surf, HIGHLIGHT_MOVE, (cx, cy), SQUARE_SIZE // 6)
                self.screen.blit(surf, (x, y))

            # Draw piece
            piece = board.piece_at(sq)
            if piece:
                sym = PIECE_UNICODE[piece.symbol()]
                colour_piece = WHITE if piece.color == chess.WHITE else BLACK
                outline_colour = BLACK if piece.color == chess.WHITE else WHITE
                # Draw outline
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        txt = self.piece_font.render(sym, True, outline_colour)
                        rect = txt.get_rect(center=(x + SQUARE_SIZE // 2 + dx, y + SQUARE_SIZE // 2 + dy))
                        self.screen.blit(txt, rect)
                txt = self.piece_font.render(sym, True, colour_piece)
                rect = txt.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
                self.screen.blit(txt, rect)

        # Rank / file labels
        for i in range(8):
            lbl_file = self.small_font.render(chr(ord("a") + i), True, (180, 180, 180))
            self.screen.blit(lbl_file, (BOARD_OFFSET_X + i * SQUARE_SIZE + 2,
                                        BOARD_OFFSET_Y + BOARD_SIZE + 2))
            lbl_rank = self.small_font.render(str(8 - i), True, (180, 180, 180))
            self.screen.blit(lbl_rank, (BOARD_OFFSET_X - 16,
                                        BOARD_OFFSET_Y + i * SQUARE_SIZE + 2))

    # -- Card panel (right side) ---------------------------------------------

    def draw_card_panel(self, card_number: int, forced_file: str, phase: str):
        """Draw the Chaos Card as a playing-card graphic beside the board."""
        panel_x = CARD_PANEL_X
        panel_w = CARD_PANEL_WIDTH

        # Panel background
        panel_rect = pygame.Rect(panel_x, BOARD_OFFSET_Y, panel_w, BOARD_SIZE)
        pygame.draw.rect(self.screen, INFO_PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (60, 60, 80), panel_rect, 1, border_radius=10)

        # Title
        title = self.card_label_font.render("CHAOS CARD", True, CARD_ACCENT)
        self.screen.blit(title, title.get_rect(centerx=panel_x + panel_w // 2,
                                                top=panel_rect.y + 12))

        # -- The card itself --
        card_w, card_h = 160, 220
        card_x = panel_x + (panel_w - card_w) // 2
        card_y = panel_rect.y + 45
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        # Card shadow
        shadow = pygame.Rect(card_x + 3, card_y + 3, card_w, card_h)
        pygame.draw.rect(self.screen, (15, 15, 15), shadow, border_radius=10)

        # Card face
        pygame.draw.rect(self.screen, CARD_FACE, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, CARD_BORDER, card_rect, 3, border_radius=10)

        # Inner border
        inner = card_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, CARD_BORDER, inner, 1, border_radius=6)

        # Number (large, centered)
        num_colour = CARD_RED if card_number in (1, 3, 5, 7) else (30, 30, 100)
        num_txt = self.card_number_font.render(str(card_number), True, num_colour)
        self.screen.blit(num_txt, num_txt.get_rect(center=card_rect.center))

        # Corner numbers (top-left, bottom-right)
        corner_font = self.card_label_font
        tl = corner_font.render(str(card_number), True, num_colour)
        self.screen.blit(tl, (card_x + 10, card_y + 8))
        br = corner_font.render(str(card_number), True, num_colour)
        br_rect = br.get_rect(right=card_x + card_w - 10, bottom=card_y + card_h - 8)
        self.screen.blit(br, br_rect)

        # Pawn symbol below the number
        pawn_sym = "\u265F"
        pawn_txt = self.card_pawn_font.render(pawn_sym, True, num_colour)
        self.screen.blit(pawn_txt, pawn_txt.get_rect(
            centerx=card_rect.centerx, top=card_rect.centery + 30))

        # -- Info below the card --
        info_y = card_y + card_h + 20

        file_lbl = self.card_label_font.render(
            f"{forced_file.upper()}-PAWN", True, CARD_TEXT)
        self.screen.blit(file_lbl, file_lbl.get_rect(
            centerx=panel_x + panel_w // 2, top=info_y))

        # Phase status
        if phase == "forced":
            phase_txt = self.ui_font.render("Must move first!", True, (255, 180, 80))
        else:
            phase_txt = self.ui_font.render("Standard chess", True, (140, 200, 140))
        self.screen.blit(phase_txt, phase_txt.get_rect(
            centerx=panel_x + panel_w // 2, top=info_y + 28))

        # Divider
        div_y = info_y + 65
        pygame.draw.line(self.screen, (60, 60, 80),
                         (panel_x + 20, div_y), (panel_x + panel_w - 20, div_y))

        # Controls help
        help_y = div_y + 15
        controls = [
            ("Click", "Select / Move"),
            ("R", "New Game"),
            ("Q", "Quit"),
        ]
        for key, desc in controls:
            key_txt = self.card_label_font.render(key, True, CARD_ACCENT)
            desc_txt = self.small_font.render(desc, True, (160, 160, 175))
            self.screen.blit(key_txt, (panel_x + 15, help_y))
            self.screen.blit(desc_txt, (panel_x + 15 + key_txt.get_width() + 8, help_y + 2))
            help_y += 24

    # -- Status bar ----------------------------------------------------------

    def draw_status(self, text: str):
        bar = pygame.Rect(BOARD_OFFSET_X, BOARD_OFFSET_Y + BOARD_SIZE + 20,
                          BOARD_SIZE, 28)
        pygame.draw.rect(self.screen, STATUS_BG, bar, border_radius=4)
        lbl = self.ui_font.render(text, True, WHITE)
        self.screen.blit(lbl, (bar.x + 10, bar.y + 4))

    # -- Game-over overlay ---------------------------------------------------

    def draw_game_over(self, message: str):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        self.screen.blit(overlay, (0, 0))

        msg = self.title_font.render(message, True, WHITE)
        cx = BOARD_OFFSET_X + BOARD_SIZE // 2
        cy = BOARD_OFFSET_Y + BOARD_SIZE // 2
        self.screen.blit(msg, msg.get_rect(center=(cx, cy - 20)))

        hint = self.ui_font.render("Press R to restart  |  Q to quit", True, (200, 200, 200))
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 18)))

    # -- Thinking indicator --------------------------------------------------

    def draw_thinking(self):
        lbl = self.ui_font.render("AI is thinking...", True, CARD_ACCENT)
        cx = BOARD_OFFSET_X + BOARD_SIZE // 2
        self.screen.blit(lbl, lbl.get_rect(center=(cx, BOARD_OFFSET_Y + BOARD_SIZE + 34)))


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------

class ChaosCardChess:
    """Manages one game session."""

    def __init__(self):
        self.board = chess.Board()
        self.card_number = random.randint(1, 8)
        self.forced_file = PAWN_FILES[self.card_number]
        self.phase = "forced"          # "forced" or "normal"
        self.selected_square: int | None = None
        self.legal_targets: set[int] = set()
        self.last_move: chess.Move | None = None
        self.game_over = False
        self.game_over_message = ""
        self.player_color = chess.WHITE
        self.ai_thinking = False

    def reset(self):
        self.__init__()

    # -- Helpers -------------------------------------------------------------

    def _forced_legal_moves(self) -> list[chess.Move]:
        """Return only legal pawn moves from the forced file."""
        file_idx = ord(self.forced_file) - ord("a")
        return [
            m for m in self.board.legal_moves
            if chess.square_file(m.from_square) == file_idx
            and self.board.piece_at(m.from_square) is not None
            and self.board.piece_at(m.from_square).piece_type == chess.PAWN
        ]

    def legal_moves_for_square(self, sq: int) -> set[int]:
        moves = (
            self._forced_legal_moves() if self.phase == "forced"
            else list(self.board.legal_moves)
        )
        return {m.to_square for m in moves if m.from_square == sq}

    def try_move(self, from_sq: int, to_sq: int) -> bool:
        """Attempt to make a move. Returns True on success."""
        candidates = (
            self._forced_legal_moves() if self.phase == "forced"
            else list(self.board.legal_moves)
        )
        for m in candidates:
            if m.from_square == from_sq and m.to_square == to_sq:
                self.board.push(m)
                self.last_move = m
                self._post_move()
                return True

        # Handle promotion: try all promotion pieces
        for promo in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
            m = chess.Move(from_sq, to_sq, promotion=promo)
            if m in self.board.legal_moves:
                if self.phase == "forced" and m not in self._forced_legal_moves():
                    continue
                self.board.push(m)
                self.last_move = m
                self._post_move()
                return True
        return False

    def _post_move(self):
        """Check for game-over and transition from forced → normal phase."""
        if self.phase == "forced":
            self.phase = "normal"

        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            self.game_over = True
            self.game_over_message = f"Checkmate! {winner} wins!"
        elif self.board.is_stalemate():
            self.game_over = True
            self.game_over_message = "Stalemate — Draw!"
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.game_over_message = "Insufficient material — Draw!"
        elif self.board.can_claim_threefold_repetition():
            self.game_over = True
            self.game_over_message = "Threefold repetition — Draw!"
        elif self.board.can_claim_fifty_moves():
            self.game_over = True
            self.game_over_message = "50-move rule — Draw!"

    def status_text(self) -> str:
        turn = "White" if self.board.turn == chess.WHITE else "Black"
        who = "Your" if self.board.turn == self.player_color else "AI's"
        extra = ""
        if self.board.is_check():
            extra = "  CHECK!"
        return f"{who} turn ({turn}){extra}"

    def is_player_turn(self) -> bool:
        return self.board.turn == self.player_color and not self.game_over


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chaos Card Chess")
    clock = pygame.time.Clock()

    renderer = Renderer(screen)
    game = ChaosCardChess()

    ai_move_event = pygame.USEREVENT + 1
    ai_delay_ms = 400

    def schedule_ai():
        if not game.game_over and not game.is_player_turn():
            game.ai_thinking = True
            pygame.time.set_timer(ai_move_event, ai_delay_ms, loops=1)

    # If AI plays White (unlikely with current setup, but handle it)
    if not game.is_player_turn():
        schedule_ai()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                    if not game.is_player_turn():
                        schedule_ai()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.game_over or not game.is_player_turn():
                    continue
                mx, my = event.pos
                file_i = (mx - BOARD_OFFSET_X) // SQUARE_SIZE
                rank_i = 7 - (my - BOARD_OFFSET_Y) // SQUARE_SIZE
                if 0 <= file_i < 8 and 0 <= rank_i < 8:
                    clicked_sq = chess.square(file_i, rank_i)

                    if game.selected_square is not None and clicked_sq in game.legal_targets:
                        if game.try_move(game.selected_square, clicked_sq):
                            game.selected_square = None
                            game.legal_targets = set()
                            schedule_ai()
                    else:
                        piece = game.board.piece_at(clicked_sq)
                        if piece and piece.color == game.player_color:
                            targets = game.legal_moves_for_square(clicked_sq)
                            if targets:
                                game.selected_square = clicked_sq
                                game.legal_targets = targets
                            else:
                                game.selected_square = None
                                game.legal_targets = set()
                        else:
                            game.selected_square = None
                            game.legal_targets = set()

            elif event.type == ai_move_event:
                if not game.game_over and not game.is_player_turn():
                    forced = game.forced_file if game.phase == "forced" else None
                    move = ai_choose_move(game.board, forced_file=forced, depth=3)
                    if move:
                        game.board.push(move)
                        game.last_move = move
                        game._post_move()
                    game.ai_thinking = False

        # -- Draw --
        screen.fill((25, 25, 25))

        # Title
        title_lbl = renderer.title_font.render("Chaos Card Chess", True, CARD_ACCENT)
        screen.blit(title_lbl, (BOARD_OFFSET_X, 15))

        renderer.draw_board(game.board, game.selected_square,
                            game.legal_targets, game.last_move)
        renderer.draw_card_panel(game.card_number, game.forced_file, game.phase)
        if game.game_over:
            renderer.draw_game_over(game.game_over_message)
        else:
            renderer.draw_status(game.status_text())
            if game.ai_thinking:
                renderer.draw_thinking()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
