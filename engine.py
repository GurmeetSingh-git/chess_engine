from board import get_all_moves, apply_move, evaluate_board
import math

def alpha_beta(board, depth, alpha, beta, maximizing_white):
    if depth == 0:
        return evaluate_board(board), None

    color = 'white' if maximizing_white else 'black'
    moves = get_all_moves(board, color)

    if not moves:
        # No moves = checkmate or stalemate
        if maximizing_white:
            return -math.inf, None  # White is checkmated
        else:
            return math.inf, None   # Black is checkmated

    best_move = None

    if maximizing_white:
        max_eval = -math.inf
        for move in moves:
            new_board = apply_move(board, move)
            eval_score, _ = alpha_beta(new_board, depth - 1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff (black won't allow this)
        return max_eval, best_move

    else:
        min_eval = math.inf
        for move in moves:
            new_board = apply_move(board, move)
            eval_score, _ = alpha_beta(new_board, depth - 1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff (white won't allow this)
        return min_eval, best_move


def get_best_move(board, color, depth=4):
    """
    Entry point called by FastAPI.
    color: 'white' or 'black'
    Returns: best move dict { from_sq, to_sq, promotion (optional) }
    """
    maximizing = (color == 'white')
    _, best_move = alpha_beta(board, depth, -math.inf, math.inf, maximizing)
    return best_move