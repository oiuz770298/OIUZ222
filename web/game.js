// Chaos Card Chess - Game Logic

const PAWN_FILES = {1:'a',2:'b',3:'c',4:'d',5:'e',6:'f',7:'g',8:'h'};
const PIECE_VALUES = {p:100, n:320, b:330, r:500, q:900, k:20000};

// Piece-square tables (White's perspective, index 0=a8)
const PST = {
  p: [
    0,0,0,0,0,0,0,0,
    50,50,50,50,50,50,50,50,
    10,10,20,30,30,20,10,10,
    5,5,10,25,25,10,5,5,
    0,0,0,20,20,0,0,0,
    5,-5,-10,0,0,-10,-5,5,
    5,10,10,-20,-20,10,10,5,
    0,0,0,0,0,0,0,0
  ],
  n: [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,0,0,0,0,-20,-40,
    -30,0,10,15,15,10,0,-30,
    -30,5,15,20,20,15,5,-30,
    -30,0,15,20,20,15,0,-30,
    -30,5,10,15,15,10,5,-30,
    -40,-20,0,5,5,0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
  ],
  b: [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,0,0,0,0,0,0,-10,
    -10,0,10,10,10,10,0,-10,
    -10,5,5,10,10,5,5,-10,
    -10,0,5,10,10,5,0,-10,
    -10,10,10,10,10,10,10,-10,
    -10,5,0,0,0,0,5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
  ],
  r: [
    0,0,0,0,0,0,0,0,
    5,10,10,10,10,10,10,5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    0,0,0,5,5,0,0,0
  ],
  q: [
    -20,-10,-10,-5,-5,-10,-10,-20,
    -10,0,0,0,0,0,0,-10,
    -10,0,5,5,5,5,0,-10,
    -5,0,5,5,5,5,0,-5,
    0,0,5,5,5,5,0,-5,
    -10,5,5,5,5,5,0,-10,
    -10,0,5,0,0,0,0,-10,
    -20,-10,-10,-5,-5,-10,-10,-20
  ],
  k: [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20,20,0,0,0,0,20,20,
    20,30,10,0,0,10,30,20
  ]
};

let game, whiteCard, whiteForced, whitePhase, blackCard, blackForced, blackPhase;
let selectedSquare, legalTargets, lastMove, aiThinking;

function initGame() {
  game = new Chess();
  whiteCard = Math.floor(Math.random() * 8) + 1;
  whiteForced = PAWN_FILES[whiteCard];
  whitePhase = 'forced';
  blackCard = Math.floor(Math.random() * 8) + 1;
  blackForced = PAWN_FILES[blackCard];
  blackPhase = 'forced';
  selectedSquare = null;
  legalTargets = [];
  lastMove = null;
  aiThinking = false;
  updateCards();
  renderBoard();
  updateStatus();
}

function resetGame() {
  document.getElementById('game-over').classList.remove('show');
  initGame();
}

// --- Board Rendering ---

function squareToAlgebraic(row, col) {
  return String.fromCharCode(97 + col) + (8 - row);
}

function renderBoard() {
  const board = document.getElementById('chess-board');
  board.innerHTML = '';

  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const sq = squareToAlgebraic(row, col);
      const div = document.createElement('div');
      div.className = 'square ' + ((row + col) % 2 === 0 ? 'light' : 'dark');
      div.dataset.square = sq;

      if (selectedSquare === sq) div.classList.add('selected');
      if (lastMove && (sq === lastMove.from || sq === lastMove.to)) div.classList.add('last-move');

      // Check highlight
      if (game.in_check()) {
        const turn = game.turn();
        const boardState = game.board();
        for (let r = 0; r < 8; r++) {
          for (let c = 0; c < 8; c++) {
            const p = boardState[r][c];
            if (p && p.type === 'k' && p.color === turn) {
              const kingSq = squareToAlgebraic(r, c);
              if (sq === kingSq) div.classList.add('check');
            }
          }
        }
      }

      // Legal targets
      if (legalTargets.includes(sq)) {
        const piece = game.get(sq);
        div.classList.add(piece ? 'legal-capture' : 'legal-target');
      }

      // Piece
      const piece = game.get(sq);
      if (piece) {
        const img = document.createElement('div');
        img.className = 'piece-svg';
        img.innerHTML = getPieceSVG(piece);
        const svgEl = img.querySelector('svg');
        if (svgEl) {
          svgEl.style.width = '100%';
          svgEl.style.height = '100%';
        }
        div.appendChild(img);
      }

      // Labels
      if (col === 0) {
        const rl = document.createElement('span');
        rl.className = 'rank-label';
        rl.textContent = 8 - row;
        rl.style.top = '2px';
        rl.style.color = (row + col) % 2 === 0 ? '#b58863' : '#f0d9b5';
        div.appendChild(rl);
      }
      if (row === 7) {
        const fl = document.createElement('span');
        fl.className = 'file-label';
        fl.textContent = String.fromCharCode(97 + col);
        fl.style.right = '2px';
        fl.style.color = (row + col) % 2 === 0 ? '#b58863' : '#f0d9b5';
        div.appendChild(fl);
      }

      div.addEventListener('click', () => onSquareClick(sq));
      board.appendChild(div);
    }
  }
}

// --- Card Panel ---

function updateOneCard(prefix, cardNum, forcedFile, phase) {
  const numEl = document.getElementById(prefix + '-card-num');
  const topEl = document.getElementById(prefix + '-corner-top');
  const botEl = document.getElementById(prefix + '-corner-bot');
  const labelEl = document.getElementById(prefix + '-pawn-label');
  const phaseEl = document.getElementById(prefix + '-phase-text');

  numEl.textContent = cardNum;
  topEl.textContent = cardNum;
  botEl.textContent = cardNum;

  const isOdd = cardNum % 2 === 1;
  const colorClass = isOdd ? 'red' : 'blue';
  numEl.className = 'card-number ' + colorClass;
  topEl.className = 'card-corner top ' + colorClass;
  botEl.className = 'card-corner bottom ' + colorClass;

  const cardEl = document.getElementById(prefix === 'w' ? 'white-card' : 'black-card');
  const pawnEl = cardEl.querySelector('.card-pawn');
  if (pawnEl) pawnEl.style.color = isOdd ? '#b41e1e' : '#1e2e80';

  labelEl.textContent = forcedFile.toUpperCase() + '-PAWN';

  if (phase === 'forced') {
    phaseEl.textContent = 'Must move first!';
    phaseEl.className = 'phase-text forced';
  } else {
    phaseEl.textContent = 'Done ✓';
    phaseEl.className = 'phase-text normal';
  }
}

function updateCards() {
  updateOneCard('w', whiteCard, whiteForced, whitePhase);
  updateOneCard('b', blackCard, blackForced, blackPhase);
}

// --- Game Logic ---

function getForcedMoves(file) {
  const moves = game.moves({ verbose: true });
  return moves.filter(m => {
    const piece = game.get(m.from);
    return piece && piece.type === 'p' && m.from[0] === file;
  });
}

function getLegalMovesForSquare(sq) {
  let moves;
  if (whitePhase === 'forced') {
    moves = getForcedMoves(whiteForced);
  } else {
    moves = game.moves({ verbose: true });
  }
  return moves.filter(m => m.from === sq).map(m => m.to);
}

function onSquareClick(sq) {
  if (game.game_over() || aiThinking || game.turn() !== 'w') return;

  if (selectedSquare && legalTargets.includes(sq)) {
    // Try to make the move
    const moveResult = game.move({ from: selectedSquare, to: sq, promotion: 'q' });
    if (moveResult) {
      lastMove = { from: selectedSquare, to: sq };
      if (whitePhase === 'forced') whitePhase = 'normal';
      selectedSquare = null;
      legalTargets = [];
      updateCards();
      renderBoard();
      checkGameOver();
      if (!game.game_over()) {
        scheduleAI();
      }
      updateStatus();
      return;
    }
  }

  // Select a piece
  const piece = game.get(sq);
  if (piece && piece.color === 'w') {
    const targets = getLegalMovesForSquare(sq);
    if (targets.length > 0) {
      selectedSquare = sq;
      legalTargets = targets;
    } else {
      selectedSquare = null;
      legalTargets = [];
    }
  } else {
    selectedSquare = null;
    legalTargets = [];
  }
  renderBoard();
}

function updateStatus() {
  const el = document.getElementById('status-bar');
  if (game.game_over()) return;
  if (aiThinking) {
    el.textContent = 'AI is thinking...';
    el.className = 'thinking';
    el.id = 'status-bar';
  } else {
    const turn = game.turn() === 'w' ? 'White' : 'Black';
    const who = game.turn() === 'w' ? 'Your' : "AI's";
    let extra = game.in_check() ? '  CHECK!' : '';
    el.textContent = `${who} turn (${turn})${extra}`;
    el.className = '';
    el.id = 'status-bar';
  }
}

function checkGameOver() {
  if (!game.game_over()) return;
  const msgEl = document.getElementById('game-over-msg');
  if (game.in_checkmate()) {
    const winner = game.turn() === 'w' ? 'Black' : 'White';
    msgEl.textContent = `Checkmate! ${winner} wins!`;
  } else if (game.in_stalemate()) {
    msgEl.textContent = 'Stalemate — Draw!';
  } else if (game.in_draw()) {
    msgEl.textContent = 'Draw!';
  } else if (game.in_threefold_repetition()) {
    msgEl.textContent = 'Threefold repetition — Draw!';
  }
  document.getElementById('game-over').classList.add('show');
  const el = document.getElementById('status-bar');
  el.textContent = msgEl.textContent;
}

// --- AI ---

function scheduleAI() {
  aiThinking = true;
  updateStatus();
  setTimeout(() => {
    const move = aiBestMove(game, 3);
    if (move) {
      game.move(move);
      lastMove = { from: move.from, to: move.to };
      if (blackPhase === 'forced') blackPhase = 'normal';
    }
    aiThinking = false;
    updateCards();
    renderBoard();
    checkGameOver();
    updateStatus();
  }, 300);
}

function evaluateBoard(g) {
  if (g.in_checkmate()) {
    return g.turn() === 'w' ? -99999 : 99999;
  }
  if (g.in_stalemate() || g.in_draw()) return 0;

  let score = 0;
  const board = g.board();
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      const p = board[r][c];
      if (!p) continue;
      let val = PIECE_VALUES[p.type] || 0;
      const pst = PST[p.type];
      if (pst) {
        const idx = p.color === 'w' ? (r * 8 + c) : ((7 - r) * 8 + c);
        val += pst[idx];
      }
      score += p.color === 'w' ? val : -val;
    }
  }
  return score;
}

function minimax(g, depth, alpha, beta, maximizing) {
  if (depth === 0 || g.game_over()) {
    return evaluateBoard(g);
  }
  const moves = g.moves({ verbose: true });
  // Order: captures first
  moves.sort((a, b) => {
    let sa = a.captured ? PIECE_VALUES[a.captured] * 10 : 0;
    let sb = b.captured ? PIECE_VALUES[b.captured] * 10 : 0;
    if (a.promotion) sa += PIECE_VALUES[a.promotion] || 0;
    if (b.promotion) sb += PIECE_VALUES[b.promotion] || 0;
    return sb - sa;
  });

  if (maximizing) {
    let maxEval = -Infinity;
    for (const m of moves) {
      g.move(m);
      const val = minimax(g, depth - 1, alpha, beta, false);
      g.undo();
      maxEval = Math.max(maxEval, val);
      alpha = Math.max(alpha, val);
      if (beta <= alpha) break;
    }
    return maxEval;
  } else {
    let minEval = Infinity;
    for (const m of moves) {
      g.move(m);
      const val = minimax(g, depth - 1, alpha, beta, true);
      g.undo();
      minEval = Math.min(minEval, val);
      beta = Math.min(beta, val);
      if (beta <= alpha) break;
    }
    return minEval;
  }
}

function aiBestMove(g, depth) {
  let moves = g.moves({ verbose: true });
  if (moves.length === 0) return null;

  // AI (black) must use its own forced pawn on first move
  if (blackPhase === 'forced') {
    const forced = moves.filter(m => {
      const p = g.get(m.from);
      return p && p.type === 'p' && m.from[0] === blackForced;
    });
    if (forced.length > 0) moves = forced;
  }

  let bestMove = moves[0];
  let bestVal = Infinity; // AI is black, minimizing

  for (const m of moves) {
    g.move(m);
    const val = minimax(g, depth - 1, -Infinity, Infinity, true);
    g.undo();
    if (val < bestVal) {
      bestVal = val;
      bestMove = m;
    }
  }
  return bestMove;
}

// --- Keyboard ---

document.addEventListener('keydown', (e) => {
  if (e.key === 'r' || e.key === 'R') resetGame();
});

// --- Init ---

initGame();
