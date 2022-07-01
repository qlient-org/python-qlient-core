"""This file contains all backends"""
import abc

from qlient.core._types import (
    GraphQLQueryType,
    GraphQLVariablesType,
    GraphQLOperationNameType,
    GraphQLContextType,
    GraphQLRootType,
    GraphQLReturnType,
    GraphQLReturnTypeGenerator,
    AsyncGraphQLReturnTypeGenerator,
)


class Backend(abc.ABC):
    """Abstract base class for all graphql backend."""

    @abc.abstractmethod
    def execute_query(
        self,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ) -> GraphQLReturnType:
        """Abstract method to execute a query on this backend.

        Args:
            query: holds the graphql query
            variables: optional, holds variables that are mentioned in the query
            operation_name: optional, holds the name of this specific operation
            context: optional, holds a graphql context
            root: optional, holds a root value for this query

        Returns:
            the query result of the graphql backend
        """
        raise NotImplementedError

    @abc.abstractmethod
    def execute_mutation(
        self,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ) -> GraphQLReturnType:
        """Abstract method to execute a mutation on this backend.

        Args:
            query: holds the graphql query
            variables: optional, holds variables that are mentioned in the query
            operation_name: optional, holds the name of this specific operation
            context: optional, holds a graphql context
            root: optional, holds a root value for this query

        Returns:
            the mutation result of the graphql backend
        """
        raise NotImplementedError

    @abc.abstractmethod
    def execute_subscription(
        self,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ) -> GraphQLReturnTypeGenerator:
        """Abstract method to initialize a subscription on this backend.

        Args:
            query: holds the graphql query
            variables: optional, holds variables that are mentioned in the query
            operation_name: optional, holds the name of this specific operation
            context: optional, holds a graphql context
            root: optional, holds a root value for this query

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


class AsyncBackend(Backend, abc.ABC):
    """Abstract base class to interact asynchronously with the backend."""

    async def execute_query(
        self,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ) -> GraphQLReturnType:
        """Abstract method to asynchronously execute a query on this backend.

        Args:
            query: holds the graphql query
            variables: optional, holds variables that are mentioned in the query
            operation_name: optional, holds the name of this specific operation
            context: optional, holds a graphql context
            root: optional, holds a root value for this query

        Returns:
            the query result of the graphql backend
        """
        raise NotImplementedError

    async def execute_mutation(
        self,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ) -> GraphQLReturnType:
        """Abstract method to asynchronously execute a mutation on this backend.

        Args:
            query: holds the graphql query
            variables: optional, holds variables that are mentioned in the query
            operation_name: optional, holds the name of this specific operation
            context: optional, holds a graphql context
            root: optional, holds a root value for this query

        Returns:
            the mutation result of the graphql backend
        """
        raise NotImplementedError

    async def execute_subscription(
        self,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ) -> AsyncGraphQLReturnTypeGenerator:
        """Abstract method to initialize an asynchronous subscription on this backend.

        Args:
            query: holds the graphql query
            variables: optional, holds variables that are mentioned in the query
            operation_name: optional, holds the name of this specific operation
            context: optional, holds a graphql context
            root: optional, holds a root value for this query

        Returns:
            an asynchronous generator that yields events from the graphql backend
        """
        raise NotImplementedError
