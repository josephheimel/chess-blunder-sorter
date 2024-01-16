import os
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


def generateBlunderString(navigable, column, row):
    print(row + 1, "/", len(navigable[column]))
    print("Blunder is a", navigable[column][row][6], "\n")
    print("Real Move:", navigable[column][row][2])
    print("Best Move:", navigable[column][row][3])
    print("Opponent's Best Move:", navigable[column][row][4], "\n")
    print(navigable[column][row][0], "\n")
    print("Opponent:", navigable[column][row][1])
    print("FEN:", navigable[column][row][5], "\n", "\n", "\n")


root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

with open(file_path, "r") as f:
    blunders = json.load(f)

column = 0
row = 0
unkn = False
navigable = []
i = 0
j = 0

for index, (key, value) in enumerate(blunders.items()):
    navigable.append([])
    for index2, (key2, value2) in enumerate(value.items()):
        navigable[i].append([])
        for index3, (key3, value3) in enumerate(value2.items()):
            navigable[i][j].append(value3)
        navigable[i][j].append(key)
        j += 1
    j = 0
    i += 1


while True:
    os.system('cls')
    generateBlunderString(navigable, column, row)
    print("R for next blunder in category,\nL for previous blunder in category,\nD for next category,\nU for previous category,\nE to exit")
    if unkn:
        print("Unrecognized command.")
        unkn = False
    action = input(":")

    match action.lower(): 
        case "r":
            row += 1
            if row == len(navigable[column]):
                row = len(navigable[column]) - 1
        case "l":
            row -= 1
            if row < 0:
               row = 0
        case "d":
            column += 1
            row = 0
            if column == len(navigable):
               column = len(navigable) - 1
        case "u":
            column -= 1
            row = 0
            if column < 0:
               column = 0
        case "e":
            sys.exit(-1)
        case _:
            unkn = True