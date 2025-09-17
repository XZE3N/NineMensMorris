import tkinter as tk
from tkinter import ttk, messagebox

from domain.board import Board
from domain.color import Color
from domain.player import Player
from exceptions import ServiceError, ValidationError
from services.board_service import BoardService
from ui.game_gui import NineMensMorrisGUI
from validation.board_validator import BoardValidator


class PlayerSelectionWindow:
    def __init__(self, root, player_service):
        self.root = root
        self.player_service = player_service

        self.root.title("Player Selection")
        self.root.iconbitmap("ico/icon.ico")

        # Add padding around the window
        self.root.configure(padx=30, pady=10)

        # Get the list of players
        self.players_list = self.player_service.get_all()

        # Append the AI to the second list
        self.ai_players_list = self.players_list.copy()
        self.ai_players_list.append('AI')

        # Create a custom style
        style = ttk.Style()

        # Set the internal padding for the Combobox
        style.configure('TCombobox', padding=(10, 10))

        # Player 1 Selection
        tk.Label(root, text="Player 1:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, sticky="w",
                                                                  pady=(10, 2))
        self.player1_selection = ttk.Combobox(root, values=self.players_list, style="TCombobox", font=("Arial", 12),
                                              width=30, state="readonly")
        self.player1_selection.set("Select player")  # Default text
        self.player1_selection.grid(row=1, column=0, columnspan=2, sticky="w")

        # Player 2 Selection
        tk.Label(root, text="Player 2:", font=("Arial", 12)).grid(row=2, column=0, columnspan=2, sticky="w",
                                                                  pady=(10, 2))
        self.player2_selection = ttk.Combobox(root, values=self.ai_players_list, style="TCombobox", font=("Arial", 12),
                                              width=30, state="readonly")
        self.player2_selection.set("Select player")
        self.player2_selection.grid(row=3, column=0, columnspan=2, sticky="w")

        # Add font to combobox
        root.option_add('*TCombobox*Listbox.font', ('Arial', '12'))

        # Add Player Button
        add_player_button = tk.Button(root, text="Add New Player", command=self.open_add_player_window,
                                      font=("Arial", 12), bg="pale green", fg="black", relief="flat",
                                      activebackground="#4ef84e", activeforeground="black")
        add_player_button.grid(row=4, column=0, pady=(20, 10), ipadx=10, ipady=5, sticky="w")

        # Remove Player Button
        remove_player_button = tk.Button(root, text="Remove Player", command=self.open_remove_player_window,
                                         font=("Arial", 12), bg="salmon", fg="black", relief="flat",
                                         activebackground="#ff511d", activeforeground="black")
        remove_player_button.grid(row=4, column=1, pady=(20, 10), ipadx=10, ipady=5, sticky="e")

        # Start Game Button
        start_button = tk.Button(root, text="Start Game", command=self.start_game, font=("Arial", 12), bg="light gray",
                                 fg="black", relief="flat", activebackground="gray", activeforeground="black")
        start_button.grid(row=5, column=0, columnspan=2, pady=(10, 20), ipadx=10, ipady=5, sticky="ew")

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

    def open_remove_player_window(self):
        remove_player_window = tk.Toplevel(self.root)

        remove_player_window.title("Remove Player")
        remove_player_window.iconbitmap("ico/icon.ico")
        remove_player_window.configure(padx=30, pady=20)

        tk.Label(remove_player_window, text="Select a Player:", font=("Arial", 12)).grid(row=0, column=0, sticky="w",
                                                                                         pady=(0, 2))
        player_box = ttk.Combobox(remove_player_window, values=self.players_list, font=("Arial", 12), width=20,
                                  style="TCombobox", state="readonly")
        player_box.set("Select player")
        player_box.grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Delete Button for removing player
        remove_button = tk.Button(remove_player_window, text="Remove Player",
                                  command=lambda: self.remove_player(player_box, remove_player_window),
                                  font=("Arial", 12), bg="light gray", fg="black", relief="flat",
                                  activebackground="gray", activeforeground="black")
        remove_button.grid(row=2, column=0, sticky="ew", pady=10, ipadx=10, ipady=5)

    def remove_player(self, player_box, remove_player_window):
        if player_box.get() == "Select player":
            messagebox.showerror("Error", "Please select a valid player!")
            remove_player_window.destroy()
            return

        player_index = player_box.current()
        player = self.players_list[player_index]

        try:
            self.player_service.remove(player.id)
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            remove_player_window.destroy()
            return
        except ServiceError as se:
            messagebox.showerror("Error", str(se))
            remove_player_window.destroy()
            return
        except ValidationError as vae:
            messagebox.showerror("Error", str(vae))
            remove_player_window.destroy()
            return

        messagebox.showinfo("Success", f"Player '{player}' was removed!")

        self.players_list = self.player_service.get_all()

        # Append the AI to the second list
        self.ai_players_list = self.players_list.copy()
        self.ai_players_list.append('AI')

        self.player1_selection["values"] = self.players_list
        self.player2_selection["values"] = self.ai_players_list
        remove_player_window.destroy()

    def open_add_player_window(self):
        add_player_window = tk.Toplevel(self.root)

        add_player_window.title("Add New Player")
        add_player_window.iconbitmap("ico/icon.ico")
        add_player_window.configure(padx=30, pady=20)

        tk.Label(add_player_window, text="Enter Player Name:", font=("Arial", 12)).grid(pady=(0, 2), row=0, column=0,
                                                                                        sticky="w")
        name_entry = tk.Entry(add_player_window, font=("Arial", 12))
        name_entry.grid(row=1, column=0, pady=(0, 10), ipady=5, sticky="ew", ipadx=10)

        # Save Button for adding player
        save_button = tk.Button(add_player_window, text="Save",
                                command=lambda: self.save_player(name_entry, add_player_window), font=("Arial", 12),
                                bg="light gray", fg="black", relief="flat", activebackground="gray",
                                activeforeground="black")
        save_button.grid(row=2, column=0, sticky="ew", pady=10, ipadx=10, ipady=5)

    def save_player(self, name_entry, add_player_window):
        new_player = name_entry.get().strip()
        try:
            if len(self.player_service.get_all()) == 0:
                player_id = 1
            else:
                player_id = self.player_service.get_all()[-1].id + 1
            self.player_service.add(player_id, new_player, Color.WHITE)
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            add_player_window.destroy()
            return
        except ServiceError as se:
            messagebox.showerror("Error", str(se))
            add_player_window.destroy()
            return
        except ValidationError as vae:
            messagebox.showerror("Error", str(vae))
            add_player_window.destroy()
            return

        messagebox.showinfo("Success", f"Player '{new_player}' added!")

        self.players_list = self.player_service.get_all()

        # Append the AI to the second list
        self.ai_players_list = self.players_list.copy()
        self.ai_players_list.append('AI')

        self.player1_selection["values"] = self.players_list
        self.player2_selection["values"] = self.ai_players_list
        add_player_window.destroy()

    def start_game(self):
        if self.player1_selection.get() == "Select player" or self.player2_selection.get() == "Select player":
            tk.messagebox.showerror("Error", "Please select both players before starting the game!")
            return

        ai = True if self.player2_selection.get() == "AI" else False

        player_one_index = self.player1_selection.current()
        if not ai:
            player_two_index = self.player2_selection.current()
            if player_one_index == player_two_index:
                tk.messagebox.showerror("Error", "The two players can not be the same!")
                return

        # Retrieve the two players from the player list
        player_one = self.players_list[player_one_index]

        if not ai:
            player_two_index = self.player2_selection.current()
            player_two = self.players_list[player_two_index]
        else:
            player_two = Player(-1, "AI", None)

        # Assign the colors to the players
        player_one.color = Color.WHITE
        player_two.color = Color.BLACK

        # Close the player selection window
        self.root.destroy()

        # Launch the main game
        root = tk.Tk()

        board = Board()
        board_validator = BoardValidator()
        board_service = BoardService(board, board_validator)

        players = [player_one, player_two]

        app = NineMensMorrisGUI(root, players, board_service)
        root.mainloop()
