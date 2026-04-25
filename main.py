from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from board import initial_board
from engine import get_best_move

app = FastAPI()

class MoveRequest(BaseModel):
    board: List[List[Optional[str]]]   # 8×8 grid of strings or null
    color: str                          # 'white' or 'black'
    depth: int = 4

@app.get("/")
def root():
    return {"status": "Chess AI running"}

@app.get("/api/initial-board")
def get_initial_board():
    return {"board": initial_board()}

@app.post("/api/best-move")
def best_move(req: MoveRequest):
    if req.color not in ('white', 'black'):
        raise HTTPException(status_code=400, detail="color must be 'white' or 'black'")

    move = get_best_move(req.board, req.color, req.depth)

    if move is None:
        return {"move": None, "status": "game_over"}

    return {
        "from": {"row": move['from'][0], "col": move['from'][1]},
        "to":   {"row": move['to'][0],   "col": move['to'][1]},
        "promotion": move.get('promotion'),
        "status": "ok"
    }