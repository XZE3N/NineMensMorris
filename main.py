import tkinter as tk

from config import Config
from domain.board import Board
from repository.player_repository import PlayerRepository
from services.board_service import BoardService
from services.player_service import PlayerService
from ui.game import Game
from ui.player_selection import PlayerSelectionWindow
from validation.board_validator import BoardValidator
from validation.player_validator import PlayerValidator

if __name__ == "__main__":
    config = Config()
    settings = config.settings

    # Instantiate the player service
    player_repository = PlayerRepository("data/players.pkl")
    player_validator = PlayerValidator()
    player_service = PlayerService(player_repository, player_validator)

    if settings.get("GUI", "False").strip().lower() == "true":
        root = tk.Tk()

        player_repository = PlayerRepository("data/players.pkl")
        player_validator = PlayerValidator()
        player_service = PlayerService(player_repository, player_validator)

        app = PlayerSelectionWindow(root, player_service)
        root.mainloop()

    else:
        board = Board()
        board_validator = BoardValidator()
        board_service = BoardService(board, board_validator)

        game = Game(board_service, player_service)
        game.run()

    ''' GUI VERSION
    root = tk.Tk()

    player_repository = PlayerRepository("data/players.pkl")
    player_validator = PlayerValidator()
    player_service = PlayerService(player_repository, player_validator)

    app = PlayerSelectionWindow(root, player_service)
    root.mainloop()
    '''

    ''' CONSOLE VERSION
    board = Board()
    board_validator = BoardValidator()
    board_service = BoardService(board, board_validator)

    player_repository = PlayerRepository("data/players.pkl")
    player_validator = PlayerValidator()
    player_service = PlayerService(player_repository, player_validator)

    game = Game(board_service, player_service)
    game.run()
    '''
