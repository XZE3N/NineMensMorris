import random
import threading
import time
import tkinter as tk
from tkinter import messagebox
from playsound import playsound

from domain.color import Color
from exceptions import ValidationError, BitBoardError
from services.ai import NineMensMorrisAI


class NineMensMorrisGUI:
    def __init__(self, root, players, board_service):
        self.__root = root
        self.__players = players
        self.__board_service = board_service

        self.__current_turn = 0
        self.__game_phase = "placing"
        self.__former_game_phase = "placing"
        self.__start_position = None

        self.__root.title("Nine Men’s Morris")
        self.__root.iconbitmap("ico/icon.ico")

        # Get the board positions
        self.__positions = self.__get_positions()

        # Figure out if the player is going against the computer
        self.__is_ai = True if self.__players[1].id == -1 else False

        self.__ai = NineMensMorrisAI() if self.__is_ai else None
        self.__ai_thinking = False

        # Create canvas for the game board
        self.__canvas = tk.Canvas(root, width=560, height=500, bg="white")
        self.__canvas.grid(row=0, column=0, columnspan=3)

        self.__turn_label = tk.Label(root, text=f"{self.__players[self.__current_turn].name}'s turn",
                                     font=("Arial", 14))
        self.__turn_label.grid(row=1, column=0, padx=50, pady=20, sticky="w")

        # Draw the board
        self.__draw_board(9, 9)

        root.update_idletasks()  # Ensures the window is updated to its final size

        # Get the window dimensions
        window_width = root.winfo_width()
        window_height = root.winfo_height()

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate position x, y
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set the geometry of the window
        root.geometry(f"+{x}+{y}")

        # Bind mouse click
        self.__canvas.bind("<Button-1>", self.__handle_click)

    def __draw_piece(self, x: int, y: int, color: str = None):
        radius = 3 if color is None else 15
        fill_color = "black" if color is None else color
        outline_color = "black" if color is None else "#333"
        self.__canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, outline=outline_color, fill=fill_color
        )
        # Style the piece
        radius -= 3
        accent = {
            "white": "#ccc",
            "black": "#333",
            "gold": "#ffffa1",
            "#98fb98": "#4ef84e",
            "#fb9898": "#f96767"
        }
        if color in accent:
            self.__canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, outline=accent[color], width=2
            )

    def __draw_pieces(self, highlight=None, secondary_highlight=None, removing=False):
        highlight = [] if not highlight else highlight
        secondary_highlight = [] if not secondary_highlight else secondary_highlight
        for i in range(24):
            x, y = self.__positions[i]
            if i in highlight:
                self.__draw_piece(x, y, "gold")
                continue
            if i in secondary_highlight and removing:
                self.__draw_piece(x, y, "#fb9898")
                continue
            if i in secondary_highlight:
                self.__draw_piece(x, y, "#98fb98")
                continue
            if not self.__board_service.occupied(i):
                self.__draw_piece(x, y)
                continue
            if self.__board_service.occupied(i, Color.WHITE):
                self.__draw_piece(x, y, "white")
            else:
                self.__draw_piece(x, y, "black")

    def __draw_board(self, white_pieces, black_pieces, highlight=None, secondary_highlight=None, removing=False):
        # Clear the canvas
        self.__canvas.delete("all")

        # Draw the squares
        self.__canvas.create_rectangle(50, 50, 450, 450, outline="black", fill="#FFF0C1", width=1)
        self.__canvas.create_rectangle(115, 115, 385, 385, outline="black", width=1)
        self.__canvas.create_rectangle(180, 180, 320, 320, outline="black", width=1)

        # Draw connecting lines
        self.__canvas.create_line(50, 250, 180, 250, fill="black", width=1)
        self.__canvas.create_line(250, 50, 250, 180, fill="black", width=1)
        self.__canvas.create_line(320, 250, 450, 250, fill="black", width=1)
        self.__canvas.create_line(250, 320, 250, 450, fill="black", width=1)

        # Draw pieces
        self.__draw_pieces(highlight, secondary_highlight, removing)

        # Draw piece storage
        self.__canvas.create_oval(490, 50, 530, 90, outline="#202020", fill="#555", width=1)
        self.__canvas.create_oval(490, 185, 530, 225, outline="#202020", fill="#555", width=1)
        self.__canvas.create_rectangle(490, 70, 530, 205, outline="#202020", fill="#555", width=1)
        self.__canvas.create_rectangle(491, 70, 529, 205, outline="#555", fill="#555",
                                       width=1)  # Clean up rectangle border

        self.__canvas.create_oval(490, 275, 530, 315, outline="#202020", fill="#555", width=1)
        self.__canvas.create_oval(490, 410, 530, 450, outline="#202020", fill="#555", width=1)
        self.__canvas.create_rectangle(490, 295, 530, 430, outline="#202020", fill="#555", width=1)
        self.__canvas.create_rectangle(491, 295, 529, 430, outline="#555", fill="#555", width=1)

        y = 73
        for i in range(white_pieces):
            self.__draw_piece(510, y, "white")
            y += 16

        y = 298
        for i in range(black_pieces):
            self.__draw_piece(510, y, "black")
            y += 16

    def __highlight_move(self, start, end):
        xs, ys = self.__positions[start]
        xe, ye = self.__positions[end]
        highlights = [
            self.__canvas.create_oval(xs - 16, ys - 16, xs + 16, ys + 16, outline="#444", width=3),
            self.__canvas.create_oval(xe - 16, ye - 16, xe + 16, ye + 16, outline="#444", width=3)
        ]

        self.__canvas.after(400, self.__remove_highlight, highlights)

    def __highlight_place(self, position):
        x, y = self.__positions[position]
        highlights = [self.__canvas.create_oval(x - 16, y - 16, x + 16, y + 16, outline="#444", width=3)]
        self.__canvas.after(400, self.__remove_highlight, highlights)

    def __warn_move(self, position):
        x, y = self.__positions[position]
        highlights = []

        if not self.__board_service.occupied(position):
            highlights.append(self.__canvas.create_oval(x - 15, y - 15, x + 15, y + 15, outline="#333", fill="#fb9898"))
            highlights.append(self.__canvas.create_oval(x - 12, y - 12, x + 12, y + 12, outline="#f96767", width=2))
            self.__canvas.after(300, self.__remove_highlight, highlights)
            return

        highlights.append(self.__canvas.create_oval(x - 16, y - 16, x + 16, y + 16, outline="#f96767", width=3))

        # Remove the highlights after 300 ms
        self.__canvas.after(300, self.__remove_highlight, highlights)

    def __remove_highlight(self, highlights):
        for highlight in highlights:
            self.__canvas.delete(highlight)

    def __update_board_and_info(self, highlight=None, secondary_highlight=None, removing=False):
        player_one = self.__players[0]
        player_two = self.__players[1]
        self.__draw_board(player_one.pieces_in_hand, player_two.pieces_in_hand, highlight, secondary_highlight,
                          removing)
        self.__turn_label["text"] = f"{self.__players[self.__current_turn].name}'s turn"

    def __play_place(self, event, position):
        next_phase = True
        for player in self.__players:
            if not player.pieces_in_hand == 0:
                next_phase = False
        if next_phase:
            self.__game_phase = "moving"
            if self.__is_ai:
                self.__ai.phase = "moving"
            self.__handle_click(event)
            return
        try:
            self.__play_place_turn(position)
        except ValueError:
            self.__warn_move(position)
        except BitBoardError:
            self.__warn_move(position)
        except ValidationError:
            self.__warn_move(position)

    def __play_move(self, position):
        player = self.__players[self.__current_turn]

        if self.__start_position is None and not self.__board_service.occupied(position, player.color):
            self.__update_board_and_info()
            self.__warn_move(position)
            return

        if self.__start_position is not None and self.__board_service.occupied(position):
            if position == self.__start_position:
                self.__start_position = None
                self.__update_board_and_info()
                return

            if self.__board_service.occupied(position, player.color):
                self.__start_position = position
                is_flying = player.pieces_on_board == 3
                available_positions = self.__board_service.available_move(position, is_flying)
                self.__update_board_and_info([position], available_positions)
                return

            self.__start_position = None
            self.__update_board_and_info()
            self.__warn_move(position)
            return

        if self.__start_position is None:
            self.__start_position = position
            is_flying = player.pieces_on_board == 3
            available_positions = self.__board_service.available_move(position, is_flying)
            self.__update_board_and_info([position], available_positions)
        else:
            try:
                self.__play_move_turn(self.__start_position, position)

                if self.__is_game_over():
                    self.__game_over()
            except ValueError:
                self.__update_board_and_info()
                self.__warn_move(position)
            except BitBoardError:
                self.__update_board_and_info()
                self.__warn_move(position)
            except ValidationError:
                self.__update_board_and_info()
                self.__warn_move(position)
            self.__start_position = None

    def __play_remove(self, position):
        opponent = self.__get_opponent()
        try:
            self.__board_service.remove(opponent.color, position)

            opponent.pieces_on_board -= 1
            self.__game_phase = self.__former_game_phase

            if self.__is_game_over():
                self.__update_board_and_info()
                self.__game_over()

            self.__switch_turn()
            self.__update_board_and_info()
            self.__play_capture_sound()
        except ValueError:
            self.__warn_move(position)
        except BitBoardError:
            self.__warn_move(position)
        except ValidationError:
            self.__warn_move(position)

    def __handle_click(self, event):
        if self.__ai_thinking:  # Block player input while AI is thinking
            return

        clicked_position = self.__get_nearest_position(event.x, event.y)
        if not clicked_position:
            return

        position = self.__positions.index(clicked_position)

        if self.__game_phase == "placing":
            self.__play_place(event, position)

        elif self.__game_phase == "removing":
            self.__play_remove(position)

        elif self.__game_phase == "moving":

            self.__play_move(position)

        if self.__is_ai and self.__players[self.__current_turn].color == Color.BLACK:
            self.__ai_make_move()


    def __play_move_turn(self, start, end):
        player = self.__players[self.__current_turn]

        if player.pieces_on_board == 3:
            self.__board_service.move_flying(player.color, start, end)
        else:
            self.__board_service.move(player.color, start, end)

        is_mill = self.__board_service.mill(player.color, end)
        if is_mill:
            opponent = self.__get_opponent()
            available_positions = self.__board_service.available_remove(opponent.color)
            self.__update_board_and_info(is_mill, available_positions, True)
            self.__game_phase = "removing"
            self.__former_game_phase = "moving"
            self.__play_mill_sound()
            return

        self.__switch_turn()
        self.__update_board_and_info()
        self.__play_move_sound()

    def __is_game_over(self) -> bool:
        if not self.__can_make_move(Color.WHITE) or not self.__can_make_move(Color.BLACK):
            return True
        for player in self.__players:
            if player.pieces_on_board < 3 and player.pieces_in_hand == 0:
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
        self.__play_victory_sound()

        if self.__players[0].pieces_on_board < 3:
            player = self.__players[1]
        elif self.__players[1].pieces_on_board < 3:
            player = self.__players[0]
        elif self.__can_make_move(self.__players[0].color):
            player = self.__players[0]
        else:
            player = self.__players[1]

        messagebox.showinfo("Game Over", f"{player.name} has won the game!")
        self.__root.destroy()
        exit(0)

    def __play_place_turn(self, position: int):
        player = self.__players[self.__current_turn]

        self.__board_service.place(player.color, position)

        player.pieces_in_hand -= 1
        player.pieces_on_board += 1

        is_mill = self.__board_service.mill(player.color, position)
        if is_mill:
            opponent = self.__get_opponent()
            available_positions = self.__board_service.available_remove(opponent.color)
            self.__update_board_and_info(is_mill, available_positions, True)
            self.__game_phase = "removing"
            self.__former_game_phase = "placing"
            self.__play_mill_sound()
            return

        self.__switch_turn()
        self.__update_board_and_info()
        self.__play_move_sound()

    def __get_opponent(self):
        return self.__players[0] if self.__current_turn == 1 else self.__players[1]

    def __switch_turn(self):
        self.__current_turn += 1
        self.__current_turn %= len(self.__players)

    def __ai_make_move(self):
        self.__ai_thinking = True

        board = self.__board_service.board_to_array()
        self.__ai.board = board

        if self.__players[1].pieces_on_board == 3 and self.__players[1].pieces_in_hand == 0:
            self.__ai.phase = "flying"

        ai_best_move, ai_best_remove = self.__ai.next_best_move()

        def ai_actions():  # Wrap AI actions in a thread-safe block
            try:
                time.sleep(random.uniform(1, 2))  # Simulate thinking with a random delay
                if ai_best_move[0] == "place":
                    self.__ai_place(ai_best_move[1])
                elif ai_best_move[0] == "move":
                    self.__ai_move(ai_best_move[1], ai_best_move[2])
                    if self.__is_game_over():
                        self.__update_board_and_info()
                        self.__game_over()

                if ai_best_remove is not None:
                    self.__update_board_and_info()
                    time.sleep(random.uniform(1, 2))  # Simulate thinking with a random delay
                    self.__ai_remove(ai_best_remove[1])
            finally:
                self.__ai_thinking = False

                self.__update_board_and_info()

                if ai_best_move[0] == "move":
                    pass
                    #self.__highlight_move(ai_best_move[1], ai_best_move[2])
                if ai_best_move[0] == "place":
                    self.__highlight_place(ai_best_move[1])

                if ai_best_remove is not None:
                    self.__warn_move(ai_best_remove[1])

        threading.Thread(target=ai_actions, daemon=True).start()
        self.__switch_turn()

    def __ai_move(self, start, end):
        ai = self.__players[1]
        if self.__players[1].pieces_on_board == 3 and self.__players[1].pieces_in_hand == 0:
            self.__board_service.move_flying(ai.color, start, end)
        else:
            self.__board_service.move(ai.color, start, end)

        is_mill = self.__board_service.mill(ai.color, end)
        if is_mill:
            self.__play_mill_sound()
            return

        self.__highlight_move(start, end)
        self.__play_move_sound()

    def __ai_remove(self, position: int):
        self.__board_service.remove(Color.WHITE, position)

        self.__players[0].pieces_on_board -= 1

        if self.__is_game_over():
            self.__update_board_and_info()
            self.__game_over()

        self.__play_capture_sound()

    def __ai_place(self, position: int):
        ai = self.__players[1]
        self.__board_service.place(ai.color, position)

        ai.pieces_in_hand -= 1
        ai.pieces_on_board += 1

        is_mill = self.__board_service.mill(ai.color, position)
        if is_mill:
            self.__play_mill_sound()
            return

        self.__play_move_sound()

    def __get_nearest_position(self, x, y):
        for pos in self.__positions:
            px, py = pos
            if (px - x) ** 2 + (py - y) ** 2 <= 20 ** 2:
                return pos
        return None

    @staticmethod
    def __get_positions():
        return [
            (50, 450), (250, 450), (450, 450),  # Bottom row
            (115, 385), (250, 385), (385, 385),  # Middle bottom row
            (180, 320), (250, 320), (320, 320),  # Top bottom row
            (50, 250), (115, 250), (180, 250), (320, 250), (385, 250), (450, 250),  # Center row
            (180, 180), (250, 180), (320, 180),  # Bottom top row
            (115, 115), (250, 115), (385, 115),  # Middle top row
            (50, 50), (250, 50), (450, 50),  # Top row
        ]

    @staticmethod
    def __play_move_sound():
        threading.Thread(target=playsound, args=('audio/move.wav',), daemon=True).start()

    @staticmethod
    def __play_capture_sound():
        threading.Thread(target=playsound, args=('audio/capture.wav',), daemon=True).start()

    @staticmethod
    def __play_mill_sound():
        threading.Thread(target=playsound, args=('audio/notify.wav',), daemon=True).start()

    @staticmethod
    def __play_victory_sound():
        threading.Thread(target=playsound, args=('audio/victory.wav',), daemon=True).start()
