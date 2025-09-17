from domain.player import Player
from exceptions import ValidationError


class PlayerValidator:
    @staticmethod
    def validate_player(player: Player) -> None:
        """
        Raises ValidationError if the player is not valid.
        :param player: Player - Player object to validate.
        :return: None.
        """
        errors = ""
        if player.id < 0:
            errors += "Invalid Id! "
        if player.name == "":
            errors += "Invalid Name! "
        if len(errors) > 0:
            raise ValidationError(errors)
