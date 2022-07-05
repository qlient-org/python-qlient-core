"""This file contains the settings that can be overwritten in the qlient Client"""


class Settings:
    """Class that represents the settings that can be adjusted to your liking"""

    def __init__(
        self,
        validate_variables: bool = True,
    ):
        self.validate_variables: bool = validate_variables

    def __str__(self) -> str:
        """Return a simple string representation of the settings"""
        return repr(self)

    def __repr__(self) -> str:
        """Return a detailed string representation of the settings"""
        class_name = self.__class__.__name__
        return f"{class_name}()"
