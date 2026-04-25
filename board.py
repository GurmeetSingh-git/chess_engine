import copy

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

PIECE_VALUES = {
    'pawn':   100,
    'knight': 320,
    'bishop': 330,
    'rook':   500,
    'queen':  900,
    'king':   20000,
}

# Piece-square tables (from White's perspective, row 0 = rank 8)
# These reward good piece placement on top of raw material value

PST = {
    'pawn': [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [ 5,  5, 10, 25, 25, 10,  5,  5],
        [ 0,  0,  0, 20, 20,  0,  0,  0],
        [ 5, -5,-10,  0,  0,-10, -5,  5],
        [ 5, 10, 10,-20,-20, 10, 10,  5],
        [ 0,  0,  0,  0,  0,  0,  0,  0],
    ],
    'knight': [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50],
    ],
    'bishop': [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20],
    ],
    'rook': [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [ 0,  0,  0,  5,  5,  0,  0,  0],
    ],
    'queen': [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [ -5,  0,  5,  5,  5,  5,  0, -5],
        [  0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20],
    ],
    'king': [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [ 20, 20,  0,  0,  0,  0, 20, 20],
        [ 20, 30, 10,  0,  0, 10, 30, 20],
    ],
}

# ─────────────────────────────────────────────
#  BOARD HELPERS
# ─────────────────────────────────────────────

def parse_piece(cell: str):
    """
    'white_knight' → ('white', 'knight')
    None           → (None, None)
    """
    if cell is None:
        return None, None
    parts = cell.split('_', 1)
    return parts[0], parts[1]


def in_bounds(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def initial_board():
    """Returns the standard starting position as an 8×8 list."""
    board = [[None] * 8 for _ in range(8)]

    back_rank = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']

    for col, piece in enumerate(back_rank):
        board[0][col] = f'black_{piece}'
        board[7][col] = f'white_{piece}'

    for col in range(8):
        board[1][col] = 'black_pawn'
        board[6][col] = 'white_pawn'

    return board


# ─────────────────────────────────────────────
#  MOVE GENERATION
# ─────────────────────────────────────────────

def get_all_moves(board, color):
    """
    Returns a list of all pseudo-legal moves for `color`.
    Each move is a dict:
      { 'from': (row, col), 'to': (row, col), 'promotion': 'queen' | None }
    """
    moves = []
    for row in range(8):
        for col in range(8):
            cell = board[row][col]
            if cell is None:
                continue
            piece_color, piece_type = parse_piece(cell)
            if piece_color != color:
                continue
            moves.extend(_piece_moves(board, row, col, color, piece_type))
    return moves


def _piece_moves(board, row, col, color, piece_type):
    if piece_type == 'pawn':
        return _pawn_moves(board, row, col, color)
    elif piece_type == 'knight':
        return _knight_moves(board, row, col, color)
    elif piece_type == 'bishop':
        return _sliding_moves(board, row, col, color, [(-1,-1),(-1,1),(1,-1),(1,1)])
    elif piece_type == 'rook':
        return _sliding_moves(board, row, col, color, [(-1,0),(1,0),(0,-1),(0,1)])
    elif piece_type == 'queen':
        return _sliding_moves(board, row, col, color,
                              [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)])
    elif piece_type == 'king':
        return _king_moves(board, row, col, color)
    return []


def _make_move(fr, to, promotion=None):
    return {'from': fr, 'to': to, 'promotion': promotion}


def _pawn_moves(board, row, col, color):
    moves = []
    direction = -1 if color == 'white' else 1   # white moves up (decreasing row)
    start_row  =  6 if color == 'white' else 1
    promo_row  =  0 if color == 'white' else 7

    # One step forward
    nr = row + direction
    if in_bounds(nr, col) and board[nr][col] is None:
        if nr == promo_row:
            for promo in ['queen', 'rook', 'bishop', 'knight']:
                moves.append(_make_move((row, col), (nr, col), promo))
        else:
            moves.append(_make_move((row, col), (nr, col)))

        # Two steps from start
        if row == start_row and board[row + 2 * direction][col] is None:
            moves.append(_make_move((row, col), (row + 2 * direction, col)))

    # Diagonal captures
    for dc in [-1, 1]:
        nc = col + dc
        if in_bounds(nr, nc):
            target_color, _ = parse_piece(board[nr][nc])
            if target_color is not None and target_color != color:
                if nr == promo_row:
                    for promo in ['queen', 'rook', 'bishop', 'knight']:
                        moves.append(_make_move((row, col), (nr, nc), promo))
                else:
                    moves.append(_make_move((row, col), (nr, nc)))

    return moves


def _knight_moves(board, row, col, color):
    moves = []
    offsets = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    for dr, dc in offsets:
        nr, nc = row + dr, col + dc
        if not in_bounds(nr, nc):
            continue
        target_color, _ = parse_piece(board[nr][nc])
        if target_color != color:          # empty or enemy
            moves.append(_make_move((row, col), (nr, nc)))
    return moves


def _sliding_moves(board, row, col, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while in_bounds(nr, nc):
            target_color, _ = parse_piece(board[nr][nc])
            if target_color is None:
                moves.append(_make_move((row, col), (nr, nc)))
            elif target_color != color:
                moves.append(_make_move((row, col), (nr, nc)))
                break                      # capture then stop
            else:
                break                      # blocked by own piece
            nr += dr
            nc += dc
    return moves


def _king_moves(board, row, col, color):
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if not in_bounds(nr, nc):
                continue
            target_color, _ = parse_piece(board[nr][nc])
            if target_color != color:
                moves.append(_make_move((row, col), (nr, nc)))
    return moves


# ─────────────────────────────────────────────
#  APPLY MOVE
# ─────────────────────────────────────────────

def apply_move(board, move):
    """
    Returns a NEW board with `move` applied. Does not mutate original.
    """
    new_board = [row[:] for row in board]   # shallow-copy each row (strings are immutable)

    fr = move['from']
    to = move['to']
    promotion = move.get('promotion')

    piece = new_board[fr[0]][fr[1]]
    new_board[to[0]][to[1]] = piece
    new_board[fr[0]][fr[1]] = None

    # Handle promotion
    if promotion:
        color, _ = parse_piece(piece)
        new_board[to[0]][to[1]] = f'{color}_{promotion}'

    return new_board


# ─────────────────────────────────────────────
#  EVALUATION
# ─────────────────────────────────────────────

def evaluate_board(board):
    """
    Returns a score from White's perspective.
    Positive  → White is better.
    Negative  → Black is better.
    """
    score = 0
    for row in range(8):
        for col in range(8):
            cell = board[row][col]
            if cell is None:
                continue
            color, piece_type = parse_piece(cell)

            material = PIECE_VALUES.get(piece_type, 0)
            pst_table = PST.get(piece_type)

            if pst_table:
                # White uses the table top-to-bottom (row 0 = black's back rank)
                # Black mirrors it vertically
                pst_row = row if color == 'white' else (7 - row)
                positional = pst_table[pst_row][col]
            else:
                positional = 0

            if color == 'white':
                score += material + positional
            else:
                score -= material + positional

    return score