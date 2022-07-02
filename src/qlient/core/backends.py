"""This file contains all backends"""
import abc

from qlient.core.models import GraphQLRequest, GraphQLResponse, GraphQLResponseGenerator


class Backend(abc.ABC):
    """Abstract base class for all graphql backend."""

    @abc.abstractmethod
    def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
        """Abstract method to execute a query on this backend.

        Args:
            request: holds the graph ql request

        Returns:
            the query result of the graphql backend
        """
        raise NotImplementedError

    @abc.abstractmethod
    def execute_mutation(self, request: GraphQLRequest) -> GraphQLResponse:
        """Abstract method to execute a mutation on this backend.

        Args:
            request: holds the graph ql request

        Returns:
            the mutation result of the graphql backend
        """
        raise NotImplementedError

    @abc.abstractmethod
    def execute_subscription(self, request: GraphQLRequest) -> GraphQLResponseGenerator:
        """Abstract method to initialize a subscription on this backend.

        Args:
            request: holds the graph ql request

        Returns:
            a generator that yields events from the graphql backend
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def schema_identifier(self) -> str:
        """A key that uniquely identifies the schema for a specific backend

        For example this can be a unique url or hostname.
        Or even a static key if the schema remains the same for the backend.

        This cache key is required for the BackendSchemaProvider.

        Returns:
            a string that uniquely identifies the schema
        """
        raise NotImplementedError
