"""This file contains the settings that can be overwritten in the qlient Client"""


class Settings:
    """Class that represents the settings that can be adjusted to your liking"""

    def __init__(
        self,
        use_schema_description: bool = True,
        allow_auto_lookup: bool = True,
        lookup_recursion_depth: int = 1,
    ):
        self.use_schema_description: bool = use_schema_description
        self.allow_auto_lookup: bool = allow_auto_lookup
        self.lookup_recursion_depth: int = lookup_recursion_depth

    def __str__(self) -> str:
        """Return a simple string representation of the settings"""
        return repr(self)

    def __repr__(self) -> str:
        """Return a detailed string representation of the settings"""
        class_name = self.__class__.__name__
        return (
            f"<{class_name}("
            f"use_schema_description={self.use_schema_description}, "
            f"allow_auto_lookup={self.allow_auto_lookup}, "
            f"lookup_recursion_depth={self.lookup_recursion_depth}"
            f")>"
        )
