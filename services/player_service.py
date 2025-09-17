from domain.color import Color
from domain.player import Player
from exceptions import ServiceError
from repository.player_repository import PlayerRepository
from validation.player_validator import PlayerValidator


class PlayerService:
    def __init__(self, player_repository: PlayerRepository, player_validator: PlayerValidator):
        self.__player_repository = player_repository
        self.__player_validator = player_validator

    def add(self, player_id: int, name: str, color: Color) -> None:
        """
        Adds a player to the list of players.
        :param player_id: Int - Id of the player to be added.
        :param name: Str - Name of the player.
        :param color: Color - Color of the player.
        :return: None.
        """
        player = Player(player_id, name, color)
        self.__player_validator.validate_player(player)
        self.__player_repository.add(player)

    def update_color(self, player_id: int, color: Color) -> None:
        """
        Updates the color of a given player.
        :param player_id: Int - Id of the player to be updated.
        :param color: Color - New color of the player.
        :return: None.
        """
        player = self.__player_repository.get(player_id)
        if not player:
            raise ServiceError("A player with the specified Id could not be found!")
        player.color = color
        self.__player_validator.validate_player(player)
        self.__player_repository.update(player)

    def update_name(self, player_id: int, name: str) -> None:
        """
        Updates the name of a given player.
        :param player_id: Int - Id of the player to be updated.
        :param name: Str - New name of the player.
        :return: None.
        """
        player = self.__player_repository.get(player_id)
        if not player:
            raise ServiceError("A player with the specified Id could not be found!")
        player.name = name
        self.__player_validator.validate_player(player)
        self.__player_repository.update(player)

    def remove(self, player_id: int) -> None:
        """
        Removes a player from the list of players.
        :param player_id: Int - Id of the player to be removed.
        :return: None.
        """
        self.__player_repository.remove(player_id)

    def get_all(self) -> list[Player]:
        """
        Returns a list of all players.
        :return: List[Player] - List of all players.
        """
        return self.__player_repository.get_all()

    def get(self, player_id: int) -> Player | None:
        """
        Retrieves the player with the given id.
        :param player_id: Int - Id of the player to be retrieved.
        :return: Player or None - The player to be retrieved.
        """
        return self.__player_repository.get(player_id)
