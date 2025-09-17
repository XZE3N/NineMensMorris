import math


class NineMensMorrisAI:
    def __init__(self):
        self.board = [None] * 24

        # Can be "placing", "moving", or "flying"
        self.phase = "placing"

    '''
    When the AI is about to lose in the next two moves due to lack a of available moves, 
    the next_move function will return None although there is a free piece at the current
    depth that can be moved. This is a very particular and hard to recreate case (in-game).
    
    * See this board configuration for more:
    board = ['W', 'W', None, None, None, None, None, None, None, 'B', 'W', None,
             None, None, 'W', 'B', None, None, None, 'W', None, 'B', 'B', 'W']
    * Every black piece is blocked except for one, but black's move is redundant as white
    will win next turn because of the open mill at [0, 1, 14].
    '''

    def is_mill(self, position: int, color: str) -> bool:
        """
        Evaluates if a piece of a given color forms a mill.
        :param position: Int - Position of the piece to be checked.
        :param color: Color - Color of the piece.
        :return: Bool - True if the piece forms a mill, False otherwise.
        """
        mills = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
            [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23],
            [0, 9, 21], [3, 10, 18], [6, 11, 15], [1, 4, 7],
            [16, 19, 22], [8, 12, 17], [5, 13, 20], [2, 14, 23]
        ]
        for mill in mills:
            if position in mill and all(self.board[pos] == color for pos in mill):
                return True
        return False

    def generate_moves(self, color: str) -> list[tuple]:
        """
        Generates all possible moves for a given color as a list of tuples.
        ("move", start, end), ("place", position).
        :param color: String - Color of the pieces.
        :return: List[tuple].
        """
        moves = []
        if self.phase == "placing":
            for i in range(24):
                if self.board[i] is None:
                    moves.append(("place", i))

        elif self.phase in ["moving", "flying"]:
            for i in range(24):
                if self.board[i] == color:
                    if self.phase == "flying":
                        for j in range(24):
                            if self.board[j] is None:
                                moves.append(("move", i, j))
                    else:
                        for neighbor in self.get_neighbors(i):
                            if self.board[neighbor] is None:
                                moves.append(("move", i, neighbor))
        return moves

    @staticmethod
    def get_neighbors(position: int) -> list[int]:
        """
        Returns a list containing the neighbouring positions for a given position.
        :param position: Int - Position to be checked.
        :return: List[int].
        """
        neighbors = {
            0: [1, 9], 1: [0, 2, 4], 2: [1, 14], 3: [4, 10],
            4: [1, 3, 5, 7], 5: [4, 13], 6: [7, 11], 7: [4, 6, 8],
            8: [7, 12], 9: [0, 10, 21], 10: [3, 9, 11, 18], 11: [6, 10, 15],
            12: [8, 13, 17], 13: [5, 12, 14, 20], 14: [2, 13, 23], 15: [11, 16],
            16: [15, 17, 19], 17: [12, 16], 18: [10, 19], 19: [16, 18, 20, 22],
            20: [13, 19], 21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
        }
        return neighbors[position]

    def apply_move(self, move: tuple, color: str | None) -> None:
        """
        Applies the given move to the board.
        :param move: Tuple - Move to be applied.
        :param color: String - Color of the pieces.
        :return: None.
        """
        if move[0] == "place":
            self.board[move[1]] = color
        elif move[0] == "move":
            self.board[move[1]] = None
            self.board[move[2]] = color
        elif move[0] == "remove":
            self.board[move[1]] = None

    def undo_move(self, move: tuple, color: str | None) -> None:
        """
        Undoes the given move.
        :param move: Tuple - Move to be undone.
        :param color: String - Color of the pieces.
        :return: None.
        """
        if move[0] == "place":
            self.board[move[1]] = None
        elif move[0] == "move":
            self.board[move[2]] = None
            self.board[move[1]] = color
        elif move[0] == "remove":
            self.board[move[1]] = color

    def get_removal_candidates(self, color: str) -> list[tuple]:
        """
        Returns a list of tuples (moves) containing the removal candidates for a given color.
        :param color: String - Color of the pieces.
        :return: List[tuple].
        """
        candidates = []
        for i in range(24):
            if self.board[i] == color and not self.is_mill(i, color):
                candidates.append(("remove", i))

        # If all pieces are in mills, allow removing any piece
        if not candidates:
            for i in range(24):
                if self.board[i] == color:
                    candidates.append(("remove", i))
        return candidates

    def evaluate(self) -> int:
        """
        Evaluation function for the minimax algorithm. Uses advanced heuristics to determine the best score.
        :return: Int - The static evaluation of the board.
        """

        black_score = 0
        white_score = 0

        black_on_board = self.board.count('B')
        white_on_board = self.board.count('W')

        # Material advantage: number of pieces on the board
        black_score += black_on_board * 5
        white_score += white_on_board * 5

        # Mobility: number of available moves
        black_moves = len(self.generate_moves('B'))
        white_moves = len(self.generate_moves('W'))

        black_score += black_moves * 5
        white_score += white_moves * 5

        # Mills: Mills obtained
        black_mills = 0
        white_mills = 0
        for i in self.board:
            if i is not None:
                if self.is_mill(i, "W"):
                    white_mills += 1
                elif self.is_mill(i, "B"):
                    black_mills += 1
        black_score += black_mills * 100
        white_score += white_mills * 100

        # Board control: central positions or connected spots
        central_positions = [1, 4, 7, 10, 13, 16, 19, 22]
        for pos in central_positions:
            if self.board[pos] == 'B':
                pass
                black_score += 1
            elif self.board[pos] == 'W':
                pass
                white_score += 1

        # Final score
        return black_score - white_score

    def minimax(self, depth: int, maximizing_player: bool, alpha: int = -math.inf, beta: int = math.inf) -> tuple:
        """
        Minimax algorithm for the Nine Men's Morris, with alpha-beta pruning.
        Determines the best available move for the given depth.
        Black is the maximizer and white is the minimizer.
        :param depth: Int - Depth the algorithm should search at.
        :param maximizing_player: Bool - Whether the player is maximizing or minimizing.
        :param alpha: Int - Alpha value for pruning.
        :param beta: Int - Beta value for pruning.
        :return: Tuple - Best value, best move, best remove candidate.
        """
        if depth == 0:
            return self.evaluate(), None, None  # Evaluation, best_move, best_remove

        color = 'B' if maximizing_player else 'W'
        opponent = 'W' if maximizing_player else 'B'

        best_value = -math.inf if maximizing_player else math.inf

        best_move = None
        best_remove = None

        # Generate the moves
        moves = self.generate_moves(color)

        # Return a neutral evaluation that does not have an impact on the recursion
        if len(moves) == 0:
            return 0, None, None
            # return math.inf if maximizing_player else -math.inf, None, None

        for move in moves:
            self.apply_move(move, color)

            forms_mill = False
            if self.phase == "placing" and self.is_mill(move[1], color):
                forms_mill = True
            if self.phase in ["moving", "flying"] and self.is_mill(move[2], color):
                forms_mill = True

            if forms_mill:
                remove_candidates = self.get_removal_candidates(opponent)
                for remove in remove_candidates:
                    self.apply_move(remove, opponent)
                    value, _, _ = self.minimax(depth - 1, not maximizing_player, alpha, beta)
                    self.undo_move(remove, opponent)

                    if maximizing_player:
                        if value > best_value:
                            best_value = value
                            best_move = move
                            best_remove = remove
                        alpha = max(alpha, best_value)
                    else:
                        if value < best_value:
                            best_value = value
                            best_move = move
                            best_remove = remove
                        beta = min(beta, best_value)

                    # Alpha-beta pruning
                    if beta <= alpha:
                        self.undo_move(move, color)
                        return best_value, best_move, best_remove
            else:
                value, _, _ = self.minimax(depth - 1, not maximizing_player, alpha, beta)

                if maximizing_player:
                    if value > best_value:
                        best_value = value
                        best_move = move
                        best_remove = None
                    alpha = max(alpha, best_value)
                else:
                    if value < best_value:
                        best_value = value
                        best_move = move
                        best_remove = None
                    beta = min(beta, best_value)

            # Undo the current move after evaluation
            self.undo_move(move, color)

            # Alpha-beta pruning
            if beta <= alpha:
                break

        return best_value, best_move, best_remove

    def next_best_move(self) -> tuple:
        """
        Function that returns the next best move on the board for black.
        :return: Tuple - Best move, best remove candidate.
        """
        _, move, remove = self.minimax(3, True)
        return move, remove
