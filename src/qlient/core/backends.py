"""This file contains all backends"""
import abc

from qlient.core.models import (
    GraphQLRequest,
    GraphQLSubscriptionRequest,
    GraphQLResponse,
)


class Backend(abc.ABC):
    """Abstract base class for all graphql backends."""

    @abc.abstractmethod
    def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
        """Abstract method to execute a query on this backend.

        Args:
            request: holds the graph ql request

        Returns:
            the query result of the graphql backend
        """
        raise NotImplementedError

    def execute_mutation(self, request: GraphQLRequest) -> GraphQLResponse:
        """Abstract method to execute a mutation on this backend.

        Args:
            request: holds the graph ql request

        Returns:
            the mutation result of the graphql backend
        """
        raise NotImplementedError

    def execute_subscription(
        self, request: GraphQLSubscriptionRequest
    ) -> GraphQLResponse:
        """Abstract method to initialize a subscription on this backend.

        Args:
            request: holds the graph ql request

        Returns:
            a generator that yields events from the graphql backend
        """
        raise NotImplementedError


class AsyncBackend(Backend, abc.ABC):
    """Abstract base class for all async graphql backends."""

    @abc.abstractmethod
    async def execute_query(
        self, request: GraphQLRequest
    ) -> GraphQLResponse:  # skipcq: PYL-W0236
        """Abstract method to execute a query on this backend asynchronously.

        Args:
            request: holds the graph ql request

        Returns:
            the query result of the graphql backend
        """
        raise NotImplementedError

    async def execute_mutation(
        self, request: GraphQLRequest
    ) -> GraphQLResponse:  # skipcq: PYL-W0236
        """Abstract method to execute a mutation on this backend asynchronously.

        Args:
            request: holds the graph ql request

        Returns:
            the mutation result of the graphql backend
        """
        raise NotImplementedError

    async def execute_subscription(
        self, request: GraphQLSubscriptionRequest
    ) -> GraphQLResponse:  # skipcq: PYL-W0236
        """Abstract method to initialize a subscription on this backend asynchronously.

        Args:
            request: holds the graph ql request

        Returns:
            a generator that yields events from the graphql backend
        """
        raise NotImplementedError
