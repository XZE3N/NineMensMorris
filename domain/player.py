from domain.color import Color


class Player:
    def __init__(self, player_id: int, name: str, color: Color | None):
        self.__id = player_id
        self.__name = name
        self.__color = color
        self.__pieces_in_hand = 9
        self.__pieces_on_board = 0

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def color(self):
        return self.__color

    @name.setter
    def name(self, name):
        self.__name = name

    @color.setter
    def color(self, color):
        self.__color = color

    @property
    def pieces_in_hand(self):
        return self.__pieces_in_hand

    @property
    def pieces_on_board(self):
        return self.__pieces_on_board

    @pieces_in_hand.setter
    def pieces_in_hand(self, pieces_in_hand):
        self.__pieces_in_hand = pieces_in_hand

    @pieces_on_board.setter
    def pieces_on_board(self, pieces_on_board):
        self.__pieces_on_board = pieces_on_board

    def __eq__(self, other) -> bool:
        if isinstance(other, Player):
            return self.__id == other.__id and self.__name == other.__name and self.__color == other.__color

    def __repr__(self):
        return self.__name