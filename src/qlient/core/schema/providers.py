"""This module contains different schema providers"""
import abc
import io
import logging
import pathlib
from typing import Union, IO

from qlient.core import __meta__
from qlient.core.backends import Backend
from qlient.core.models import GraphQLRequest
from qlient.core.schema.schema import Schema

logger = logging.getLogger(__meta__.__title__)


class SchemaProvider(abc.ABC):
    """Super class for all schema providers

    This makes it easy to create your own schema provider anytime.
    See the implementations below for a quick overview.
    """

    @abc.abstractmethod
    def load_schema(self) -> Schema:
        """Abstract method to load the schema.

        This function gets called in order to load the schema from the source.
        Note that this function is not called with any arguments.

        Returns:
            The raw schema in it's json form
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def schema_cache_key(self) -> str:
        """A key that uniquely identifies the schema for a specific backend in the cache

        For example this can be a unique url or hostname.
        Or even a static key if the schema remains the same for the backend.

        Returns:
            a string that uniquely identifies the schema
        """
        raise NotImplementedError


class FileSchemaProvider(SchemaProvider):
    """Schema provider to read the schema from the file."""

    def __init__(self, file: Union[str, pathlib.Path, IO, io.IOBase]):
        filepath = None
        if isinstance(file, str):
            file = pathlib.Path(file)
        if isinstance(file, pathlib.Path):
            filepath = str(file.resolve())
            file = file.open("r")
        self.filepath: str = filepath or file.name
        self.file = file

    def load_schema(self) -> Schema:
        """Method to load the schema from the local file

        Returns:
            the schema from the file
        """
        logger.debug(f"Reading local schema from `{self.file}`")
        import json

        raw_schema = json.load(self.file)
        return Schema.from_raw(self, raw_schema)

    @property
    def schema_cache_key(self) -> str:
        """Property to return the cache key that uniquely identifies this schema.

        This uses the absolute filepath as cache key.

        Returns:
            the absolute filepath
        """
        return self.filepath


class BackendSchemaProvider(SchemaProvider):
    """Schema provider to read the schema using the backend.

    This provider uses an introspection query to load the schema directly from the backend.

    NOTE! This only works when the graphql backend has allowed introspection.
    """

    backend: Backend  # just a type hint

    INTROSPECTION_OPERATION_NAME = "IntrospectionQuery"
    INTROSPECTION_QUERY = """
            query IntrospectionQuery {
              __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                  ...FullType
                }
                directives {
                  name
                  description
                  locations
                  args {
                    ...InputValue
                  }
                }
              }
            }
            fragment FullType on __Type {
              kind
              name
              description
              fields(includeDeprecated: true) {
                name
                description
                args {
                  ...InputValue
                }
                type {
                  ...TypeRef
                }
                isDeprecated
                deprecationReason
              }
              inputFields {
                ...InputValue
              }
              interfaces {
                ...TypeRef
              }
              enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
              }
              possibleTypes {
                ...TypeRef
              }
            }
            fragment InputValue on __InputValue {
              name
              description
              type { ...TypeRef }
              defaultValue
            }
            fragment TypeRef on __Type {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                        ofType {
                          kind
                          name
                          ofType {
                            kind
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """

    def __init__(self, backend: Backend):
        self.backend: Backend = backend

    def load_schema(self) -> Schema:
        """Send the introspection query to the backend and return the given schema

        Returns:
            the given schema from the backend.
        """
        logger.debug(f"Loading remote schema using `{self.backend}`")
        request = GraphQLRequest(
            query=self.INTROSPECTION_QUERY,
            operation_name=self.INTROSPECTION_OPERATION_NAME,
            variables={},
        )
        schema_content = self.backend.execute_query(request)
        return Schema.from_raw(self, schema_content.data["__schema"])

    @property
    def schema_cache_key(self) -> str:
        """Property to return the cache key that uniquely identifies this schema in the cache.

        This uses the backends cache key property as cache key.

        Returns:
            the cache key as defined by the backend.
        """
        return self.backend.schema_identifier
