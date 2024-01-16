import chess
import chess.engine
import chess.pgn
import json
import tkinter as tk
from tkinter import filedialog


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

import sys
sys.excepthook = show_exception_and_exit

#
# args: board                   - board object of blunder
#       errorScore              - score to quantify relevance of blunder
#       moveActual              - move that was played
#       bestMove                - move that should have been played
#       opponentBestMove        - move that the blunder gives to the opponent
#       evalBefore              - evaluation before blunder
#       evalCur                 - evaluation after blunder
#       evalDif                 - change in evaluation
#       bestMoveMisses          - times the same best move is missed
#       opponentBestMoveMisses  - times the same opponent's threat is missed
#       opponent                - opponents username
class Blunder:
  def __init__(self, board, errorScore, moveActual, bestMove, opponentBestMove, evalBefore, evalCur, evalDif, bestMoveMisses, opponentBestMoveMisses, opponent):
    self.board = board
    self.moveActual = moveActual
    self.bestMove = bestMove
    self.opponentBestMove = opponentBestMove
    self.evalBefore = evalBefore
    self.evalCur = evalCur
    self.evalDif = evalDif
    self.bestMoveMisses = bestMoveMisses
    self.opponentBestMoveMisses = opponentBestMoveMisses
    self.opponent = opponent


#
# args: d   - dict obj
#
# ret:  array of values and headers at base of a dict
def getAllValues(d, prefix=None):
    if prefix is None:
        prefix = list()
    for key, value in d.items():
        if not isinstance(value, dict):
            value.append(prefix + [key])
            yield value
        else:
            yield from getAllValues(value, prefix + [key])

#
# args: pieceType   - array of blunders with the same piece
#
# ret:  array of blunders of this piece type and sorted by errorScore
def orderByError(pieceType, blunder):
  # first blunder in array
  if pieceType == []:
    pieceType.append(blunder)
    return pieceType

  # insert above next lowest blunder
  for i in range(len(pieceType)):
    if blunder.errorScore > pieceType[i].errorScore:
      pieceType.insert(i, blunder)
      return pieceType
  
  # smallest blunder
  pieceType.append(blunder)
  return pieceType

#
# args: blunderType   - dict of categorized blunders
#
# ret:  dict of blunders categorized by mistake type and piece and sorted by errorScore
def categorize(blunderType, blunder):
  if "K" in blunder.moveActual:
    blunderType["king"] = orderByError(blunderType["king"], blunder)
    return blunderType
  if "Q" in blunder.moveActual:
    blunderType["queen"] = orderByError(blunderType["queen"], blunder)
    return blunderType
  if "R" in blunder.moveActual:
    blunderType["rook"] = orderByError(blunderType["rook"], blunder)
    return blunderType
  if "N" in blunder.moveActual:
    blunderType["knight"] = orderByError(blunderType["knight"], blunder)
    return blunderType
  if "B" in blunder.moveActual:
    blunderType["bishop"] = orderByError(blunderType["bishop"], blunder)
    return blunderType
  else:
    blunderType["pawn"] = orderByError(blunderType["pawn"], blunder)
    return blunderType

#
# args: blunders    - array of unsorted blunders
#
# ret:  blunders categorized by mistake type and piece and sorted by errorScore
def sortBlunders(blunders):

  resultSet = {
    "missedMate": {"king": [], "queen": [], "rook": [], "knight": [], "bishop": [], "pawn": []},
    "allowedMate": {"king": [], "queen": [], "rook": [], "knight": [], "bishop": [], "pawn": []},
    "missedCaptures": {"king": [], "queen": [], "rook": [], "knight": [], "bishop": [], "pawn": []},
    "missedDefense": {"king": [], "queen": [], "rook": [], "knight": [], "bishop": [], "pawn": []},
    "positionalMistake": {"king": [], "queen": [], "rook": [], "knight": [], "bishop": [], "pawn": []}
  }

  for b in blunders:

    # missed mate (evalBefore is mate in n moves)
    if b.evalBefore == 30:
      b.errorScore = (1 + b.bestMoveMisses) * b.evalDif
      resultSet["missedMate"] = categorize(resultSet["missedMate"], b)

    # allowed opponent mate (evalCur is mate in n moves)
    elif b.evalCur == 30:
      b.errorScore = (1 + b.opponentBestMoveMisses) * b.evalDif
      resultSet["allowedMate"] = categorize(resultSet["allowedMate"], b)

    # missed capture (best move is takes)
    elif "x" in b.bestMove:
      b.errorScore = (1 + b.bestMoveMisses) * b.evalDif
      resultSet["missedCaptures"] = categorize(resultSet["missedCaptures"], b)

    # missed defense (opponent best move is takes)
    elif "x" in b.opponentBestMove:
      b.errorScore = (1 + b.opponentBestMoveMisses) * b.evalDif
      resultSet["missedDefense"] = categorize(resultSet["missedDefense"], b)

    # positional mistake (no captures or checks)
    else:
      b.errorScore = (1 + b.bestMoveMisses + b.opponentBestMoveMisses) * b.evalDif
      resultSet["positionalMistake"] = categorize(resultSet["positionalMistake"], b)

  # sort
  unsortedBlunders = getAllValues(resultSet)
  sortedBlunders = []

  for array in unsortedBlunders:    
    # empty piece array
    if len(array) == 1:
      continue

    # first blunder array in array
    if sortedBlunders == []:
      sortedBlunders.append(array)
      continue

    # insert above next shortest array
    for i in range(len(sortedBlunders) + 1):
      # smallest array size
      if i == len(sortedBlunders):
        sortedBlunders.append(array)
      # insert into array
      elif len(array) > len(sortedBlunders[i]) or (len(array) == len(sortedBlunders[i]) and array[0].errorScore > sortedBlunders[i][0].errorScore):
        sortedBlunders.insert(i, array)
        break
    
    
  return sortedBlunders

#
# args: isWhite   - player color as boolean
#       info      - engine analysis for position
#
# ret:  evaluation in centipawns or None for mate lines
def getScore(isWhite, info):
    if isWhite:
      return info["score"].black().score()
    else:
      return info["score"].white().score()

#
# args: board   - last move in san
#       move    - move in san
#
# ret:  1 if moves match, 0 otherwise
def repetitionCounter(lastMove, move):
  if lastMove == move:
    return 1
  else:
    return 0

#
# 
# main:
blunders = []
engine = chess.engine.SimpleEngine.popen_uci("stockfish-windows-x86-64-avx2.exe")
games = []
progress = 0

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

# Populate games array
with open(file_path) as pgn:
  while True:
    gameNotation = chess.pgn.read_game(pgn)
    if gameNotation is not None:
      games.append(gameNotation)
    else:
      break

# Find main player
if games[0].headers["White"] == games[1].headers["White"] or games[0].headers["White"] == games[1].headers["Black"]:
  player = games[0].headers["White"]

if games[0].headers["Black"] == games[1].headers["Black"] or games[0].headers["Black"] == games[1].headers["White"]:
  player = games[0].headers["Black"]

# Parse game notation
for game in games:
  board = game.board()
  beforeMove = False
  evalCur = 0
  evalBefore = 0
  bestMoveMisses = 0
  opponentBestMoveMisses = 0
  bestMove = "n/a"
  opponentBestMove = "n/a"
  captures = 0

  for move in game.mainline_moves():

    moveActual = board.san(move)
    # set move order
    if game.headers["Black"] == player:
      beforeMove = True

      # set opponent
      opponent = game.headers["White"]
    else:
      opponent = game.headers["Black"]

    # stop looking with 7 pieces left
    if captures >= 25:
      break
    if board.is_capture(move):
      captures += 1

    # Advance board
    board.push(move)
    if board.is_checkmate():
      break

    # Board before player move
    if beforeMove:
      beforeMove = False
      info = engine.analyse(board, chess.engine.Limit(depth=20))
      if "pv" not in info.keys():
        continue
      evalBefore = getScore(player == game.headers["White"], info)
      bestMoveMisses = repetitionCounter(bestMove, board.san(info["pv"][0]))
      bestMove = board.san(info["pv"][0])
      continue

    # After player move
    beforeMove = True
    info = engine.analyse(board, chess.engine.Limit(depth=20))
    if "pv" not in info.keys():
      continue
    evalCur = getScore(player == game.headers["White"], info)
    opponentBestMoveMisses = repetitionCounter(opponentBestMove, board.san(info["pv"][0]))
    opponentBestMove = board.san(info["pv"][0])

    # Find blunders
    if evalBefore == None:
      evalBefore = 30
    else:
      evalBefore /= 100
    if evalCur == None:
      evalCur = 30
    else:
      evalCur /= 100
    evalDif = -((evalBefore + 100) - (evalCur + 100))

    if evalDif > 2 and (evalCur < 15 or evalCur > -15):
      # Check for miss by repetition
      if bestMoveMisses > 0 or opponentBestMoveMisses > 0:
        b = blunders.pop()
        b.bestMoveMisses += bestMoveMisses
        b.opponentBestMoveMisses += opponentBestMoveMisses
        blunders.append(b)
        continue
      blunders.append(Blunder(board, 0, moveActual, bestMove, opponentBestMove, evalBefore, evalCur, evalDif, bestMoveMisses, opponentBestMoveMisses, opponent))
  progress += 1
  print(game.headers["White"],"vs. ", game.headers["Black"], game.headers["Result"], "|", progress, "/", len(games))
  print(board)

# Sort blunders
sortedBlunders = sortBlunders(blunders)

# Make json readable
jsonString = {}

for sB in sortedBlunders:
  key = sB[len(sB) - 1][0] + " when moving a " + sB[len(sB) - 1][1]
  value = {}
  rank = 0

  for b in sB:
    if isinstance(b, list):
      continue

    rank += 1
    props = {
      "board": str(b.board),
      "opponent": b.opponent,
      "real move": b.moveActual,
      "best move": b.bestMove,
      "opponent best move": b.opponentBestMove,
      "fen": b.board.fen()
    }
    value.update({rank : props})
  
  jsonString.update({key : value})


with open("blunders.json", "w") as f:
  json.dump(jsonString, f, indent=2)

print("done")