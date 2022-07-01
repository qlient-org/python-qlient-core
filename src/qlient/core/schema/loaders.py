"""This file contains the loader functions for the graphql schema"""
import logging
from typing import Dict, Optional

from qlient.core import __meta__
from qlient.core._types import RawSchema
from qlient.core.caches import Cache
from qlient.core.schema.providers import SchemaProvider, AsyncSchemaProvider

logger = logging.getLogger(__meta__.__title__)


def load_schema(provider: SchemaProvider, cache: Optional[Cache]) -> RawSchema:
    """Load the schema from the given provider

    Args:
        provider: holds either None or the schema provider
        cache: holds the cache that contains the schema

    Returns:
        the schema
    """
    schema: Optional[Dict] = (
        cache.get(provider.schema_cache_key) if cache is not None else None
    )
    if schema is not None:
        # if schema is not None, this means that the cache is also not None.
        # Therefore, it is safe to access to cache properties
        logger.debug(
            f"Returning schema `{provider.schema_cache_key}` from cache `{cache.__class__.__name__}`"
        )
        return schema

    logger.debug(f"Using schema from provider `{provider}`")
    schema = provider.load_schema()

    if cache is not None:
        logger.debug(
            f"Caching schema in `{cache.__class__.__name__}` for future usage with key `{provider.schema_cache_key}`"
        )
        cache[provider.schema_cache_key] = schema

    return schema


async def load_schema_async(
    provider: AsyncSchemaProvider, cache: Optional[Cache]
) -> RawSchema:
    """Load the schema from the given provider

    Args:
        provider: holds either None or the schema provider
        cache: holds the cache that contains the schema

    Returns:
        the schema
    """
    schema: Optional[Dict] = (
        cache.get(provider.schema_cache_key) if cache is not None else None
    )
    if schema is not None:
        # if schema is not None, this means that the cache is also not None.
        # Therefore, it is safe to access to cache properties
        logger.debug(
            f"Returning schema `{provider.schema_cache_key}` from cache `{cache.__class__.__name__}`"
        )
        return schema

    logger.debug(f"Using schema from provider `{provider}`")
    schema = await provider.load_schema()

    if cache is not None:
        logger.debug(
            f"Caching schema in `{cache.__class__.__name__}` for future usage with key `{provider.schema_cache_key}`"
        )
        cache[provider.schema_cache_key] = schema

    return schema
