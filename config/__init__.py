class Config:
    def __init__(self, settings_file: str = "settings.properties"):
        self.__settings = {}
        self.__load_settings(settings_file)

    @property
    def settings(self):
        return self.__settings

    def __load_settings(self, path: str) -> None:
        """
        Reads the settings file and stores key-value pairs in the settings dictionary.
        Raises FileNotFoundError if the file was not found.
        Raises ValueError if the file format is not supported.
        :param path: String - Name of the settings file.
        :return: None.
        """
        try:
            with open(path, "r") as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        self.__settings[key.strip()] = value.strip()

        except FileNotFoundError:
            raise FileNotFoundError(f"Settings file '{path}' not found.")

        except ValueError:
            raise ValueError(
                f"Invalid format in settings file '{path}'. Each line must be in 'key=value' format.")