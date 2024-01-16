# To process a user's games and explore blunders:
- Download and unpack executables and Stockfish 16 included in '.zip' located in 'Releases' page --->
- Download two or more of user's PGN's from chess.com or other source and, if needed, compile into a single '.pgn' file. (or use included 'PGNs' example folder)
- Run 'main.exe' and select PGN file. When parsed, each game and total progress will display. (or use included 'Blunder Files' example folder)
- Run 'navigator.exe' and select blunder json file to display. Use on screen controls to navigate.


# Improvements
- Theoretical:
  - Refine categories to group similar board positions
  - Alert user in game review more often when they have made a commonly made mistake
  - Alert user in game review less often when they succeed in similar positions
 
- Practical:
  - Normal chess UI
  - Asynchronous processing
