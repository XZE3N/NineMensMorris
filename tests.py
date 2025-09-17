import unittest

from domain.board import Board
from domain.color import Color, ANSIColors
from domain.player import Player
from exceptions import BitBoardError, ValidationError, RepositoryError, ServiceError
from repository.player_repository import PlayerRepository
from services.ai import NineMensMorrisAI
from services.board_service import BoardService
from services.player_service import PlayerService
from validation.board_validator import BoardValidator
from validation.player_validator import PlayerValidator


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.white_position = 16
        self.black_position = 17
        self.move_end_position = 12
        self.mill_position = 15

    def test_empty(self):
        # Initially all the positions should be vacant
        for i in range(24):
            result = self.board.occupied(i)
            self.assertFalse(result)

    def test_board_to_array(self):
        self.board.place(Color.WHITE, 0)
        self.board.place(Color.WHITE, 1)
        self.board.place(Color.WHITE, 2)

        board = self.board.board_to_array()

        actual_board = [None] * 24
        actual_board[0] = 'W'
        actual_board[1] = 'W'
        actual_board[2] = 'W'

        self.assertEqual(board, actual_board)

    def test_place(self):
        self.board.place(Color.WHITE, self.white_position)

        for i in range(24):
            result = self.board.occupied(i, Color.WHITE)
            if i != self.white_position:
                self.assertFalse(result)
            else:
                self.assertTrue(result)

        self.board.place(Color.BLACK, self.black_position)

        for i in range(24):
            result = self.board.occupied(i, Color.BLACK)
            if i != self.black_position:
                self.assertFalse(result)
            else:
                self.assertTrue(result)

        with self.assertRaises(BitBoardError) as cm:
            self.board.place(Color.WHITE, self.white_position)
        exception = cm.exception
        self.assertEqual(str(exception), "Position is occupied!")

    def test_remove(self):
        self.board.place(Color.WHITE, self.white_position)

        self.board.place(Color.BLACK, self.black_position)

        self.board.remove(Color.WHITE, self.white_position)
        self.assertFalse(self.board.occupied(self.white_position))

        self.board.remove(Color.BLACK, self.black_position)
        self.assertFalse(self.board.occupied(self.black_position))

        with self.assertRaises(BitBoardError) as cm:
            self.board.remove(Color.WHITE, self.white_position)
        exception = cm.exception
        self.assertEqual(str(exception), "No white piece at this position!")

        self.board.place(Color.WHITE, 0)
        self.board.place(Color.WHITE, 1)
        self.board.place(Color.WHITE, 2)
        self.board.place(Color.WHITE, 3)

        with self.assertRaises(BitBoardError) as cm:
            self.board.remove(Color.WHITE, 0)
        exception = cm.exception
        self.assertEqual(str(exception), "You cannot remove pieces that form a mill!")

    def test_move(self):
        self.board.place(Color.WHITE, self.white_position)

        self.board.place(Color.BLACK, self.black_position)

        with self.assertRaises(BitBoardError) as cm:
            self.board.move(Color.WHITE, self.white_position, self.black_position)
        exception = cm.exception
        self.assertEqual(str(exception), "End position is occupied!")

        self.board.remove(Color.BLACK, self.black_position)

        with self.assertRaises(BitBoardError) as cm:
            self.board.move(Color.WHITE, self.black_position, self.move_end_position)
        exception = cm.exception
        self.assertEqual(str(exception), "No piece at starting position!")

        self.board.move(Color.WHITE, self.white_position, self.move_end_position)
        self.assertFalse(self.board.occupied(self.white_position))
        self.assertTrue(self.board.occupied(self.move_end_position, Color.WHITE))

        self.board.place(Color.BLACK, self.black_position)

        self.board.move(Color.BLACK, self.black_position, self.white_position)
        self.assertFalse(self.board.occupied(self.black_position))
        self.assertTrue(self.board.occupied(self.white_position, Color.BLACK))

    def test_mill(self):
        result = self.board.mill(Color.WHITE, self.white_position)
        self.assertFalse(result)

        result = self.board.mill(Color.BLACK, 24)
        self.assertFalse(result)

        self.board.place(Color.WHITE, 0)
        self.board.place(Color.WHITE, 9)
        self.board.place(Color.WHITE, 21)
        self.assertTrue(self.board.mill(Color.WHITE, 0))

        self.board.place(Color.WHITE, 3)
        self.board.place(Color.WHITE, 10)
        self.board.place(Color.WHITE, 18)
        self.assertTrue(self.board.mill(Color.WHITE, 18))

        self.board.place(Color.WHITE, 5)
        self.board.place(Color.WHITE, 13)
        self.board.place(Color.WHITE, 20)
        self.assertTrue(self.board.mill(Color.WHITE, 13))

        self.board.place(Color.WHITE, 2)
        self.board.place(Color.WHITE, 14)
        self.board.place(Color.WHITE, 23)
        self.assertTrue(self.board.mill(Color.WHITE, 2))


class TestBoardValidator(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board_validator = BoardValidator()

    def test_validate_position(self):
        with self.assertRaises(ValidationError) as cm:
            self.board_validator.validate_position(-1)
        exception = cm.exception
        self.assertEqual(str(exception), "Position must be between 0 and 23!")

        with self.assertRaises(ValidationError) as cm:
            self.board_validator.validate_position(24)
        exception = cm.exception
        self.assertEqual(str(exception), "Position must be between 0 and 23!")

    def test_validate_adjacency(self):
        with self.assertRaises(ValidationError) as cm:
            self.board_validator.validate_adjacency(1, 5)
        exception = cm.exception
        self.assertEqual(str(exception), "The two positions must be adjacent!")

        with self.assertRaises(ValidationError) as cm:
            self.board_validator.validate_adjacency(21, 19)
        exception = cm.exception
        self.assertEqual(str(exception), "The two positions must be adjacent!")


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player_id = 1
        self.name = "Andrei"
        self.color = Color.BLACK

        self.new_name = "Miau"
        self.new_color = Color.WHITE

    def test_init(self):
        player = Player(self.player_id, self.name, self.color)
        self.assertEqual(player.id, self.player_id)
        self.assertEqual(player.name, self.name)
        self.assertEqual(player.color, self.color)

    def test_setters(self):
        player = Player(self.player_id, self.name, self.color)
        player.name = self.new_name
        self.assertEqual(player.name, self.new_name)
        player.color = self.new_color
        self.assertEqual(player.color, self.new_color)

    def test_pieces_counters(self):
        player = Player(self.player_id, self.name, self.color)
        self.assertEqual(player.pieces_in_hand, 9)
        self.assertEqual(player.pieces_on_board, 0)

        player.pieces_in_hand -= 1
        player.pieces_on_board += 1
        self.assertEqual(player.pieces_on_board, 1)
        self.assertEqual(player.pieces_in_hand, 8)


class TestPlayerValidator(unittest.TestCase):
    def setUp(self):
        self.player_validator = PlayerValidator()
        self.player = Player(1, "Andrei", Color.BLACK)
        self.invalid_player = Player(-2, "", Color.WHITE)

    def test_validate_player(self):
        self.player_validator.validate_player(self.player)

        with self.assertRaises(ValidationError) as cm:
            self.player_validator.validate_player(self.invalid_player)
        exception = cm.exception
        self.assertEqual(str(exception), "Invalid Id! Invalid Name! ")


class TestPlayerRepository(unittest.TestCase):
    def setUp(self):
        self.player_repository = PlayerRepository("data/test_players.pkl")
        self.player = Player(1, "Andrei", Color.BLACK)

    def test_add_update_delete(self):
        self.player_repository.add(self.player)
        found_player = self.player_repository.get(self.player.id)
        self.assertEqual(found_player, self.player)

        with self.assertRaises(RepositoryError) as cm:
            self.player_repository.add(self.player)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id already exists!")

        self.player_repository.update(Player(self.player.id, "Miau", self.player.color))
        found_player = self.player_repository.get(self.player.id)
        self.assertEqual(found_player.name, "Miau")

        self.player_repository.remove(self.player.id)

        found_player = self.player_repository.get(self.player.id)
        self.assertEqual(found_player, None)

        with self.assertRaises(RepositoryError) as cm:
            self.player_repository.update(Player(self.player.id, "Miau", self.player.color))
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id could not be found!")

        with self.assertRaises(RepositoryError) as cm:
            self.player_repository.remove(self.player.id)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id could not be found!")

    def test_get_all(self):
        self.player_repository.add(self.player)

        players = self.player_repository.get_all()
        self.assertEqual(players[-1], self.player)

        self.player_repository.remove(self.player.id)


class TestPlayerService(unittest.TestCase):
    def setUp(self):
        self.player_repository = PlayerRepository("data/test_players.pkl")
        self.player_validator = PlayerValidator()
        self.player_service = PlayerService(self.player_repository, self.player_validator)
        self.player = Player(1, "Andrei", Color.BLACK)

    def test_add_update_delete(self):
        self.player_service.add(self.player.id, self.player.name, self.player.color)
        found_player = self.player_service.get(self.player.id)
        self.assertEqual(found_player, self.player)

        with self.assertRaises(RepositoryError) as cm:
            self.player_service.add(self.player.id, self.player.name, self.player.color)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id already exists!")

        self.player_service.update_name(self.player.id, "Miau")
        found_player = self.player_service.get(self.player.id)
        self.assertEqual(found_player.name, "Miau")

        self.player_service.update_color(self.player.id, Color.WHITE)
        found_player = self.player_service.get(self.player.id)
        self.assertEqual(found_player.color, Color.WHITE)

        self.player_service.remove(self.player.id)
        found_player = self.player_service.get(self.player.id)
        self.assertEqual(found_player, None)

        with self.assertRaises(RepositoryError) as cm:
            self.player_service.remove(self.player.id)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id could not be found!")

        with self.assertRaises(ServiceError) as cm:
            self.player_service.update_color(self.player.id, Color.WHITE)
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id could not be found!")

        with self.assertRaises(ServiceError) as cm:
            self.player_service.update_name(self.player.id, "Miau")
        the_exception = cm.exception
        self.assertEqual(str(the_exception), "A player with the specified Id could not be found!")

    def test_get_all(self):
        self.player_service.add(self.player.id, self.player.name, self.player.color)

        players = self.player_service.get_all()
        self.assertEqual(players[-1], self.player)

        self.player_service.remove(self.player.id)


class TestBoardService(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board_validator = BoardValidator()
        self.board_service = BoardService(self.board, self.board_validator)
        self.white_position = 16
        self.black_position = 17
        self.move_end_position = 19
        self.mill_position = 15

    def test_board_to_array(self):
        self.board_service.place(Color.WHITE, 0)
        self.board_service.place(Color.WHITE, 1)
        self.board_service.place(Color.WHITE, 2)

        board = self.board_service.board_to_array()

        actual_board = [None] * 24
        actual_board[0] = 'W'
        actual_board[1] = 'W'
        actual_board[2] = 'W'

        self.assertEqual(board, actual_board)

    def test_occupied(self):
        self.board_service.place(Color.WHITE, 0)
        self.assertTrue(self.board_service.occupied(0, Color.WHITE))
        self.board_service.remove(Color.WHITE, 0)
        self.assertFalse(self.board_service.occupied(0, Color.WHITE))

    def test_place(self):
        self.board_service.place(Color.WHITE, self.white_position)

        for i in range(24):
            result = self.board.occupied(i, Color.WHITE)
            if i != self.white_position:
                self.assertFalse(result)
            else:
                self.assertTrue(result)

    def test_remove(self):
        self.board_service.place(Color.BLACK, self.black_position)
        self.board_service.remove(Color.BLACK, self.black_position)
        self.assertFalse(self.board.occupied(self.black_position))

        with self.assertRaises(BitBoardError) as cm:
            self.board_service.remove(Color.BLACK, self.black_position)
        exception = cm.exception
        self.assertEqual(str(exception), "No black piece at this position!")

    def test_move(self):
        self.board_service.place(Color.WHITE, self.white_position)
        self.board_service.move(Color.WHITE, self.white_position, self.move_end_position)
        self.assertFalse(self.board.occupied(self.white_position))
        self.assertTrue(self.board.occupied(self.move_end_position, Color.WHITE))

    def test_move_flying(self):
        self.board_service.place(Color.WHITE, self.white_position)
        self.board_service.move_flying(Color.WHITE, self.white_position, 23)
        self.assertFalse(self.board.occupied(self.white_position))
        self.assertTrue(self.board.occupied(23, Color.WHITE))

    def test_board_highlighting(self):
        self.board_service.place(Color.WHITE, 0)
        self.board_service.place(Color.WHITE, 1)
        self.board_service.place(Color.WHITE, 2)
        self.board_service.place(Color.BLACK, 3)
        self.board_service.place(Color.WHITE, 4)

        str(self.board_service)
        repr(self.board_service)

        self.board_service.highlighted_mill_board(Color.WHITE, 2)
        self.board_service.highlighted_mill_board(Color.WHITE, 22)
        self.board_service.board()

        self.board_service.place(Color.BLACK, 9)
        self.board_service.place(Color.BLACK, 10)
        self.board_service.place(Color.BLACK, 11)
        self.board_service.highlighted_mill_board(Color.BLACK, 10)

    def test_mill(self):
        self.board_service.place(Color.WHITE, self.white_position)
        self.board_service.place(Color.WHITE, self.black_position)
        self.board_service.place(Color.WHITE, self.mill_position)
        result = self.board_service.mill(Color.WHITE, self.mill_position)
        self.assertTrue(result)

    def test_available_move(self):
        self.board_service.place(Color.WHITE, 1)
        positions = self.board_service.available_move(1)
        self.assertTrue(positions, [0, 2, 4])

        positions = self.board_service.available_move(1, True)
        self.assertTrue(positions, [i for i in range(24) if i != 1])

    def test_available_remove(self):
        self.board_service.place(Color.WHITE, 0)
        self.board_service.place(Color.WHITE, 1)
        self.board_service.place(Color.WHITE, 2)
        self.board_service.place(Color.WHITE, 3)

        positions = self.board_service.available_remove(Color.WHITE)
        self.assertTrue(positions, [3])

        self.board_service.remove(Color.WHITE, 3)
        positions = self.board_service.available_remove(Color.WHITE)
        self.assertTrue(positions, [0, 1, 2])


class TestAI(unittest.TestCase):
    def setUp(self):
        self.ai = NineMensMorrisAI()

    def test_place(self):
        self.ai.phase = "placing"
        self.ai.board = ['W', 'W', None, None, None, None, None, None, None, 'B', 'W', None, None, None, 'W', 'B', None,
                         None, None, 'W', None, 'B', 'B', 'W']
        best_move, best_remove = self.ai.next_best_move()
        self.assertEqual(best_move, ('place', 2))

    def test_move(self):
        self.ai.phase = "moving"
        self.ai.board = ['W', 'W', None, None, None, None, None, None, None, 'B', 'W', None, None, None, 'W', 'B', None,
                         None, None, 'W', None, 'B', 'B', 'W']
        best_move, best_remove = self.ai.next_best_move()
        self.assertEqual(best_move, ('move', 15, 11))

    def test_flying(self):
        self.ai.phase = "flying"
        self.ai.board = ['W', 'W', 'W', 'B', 'B', 'B', 'B', 'B', None, 'B', 'B', 'B', None, None, None, None, None,
                         None, None, None, None, None, None, 'B']
        best_move, best_remove = self.ai.next_best_move()
        self.assertEqual(best_move, ('move', 3, 8))
        self.assertEqual(best_remove, ('remove', 1))


if __name__ == "__main__":
    unittest.main()
