"""This file contains all qlient specific exceptions"""
from typing import Dict


class QlientException(Exception):
    """Base class for qlient exceptions"""


class SchemaException(QlientException):
    """Indicates that something is wrong regarding the graphql schema"""

    def __init__(self, schema: Dict, *args):
        self.schema: Dict = schema
        super(SchemaException, self).__init__(*args)


class SchemaParseException(SchemaException):
    """This exception gets thrown when the parser was unable to parse the graphql schema"""


class NoTypesFound(SchemaParseException):
    """Indicates that the schema does not have any types defined"""


class OutOfAsyncContext(QlientException):
    """Indicates that you are running out of an async context"""
