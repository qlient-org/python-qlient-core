import logging
import typing

from qlient.core import __meta__
from qlient.core._types import RawSchema
from qlient.core.schema.models import Type, Directive
from qlient.core.schema.parser import parse_schema, ParseResult

logger = logging.getLogger(__meta__.__title__)

SchemaProviderType = typing.Type["SchemaProvider"]


class Schema:
    """Represents a graphql schema"""

    def __init__(
        self,
        raw_schema: RawSchema,
        provider: SchemaProviderType,
    ):
        self.raw_schema: RawSchema = raw_schema
        self.schema_provider: SchemaProviderType = provider

        parse_result: ParseResult = parse_schema(self.raw_schema)

        self.query_type: typing.Optional[Type] = parse_result.query_type
        self.mutation_type: typing.Optional[Type] = parse_result.mutation_type
        self.subscription_type: typing.Optional[Type] = parse_result.subscription_type
        self.types_registry: typing.Dict[str, Type] = parse_result.types
        self.directives_registry: typing.Dict[str, Directive] = parse_result.directives
        logger.debug("Schema successfully introspected")

    def __eq__(self, other: "Schema"):
        return (
            self.raw_schema == other.raw_schema
            and self.schema_provider == other.schema_provider
        )

    def __getattr__(self, key) -> typing.Optional[Type]:
        return self[key]

    def __getitem__(self, key) -> typing.Optional[Type]:
        return self.types_registry.get(key)

    def __str__(self) -> str:
        """Return a simple string representation of the schema instance"""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the schema instance"""
        class_name = self.__class__.__name__
        return (
            f"<{class_name}("
            f"query_type={self.query_type}, "
            f"mutation_type={self.mutation_type}, "
            f"subscription_type={self.subscription_type})>"
        )
