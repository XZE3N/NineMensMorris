import random
import time

from domain.color import Color, ANSIColors
from domain.player import Player
from exceptions import ValidationError, RepositoryError, ServiceError, BitBoardError
from services.ai import NineMensMorrisAI
from services.board_service import BoardService
from services.player_service import PlayerService


class Game:
    def __init__(self, board_service: BoardService, player_service: PlayerService):
        self.__board_service = board_service
        self.__player_service = player_service
        self.__player_one = None
        self.__player_two = None
        self.__players = []
        self.__current_turn = 0

        self.__is_ai = False
        self.__ai = None

    def run(self):
        print("Welcome to Nine Men's Morris!")
        self.__player_selection()

    def __print_player_selection_options(self):
        print("----- Player Selection -----")
        if self.__player_one:
            print(f"1. Select Player One. {ANSIColors.BLUE}[{self.__player_one.name}]{ANSIColors.END}")
        else:
            print("1. Select Player One.")
        if self.__player_two:
            print(f"2. Select Player Two. {ANSIColors.BLUE}[{self.__player_two.name}]{ANSIColors.END}")
        else:
            print("2. Select Player Two.")
        print("3. Start Game.")
        print("0. Exit Game.")

    def __player_selection(self):
        self.__print_player_selection_options()

        options = {
            "1": (self.__select_player, "__player_one"),
            "2": (self.__select_player, "__player_two"),
            "3": self.__exit_player_selection
        }

        while True:
            option = input("Please select an option from the list: ")
            option = option.strip()
            if option == '':
                continue
            if option == '0':
                print("Goodbye!")
                exit(0)
            option = option.lower()
            if option in options:
                try:
                    if isinstance(options[option], tuple):
                        function, params = options[option]
                        print(ANSIColors.CYAN)
                        function(params)
                        print(ANSIColors.END)
                    else:
                        options[option]()
                    self.__print_player_selection_options()
                except ValueError as ve:
                    print(f"{ANSIColors.RED}Error: {ve}{ANSIColors.END}")
            else:
                print("Invalid option!")

    @staticmethod
    def __print_select_player_options(player: str):
        if player == "__player_one":
            print("----- Select Player 1 -----")
        elif player == "__player_two":
            print(f"----- Select Player 2 -----")
        print("1. Select existing player.")
        print("2. Create new player.")
        print("3. Remove an existing player.")
        print("0. Exit")

    def __select_player(self, player: str):
        self.__print_select_player_options(player)
        options = {
            "1": self.__select_existing_player,
            "2": self.__create_new_player,
            "3": self.__remove_existing_player
        }

        while True:
            option = input("Please select an option from the list: ")
            option = option.strip()
            if option == '':
                continue
            if option == '0':
                print("---------------------------")
                break
            option = option.lower()
            if option in options:
                print(ANSIColors.YELLOW)
                try:
                    result = options[option]()
                    if isinstance(result, Player):
                        if player == "__player_one":
                            if result.id == -1:
                                raise ValueError("The AI can only play as black!")
                            if self.__player_two == result:
                                raise ValueError("The two players cannot both be the same!")
                            self.__player_one = result
                            return
                        if player == "__player_two":
                            if self.__player_one == result:
                                raise ValueError("The two players cannot both be the same!")
                            self.__player_two = result
                            return
                except ValidationError as vde:
                    print(f"{ANSIColors.RED}Error: {vde}{ANSIColors.END}")
                except RepositoryError as re:
                    print(f"{ANSIColors.RED}Error: {re}{ANSIColors.END}")
                except ServiceError as se:
                    print(f"{ANSIColors.RED}Error: {se}{ANSIColors.END}")
                except ValueError as ve:
                    print(f"{ANSIColors.RED}Error: {ve}{ANSIColors.END}")

                print(f"{ANSIColors.END}{ANSIColors.CYAN}")
                self.__print_select_player_options(player)
            else:
                print("Invalid option!")

    def __select_existing_player(self):
        players_list = self.__player_service.get_all()
        if len(players_list) == 0:
            print("There are no existing players!")
            return

        players = {}
        for player in players_list:
            players[str(player.id)] = player

        print(f"----- Existing players -----")
        print("#. AI")
        for player in players_list:
            print(f"{player.id}. {player.name}")
        print("0. Exit")

        while True:
            option = input("Please select a player from the list: ")
            option = option.strip()
            if option == '':
                continue
            if option == '0':
                print(f"----------------------------")
                return
            option = option.lower()
            if option in players:
                print(f"----------------------------")
                return players[option]
            elif option == "#":
                print(f"----------------------------")
                return Player(-1, "AI", None)
            else:
                print("Please select a valid player!")

    def __create_new_player(self):
        print("Adding player...")
        if len(self.__player_service.get_all()) == 0:
            player_id = 1
        else:
            player_id = self.__player_service.get_all()[-1].id + 1

        name = input("Provide a name for the player: ").strip()

        self.__player_service.add(player_id, name, Color.WHITE)
        print("Player added successfully!")

    def __remove_existing_player(self):
        print("Removing existing player...")
        try:
            player_id = int(input("Provide a player Id: "))
        except ValueError:
            raise ValueError("The value of the player Id must be an integer!")
        self.__player_service.remove(player_id)
        print("Player removed successfully!")

    def __exit_player_selection(self):
        if not self.__player_one:
            raise ValueError("Player one was not selected!")
        if not self.__player_two:
            raise ValueError("Player two was not selected!")

        self.__player_one.color = Color.WHITE
        self.__player_two.color = Color.BLACK

        self.__players = [self.__player_one, self.__player_two]
        if self.__player_two.id == -1:
            self.__is_ai = True
            self.__ai = NineMensMorrisAI()
            self.__ai.phase = "placing"

        self.__piece_placing()

    def __print_board_and_info(self):
        print(self.__board_service.board())
        if self.__players[self.__current_turn].color == Color.WHITE:
            print(f"{ANSIColors.GREEN}{self.__players[self.__current_turn].name}{ANSIColors.END}'s turn.")
        else:
            print(f"{ANSIColors.RED}{self.__players[self.__current_turn].name}{ANSIColors.END}'s turn.")

    def __print_pieces_in_hand(self):
        print(
            f"{ANSIColors.BLUE}[{self.__player_one.name}]{ANSIColors.END}: Pieces in hand - {ANSIColors.GREEN}[{self.__player_one.pieces_in_hand}]{ANSIColors.END}")
        print(
            f"{ANSIColors.BLUE}[{self.__player_two.name}]{ANSIColors.END}: Pieces in hand - {ANSIColors.GREEN}[{self.__player_two.pieces_in_hand}]{ANSIColors.END}")

    def __ai_make_move(self):
        board = self.__board_service.board_to_array()
        self.__ai.board = board

        if self.__players[1].pieces_on_board == 3 and self.__players[1].pieces_in_hand == 0:
            self.__ai.phase = "flying"

        ai_best_move, ai_best_remove = self.__ai.next_best_move()

        if ai_best_move[0] == "place":
            self.__ai_place(ai_best_move[1])
        elif ai_best_move[0] == "move":
            self.__ai_move(ai_best_move[1], ai_best_move[2])
            if self.__is_game_over():
                self.__game_over()

        if ai_best_remove is not None:
            self.__ai_remove(ai_best_remove[1])
            self.__switch_turn()
            self.__print_board_and_info()
            self.__print_pieces_in_hand()
            print(f"White piece at position {self.reverse_translate_piece(ai_best_remove[1])} was removed.")
        else:
            self.__switch_turn()
            self.__print_board_and_info()
            self.__print_pieces_in_hand()

    def __ai_move(self, start, end):
        ai = self.__players[1]
        if self.__players[1].pieces_on_board == 3 and self.__players[1].pieces_in_hand == 0:
            self.__board_service.move_flying(ai.color, start, end)
        else:
            self.__board_service.move(ai.color, start, end)

        is_mill = self.__board_service.mill(ai.color, end)

    def __ai_remove(self, position: int):
        self.__board_service.remove(Color.WHITE, position)

        self.__players[0].pieces_on_board -= 1

        if self.__is_game_over():
            self.__game_over()

    def __ai_place(self, position: int):
        ai = self.__players[1]
        self.__board_service.place(ai.color, position)

        ai.pieces_in_hand -= 1
        ai.pieces_on_board += 1

    def __piece_placing(self):
        print("----- GAME STARTED -----")
        self.__print_board_and_info()
        self.__print_pieces_in_hand()

        while True:
            next_phase = True
            for player in self.__players:
                if not player.pieces_in_hand == 0:
                    next_phase = False

            if next_phase:
                if self.__is_ai:
                    self.__ai.phase = "moving"
                self.__move_phase()

            if self.__is_ai and self.__players[self.__current_turn].color == Color.BLACK:
                self.__ai_make_move()
                continue

            option = input("Please select a position on the board: ")
            option = option.strip()
            if option == '':
                continue
            option = option.lower()
            try:
                position = self.translate_piece(option)
                self.__play_place_turn(position)

                if not self.__is_ai:
                    self.__print_board_and_info()
                    self.__print_pieces_in_hand()
            except ValueError as ve:
                print(f"{ANSIColors.RED}Error: {ve}{ANSIColors.END}")
            except BitBoardError as bbe:
                print(f"{ANSIColors.RED}Error: {bbe}{ANSIColors.END}")

    def __play_place_turn(self, position: int):
        player = self.__players[self.__current_turn]

        self.__board_service.place(player.color, position)
        player.pieces_in_hand -= 1
        player.pieces_on_board += 1

        if self.__board_service.mill(player.color, position):
            print(self.__board_service.highlighted_mill_board(player.color, position))
            if player.color == Color.WHITE:
                print(f"{ANSIColors.GREEN}{player.name}{ANSIColors.END} formed a mill!")
            else:
                print(f"{ANSIColors.RED}{player.name}{ANSIColors.END} formed a mill!")
            self.__play_remove_piece()

        self.__switch_turn()

    def __switch_turn(self):
        if self.__current_turn == 1:
            self.__current_turn = 0
        else:
            self.__current_turn = 1

    def __play_remove_piece(self):
        player = self.__players[self.__current_turn]
        if self.__current_turn == 1:
            opponent = self.__players[0]
        else:
            opponent = self.__players[1]

        while True:
            option = input("Which piece would you like to remove? ")
            option = option.strip()
            if option == '':
                continue
            option = option.lower()
            try:
                position = self.translate_piece(option)

                self.__board_service.remove(opponent.color, position)
                opponent.pieces_on_board -= 1
                return
            except ValueError as ve:
                print(f"{ANSIColors.RED}Error: {ve}{ANSIColors.END}")
            except BitBoardError as bbe:
                print(f"{ANSIColors.RED}Error: {bbe}{ANSIColors.END}")

    def __move_phase(self):
        print("----- ALL PIECES WERE PLACED -----")
        self.__print_board_and_info()
        while True:
            if self.__is_game_over():
                self.__game_over()

            if self.__is_ai and self.__players[self.__current_turn].color == Color.BLACK:
                self.__ai_make_move()
                continue

            start_option = input("Which piece would you like to move? ")
            end_option = input("Where would you like to move? ")

            start_option = start_option.strip()
            end_option = end_option.strip()

            if start_option == '' or end_option == '':
                continue

            start_option = start_option.lower()
            end_option = end_option.lower()
            try:
                start = self.translate_piece(start_option)
                end = self.translate_piece(end_option)
                self.__play_move_turn(start, end)
                if not self.__is_ai:
                    self.__print_board_and_info()
            except ValueError as ve:
                print(f"{ANSIColors.RED}Error: {ve}{ANSIColors.END}")
            except BitBoardError as bbe:
                print(f"{ANSIColors.RED}Error: {bbe}{ANSIColors.END}")
            except ValidationError as vae:
                print(f"{ANSIColors.RED}Error: {vae}{ANSIColors.END}")

    def __play_move_turn(self, start, end):
        player = self.__players[self.__current_turn]

        if player.pieces_on_board == 3:
            self.__board_service.move_flying(player.color, start, end)
        else:
            self.__board_service.move(player.color, start, end)

        if self.__board_service.mill(player.color, end):
            print(self.__board_service.highlighted_mill_board(player.color, end))
            if player.color == Color.WHITE:
                print(f"{ANSIColors.GREEN}{player.name}{ANSIColors.END} formed a mill!")
            else:
                print(f"{ANSIColors.RED}{player.name}{ANSIColors.END} formed a mill!")
            self.__play_remove_piece()

        self.__switch_turn()

    def __is_game_over(self) -> bool:
        if not self.__can_make_move(Color.WHITE) or not self.__can_make_move(Color.BLACK):
            return True
        for player in self.__players:
            if player.pieces_on_board < 3:
                return True
        return False

    def __can_make_move(self, color: Color) -> bool:
        player = next(p for p in self.__players if p.color == color)
        is_flying = player.pieces_on_board == 3
        positions = [x for x in range(24) if self.__board_service.occupied(x, color)]
        for position in positions:
            if self.__board_service.available_move(position, is_flying):
                return True
        return False

    def __game_over(self):
        if self.__players[0].pieces_on_board < 3:
            player = self.__players[1]
        elif self.__players[1].pieces_on_board < 3:
            player = self.__players[0]
        elif self.__can_make_move(self.__players[0].color):
            player = self.__players[0]
        else:
            player = self.__players[1]

        print(f"{player.name} has won the game!")

        exit(0)

    @staticmethod
    def translate_piece(position: str) -> int:
        piece_map = {
            "a0": 0,
            "d0": 1,
            "g0": 2,
            "b1": 3,
            "d1": 4,
            "f1": 5,
            "c2": 6,
            "d2": 7,
            "e2": 8,
            "a3": 9,
            "b3": 10,
            "c3": 11,
            "e3": 12,
            "f3": 13,
            "g3": 14,
            "c4": 15,
            "d4": 16,
            "e4": 17,
            "b5": 18,
            "d5": 19,
            "f5": 20,
            "a6": 21,
            "d6": 22,
            "g6": 23
        }
        if position in piece_map:
            return piece_map[position]
        raise ValueError("Invalid piece position!")

    @staticmethod
    def reverse_translate_piece(index: int) -> str:
        piece_map = {
            0: "a0",
            1: "d0",
            2: "g0",
            3: "b1",
            4: "d1",
            5: "f1",
            6: "c2",
            7: "d2",
            8: "e2",
            9: "a3",
            10: "b3",
            11: "c3",
            12: "e3",
            13: "f3",
            14: "g3",
            15: "c4",
            16: "d4",
            17: "e4",
            18: "b5",
            19: "d5",
            20: "f5",
            21: "a6",
            22: "d6",
            23: "g6"
        }
        if index in piece_map:
            return piece_map[index]