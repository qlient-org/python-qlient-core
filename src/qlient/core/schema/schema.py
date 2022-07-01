import logging
from typing import Optional, Dict

from qlient.core import __meta__
from qlient.core._types import RawSchema
from qlient.core.caches import Cache
from qlient.core.schema.loaders import load_schema, load_schema_async
from qlient.core.schema.models import Type, Directive
from qlient.core.schema.parser import parse_schema, ParseResult
from qlient.core.schema.providers import SchemaProvider, AsyncSchemaProvider
from qlient.core.settings import Settings

logger = logging.getLogger(__meta__.__title__)


class Schema:
    """Represents a graphql schema"""

    @classmethod
    def load(
        cls,
        provider: SchemaProvider,
        settings: Optional[Settings],
        cache: Optional[Cache],
    ) -> "Schema":
        """Class method to load the schema synchronously

        Args:
            provider: holds the schema provider
            settings: holds the client settings
            cache: holds the cache to use

        Returns:
            A introspected and ready to use schema
        """
        raw_schema: RawSchema = load_schema(provider, cache)
        parse_result: ParseResult = parse_schema(raw_schema)
        return cls(parse_result, provider, settings, cache)

    @classmethod
    async def load_async(
        cls,
        provider: AsyncSchemaProvider,
        settings: Optional[Settings],
        cache: Optional[Cache],
    ) -> "Schema":
        """Class method to load the schema asynchronously

        Args:
            provider: holds the schema provider
            settings: holds the client settings
            cache: holds the cache to use

        Returns:
            A introspected and ready to use schema
        """
        raw_schema: RawSchema = await load_schema_async(provider, cache)
        parse_result: ParseResult = parse_schema(raw_schema)
        return cls(parse_result, provider, settings, cache)

    def __init__(
        self,
        parse_result,
        provider: SchemaProvider,
        settings: Optional[Settings] = None,
        cache: Optional[Cache] = None,
    ):
        self.schema_provider: SchemaProvider = provider
        self.settings: Settings = settings or Settings()
        self.cache: Optional[Cache] = cache

        self.query_type: Optional[Type] = parse_result.query_type
        self.mutation_type: Optional[Type] = parse_result.mutation_type
        self.subscription_type: Optional[Type] = parse_result.subscription_type
        self.types_registry: Dict[str, Type] = parse_result.types
        self.directives_registry: Dict[str, Directive] = parse_result.directives
        logger.debug("Schema successfully introspected")

    def __getattr__(self, key) -> Optional[Type]:
        return self[key]

    def __getitem__(self, key) -> Optional[Type]:
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
