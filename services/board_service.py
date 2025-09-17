from domain.board import Board
from domain.color import Color, ANSIColors
from validation.board_validator import BoardValidator


class BoardService:
    def __init__(self, board: Board, board_validator: BoardValidator):
        self.__board = board
        self.__board_validator = board_validator

    def board_to_array(self) -> list:
        """
        Returns the board as a list, with 'W' for a white piece, 'B' for a black piece and None for empty positions.
        Used in conjunction with the NineMensMorrisAI function.
        :return: List.
        """
        return self.__board.board_to_array()

    def occupied(self, position: int, color: Color = None) -> bool:
        """
        Method that determines if a position on the board is occupied. Color can be specified to check only the pieces of the specified color.
        :param position: Int - Position to be checked.
        :param color: Color - Color of the specified position.
        :return: Bool - True if the position is occupied, False otherwise.
        """
        self.__board_validator.validate_position(position)
        return self.__board.occupied(position, color)

    def place(self, color: Color, position: int) -> None:
        """
        Places a piece of a given color on the board.
        :param color: Color - Color of the piece.
        :param position: Int - Position where the piece will be placed.
        :return: None.
        """
        self.__board_validator.validate_position(position)
        self.__board.place(color, position)

    def remove(self, color: Color, position: int) -> None:
        """
        Removes a piece of a given color from the board.
        :param color: Color - Color of the piece.
        :param position: Int - Position of the piece to be removed.
        :return: None.
        """
        self.__board_validator.validate_position(position)
        self.__board.remove(color, position)

    def move(self, color: Color, start: int, end) -> None:
        """
        Moves a piece of a given color from the start position to the end position.
        :param color: Color - Color of the piece.
        :param start: Int - Initial position of the piece.
        :param end: Int - Position where the piece will be moved.
        :return: None.
        """
        self.__board_validator.validate_position(start)
        self.__board_validator.validate_position(end)
        self.__board_validator.validate_adjacency(start, end)
        self.__board.move(color, start, end)

    def move_flying(self, color: Color, start: int, end) -> None:
        """
        Moves a flying piece of a given color from the start position to the end position.
        :param color: Color - Color of the piece.
        :param start: Int - Initial position of the piece.
        :param end: Int - Position where the piece will be moved.
        :return: None.
        """
        self.__board_validator.validate_position(start)
        self.__board_validator.validate_position(end)
        self.__board.move(color, start, end)

    def mill(self, color: Color, position: int) -> list | None:
        """
        Evaluates if a newly placed piece of a given color forms a mill.
        :param color: Color - Color of the piece.
        :param position: Int - Position of the piece to be checked.
        :return: Bool - True if the piece forms a mill, False otherwise.
        """
        self.__board_validator.validate_position(position)
        return self.__board.mill(color, position)

    def available_move(self, position: int, flying: bool = False) -> list[int] | None:
        """
        Returns a list of available moves for the given position, or None if no available moves are found.
        :param position: Int - Position of the piece to be checked.
        :param flying: Bool - True if the piece is a flying piece, False otherwise.
        :return: List[Int] or None.
        """
        if flying is True:
            available_moves = [x for x in range(24) if not self.__board.occupied(x)]
            return available_moves if len(available_moves) > 0 else None
        adjacent_positions = self.__board_validator.adjacency[position]
        available_moves = [x for x in adjacent_positions if not self.__board.occupied(x)]
        return available_moves if len(available_moves) > 0 else None

    def available_remove(self, color: Color) -> list[int] | None:
        """
        Returns a list of available pieces of a given color that can be removed.
        :param color: Color - Color of the pieces.
        :return: List[int] or None.
        """
        all_mills = True
        for p in [x for x in range(24) if self.__board.occupied(x, color)]:
            if not self.__board.mill(color, p):
                all_mills = False
        if all_mills:
            available_moves = [x for x in range(24) if self.__board.occupied(x, color)]
        else:
            available_moves = [x for x in range(24) if
                               self.__board.occupied(x, color) and not self.__board.mill(color, x)]
        return available_moves if len(available_moves) > 0 else None

    def highlighted_mill_board(self, color: Color, position: int) -> str | None:
        """
        Returns the board as a string with the mill at 'position' highlighted.
        :param color: Color - Color of the pieces.
        :param position: Int - Position of the piece to be checked.
        :return: Str - The board as a string.
        """
        self.__board_validator.validate_position(position)
        for mill in self.__board.mills:
            if position in mill:
                ok = True
                for p in mill:
                    if not self.__board.occupied(p, color):
                        ok = False
                if ok:
                    return self.__highlighted_string(mill)
        return None

    def __get_piece_at(self, position: int) -> str:
        """
        Helper method used for displaying the board to the console.
        Returns 'W' alongside ANSI color escape sequences for a white piece.
        Returns 'B' alongside ANSI color escape sequences for a black piece.
        Returns '0' for an empty position on the board.
        :param position: Int - Position to be checked.
        :return: String - The corresponding string.
        """
        if self.__board.occupied(position, Color.WHITE):
            return f"{ANSIColors.GREEN}W{ANSIColors.END}"
        if self.__board.occupied(position, Color.BLACK):
            return f"{ANSIColors.RED}B{ANSIColors.END}"
        return "0"

    def __get_piece_at_with_highlighting(self, position: int, highlighting: list) -> str:
        """
        Helper method used for displaying the highlighted board to the console.
        Returns 'W' alongside ANSI color escape sequences for a white piece.
        Returns 'B' alongside ANSI color escape sequences for a black piece.
        Returns '0' for an empty position on the board.
        :param position: Int - Position to be checked.
        :return: String - The corresponding string.
        """
        if self.__board.occupied(position, Color.WHITE):
            if position in highlighting:
                return f"{ANSIColors.YELLOW}W{ANSIColors.END}"
            return f"{ANSIColors.GREEN}W{ANSIColors.END}"
        if self.__board.occupied(position, Color.BLACK):
            if position in highlighting:
                return f"{ANSIColors.YELLOW}B{ANSIColors.END}"
            return f"{ANSIColors.RED}B{ANSIColors.END}"
        return "0"

    def board(self) -> str:
        """
        Returns the board as a string.
        :return: Str - The board as a string.
        """
        string = (f"""
        6   {self.__get_piece_at(21)}-------------{self.__get_piece_at(22)}-------------{self.__get_piece_at(23)}
            |             |             |
        5   |    {self.__get_piece_at(18)}--------{self.__get_piece_at(19)}--------{self.__get_piece_at(20)}    |
            |    |        |        |    |
        4   |    |    {self.__get_piece_at(15)}---{self.__get_piece_at(16)}---{self.__get_piece_at(17)}    |    |
            |    |    |       |    |    |
        3   {self.__get_piece_at(9)}----{self.__get_piece_at(10)}----{self.__get_piece_at(11)}       {self.__get_piece_at(12)}----{self.__get_piece_at(13)}----{self.__get_piece_at(14)}
            |    |    |       |    |    |
        2   |    |    {self.__get_piece_at(6)}---{self.__get_piece_at(7)}---{self.__get_piece_at(8)}    |    |
            |    |        |        |    |
        1   |    {self.__get_piece_at(3)}--------{self.__get_piece_at(4)}--------{self.__get_piece_at(5)}    |
            |             |             |
        0   {self.__get_piece_at(0)}-------------{self.__get_piece_at(1)}-------------{self.__get_piece_at(2)}

            a    b    c   d   e    f    g 
        """)
        return string

    def __highlighted_string(self, highlights):
        """
        Returns the highlighted board as a string.
        :return: Str - The board as a string.
        """
        string = (f"""
        6   {self.__get_piece_at_with_highlighting(21, highlights)}-------------{self.__get_piece_at_with_highlighting(22, highlights)}-------------{self.__get_piece_at_with_highlighting(23, highlights)}
            |             |             |
        5   |    {self.__get_piece_at_with_highlighting(18, highlights)}--------{self.__get_piece_at_with_highlighting(19, highlights)}--------{self.__get_piece_at_with_highlighting(20, highlights)}    |
            |    |        |        |    |
        4   |    |    {self.__get_piece_at_with_highlighting(15, highlights)}---{self.__get_piece_at_with_highlighting(16, highlights)}---{self.__get_piece_at_with_highlighting(17, highlights)}    |    |
            |    |    |       |    |    |
        3   {self.__get_piece_at_with_highlighting(9, highlights)}----{self.__get_piece_at_with_highlighting(10, highlights)}----{self.__get_piece_at_with_highlighting(11, highlights)}       {self.__get_piece_at_with_highlighting(12, highlights)}----{self.__get_piece_at_with_highlighting(13, highlights)}----{self.__get_piece_at_with_highlighting(14, highlights)}
            |    |    |       |    |    |
        2   |    |    {self.__get_piece_at_with_highlighting(6, highlights)}---{self.__get_piece_at_with_highlighting(7, highlights)}---{self.__get_piece_at_with_highlighting(8, highlights)}    |    |
            |    |        |        |    |
        1   |    {self.__get_piece_at_with_highlighting(3, highlights)}--------{self.__get_piece_at_with_highlighting(4, highlights)}--------{self.__get_piece_at_with_highlighting(5, highlights)}    |
            |             |             |
        0   {self.__get_piece_at_with_highlighting(0, highlights)}-------------{self.__get_piece_at_with_highlighting(1, highlights)}-------------{self.__get_piece_at_with_highlighting(2, highlights)}

            a    b    c   d   e    f    g 
        """)
        return string

    def __str__(self):
        return self.board()

    def __repr__(self):
        return self.board()
