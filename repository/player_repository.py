import pickle

from domain.player import Player
from exceptions import RepositoryError


class PlayerRepository:
    def __init__(self, file_path: str):
        self.__players = {}
        self.__path = file_path

        with open(self.__path, "rb") as file:
            if file.read(1):
                self.__load_from_file()

    def add(self, player: Player) -> None:
        """
        Adds a player to the repository.
        Raises RepositoryError if the player already exists.
        :param player: Player - The player to be added.
        :return: None.
        """
        if self.get(player.id):
            raise RepositoryError('A player with the specified Id already exists!')
        self.__players[player.id] = player
        self.__save_to_file()

    def update(self, player: Player) -> None:
        """
        Updates a player in the repository.
        Raises RepositoryError if the player does not exist.
        :param player: Player - The player to be updated.
        :return: None.
        """
        if not self.get(player.id):
            raise RepositoryError('A player with the specified Id could not be found!')
        self.__players[player.id] = player
        self.__save_to_file()

    def remove(self, player_id: int) -> None:
        """
        Removes a player from the repository.
        Raises RepositoryError if the player does not exist.
        :param player_id: Int - Id of the player to be removed.
        :return: None.
        """
        if not self.get(player_id):
            raise RepositoryError('A player with the specified Id could not be found!')
        del self.__players[player_id]
        self.__save_to_file()

    def get(self, player_id: int) -> Player | None:
        """
        Retrieves a player from the repository.
        :param player_id: Int - Id of the player to be retrieved.
        :return: None or Player - The player to be retrieved.
        """
        return self.__players.get(player_id)

    def get_all(self) -> list[Player]:
        """
        Retrieves all players from the repository.
        :return: List[Player] - List of all players.
        """
        return list(self.__players.values())

    def __load_from_file(self) -> None:
        """
        Loads all the players from the file.
        :return: None.
        """
        with open(self.__path, "rb") as file:
            self.__players = pickle.load(file)

    def __save_to_file(self) -> None:
        """
        Saves all the players to the file.
        :return: None.
        """
        with open(self.__path, "wb") as file:
            pickle.dump(self.__players, file)
