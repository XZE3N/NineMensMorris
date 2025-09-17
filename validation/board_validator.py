from exceptions import ValidationError


class BoardValidator:
    def __init__(self):
        self.adjacency = {
            0: [1, 9], 1: [0, 2, 4], 2: [1, 14],
            3: [4, 10], 4: [1, 3, 5, 7], 5: [4, 13],
            6: [7, 11], 7: [4, 6, 8], 8: [7, 12],
            9: [0, 10, 21], 10: [3, 9, 11, 18], 11: [6, 10, 15],
            12: [8, 13, 17], 13: [5, 12, 14, 20], 14: [2, 13, 23],
            15: [11, 16], 16: [15, 17, 19], 17: [12, 16],
            18: [10, 19], 19: [16, 18, 20, 22], 20: [13, 19],
            21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
        }

    @staticmethod
    def validate_position(position: int) -> None:
        """
        Checks if the given position is valid.
        Raises ValidationError if the position is not between 0 and 23.
        :param position: Int - The position to validate.
        :return: None.
        """
        if not (0 <= position <= 23):
            raise ValidationError('Position must be between 0 and 23!')

    def validate_adjacency(self, start: int, end: int) -> None:
        """
        Checks if two given positions are adjacent.
        :param start: Int - The starting position.
        :param end: Int - The ending position.
        :return: None.
        """
        if end not in self.adjacency.get(start, []):
            raise ValidationError('The two positions must be adjacent!')
