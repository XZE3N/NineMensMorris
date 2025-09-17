from domain.color import Color
from exceptions import BitBoardError


class Board:
    def __init__(self):
        self.__black_pieces = 0
        self.__white_pieces = 0

        self.mills = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [9, 10, 11], [12, 13, 14], [15, 16, 17],
            [18, 19, 20], [21, 22, 23],
            [0, 9, 21], [3, 10, 18], [6, 11, 15],
            [1, 4, 7], [16, 19, 22], [8, 12, 17],
            [5, 13, 20], [2, 14, 23]
        ]

    def board_to_array(self) -> list:
        """
        Returns the board as a list, with 'W' for a white piece, 'B' for a black piece and None for empty positions.
        Used in conjunction with the NineMensMorrisAI function.
        :return: List.
        """
        board = [
            "B" if self.occupied(i, Color.BLACK)
            else "W" if self.occupied(i, Color.WHITE)
            else None for i in range(24)
        ]
        return board

    def occupied(self, position: int, color: Color = None) -> bool:
        """
        Method that determines if a position on the board is occupied. Color can be specified to check only the pieces of the specified color.
        :param position: Int - Position to be checked.
        :param color: Color - Color of the specified position.
        :return: Bool - True if the position is occupied, False otherwise.
        """
        if color is None:
            result = (self.__white_pieces | self.__black_pieces) & (1 << position)
        elif color == Color.BLACK:
            result = self.__black_pieces & (1 << position)
        else:
            result = self.__white_pieces & (1 << position)
        return bool(result)

    def place(self, color: Color, position: int) -> None:
        """
        Method that places a piece on the board.
        Raises BitBoardError if the position is occupied.
        :param color: Color - Color of the piece to be placed.
        :param position: Int - Position where the piece will be placed.
        :return: None.
        """
        if self.occupied(position):
            raise BitBoardError("Position is occupied!")
        if color == Color.WHITE:
            self.__white_pieces |= 1 << position
        else:
            self.__black_pieces |= 1 << position

    def remove(self, color: Color, position: int) -> None:
        """
        Method that removes a piece on the board.
        Raises BitBoardError if there is no piece at the specified position.
        :param color: Color - Color of the piece to be removed.
        :param position: Int - Position of the piece to be removed.
        :return: None.
        """
        if not self.occupied(position, color):
            if color == Color.BLACK:
                message_color = "black"
            else:
                message_color = "white"
            raise BitBoardError(f"No {message_color} piece at this position!")

        # If all the pieces form mills we allow the player to remove any one of them.
        positions = {pos for pos in range(24) if self.occupied(pos, color)}
        all_mills = all(self.mill(color, pos) for pos in positions)

        if self.mill(color, position) and not all_mills:
            raise BitBoardError("You cannot remove pieces that form a mill!")

        if color == Color.WHITE:
            self.__white_pieces &= ~(1 << position)
        else:
            self.__black_pieces &= ~(1 << position)

    def move(self, color: Color, start: int, end: int) -> None:
        """
        Method that moves a piece on the board.
        Raises BitBoardError if the end position is occupied or if the start position is empty.
        :param color: Color - Color of the piece to be moved.
        :param start: Int - Starting position of the piece to be moved.
        :param end: Int - Ending position of the piece to be moved.
        :return: None.
        """
        if not self.occupied(start, color):
            raise BitBoardError("No piece at starting position!")
        if self.occupied(end):
            raise BitBoardError("End position is occupied!")
        if color == Color.WHITE:
            self.__white_pieces &= ~(1 << start)
        else:
            self.__black_pieces &= ~(1 << start)
        self.place(color, end)

    def mill(self, color: Color, position: int) -> list | None:
        """
        Evaluate if a newly placed piece forms a mill using predefined mill patterns.
        :param color: Color - Color of the piece to be checked.
        :param position: Int - Position to be checked.
        :return: Bool - True if the newly placed piece forms a mill, False otherwise.
        """
        for mill in self.mills:
            if position in mill:
                ok = True
                for p in mill:
                    if not self.occupied(p, color):
                        ok = False
                if ok:
                    return mill
        return None
