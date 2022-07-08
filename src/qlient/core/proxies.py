import abc
import itertools
from typing import Dict, Iterable, List, Optional

from qlient.core._internal import await_if_coro
from qlient.core._types import GraphQLContextType, GraphQLRootType, GraphQLQueryType
from qlient.core.backends import Backend
from qlient.core.builder import TypedGQLQueryBuilder, Fields
from qlient.core.models import (
    GraphQLResponse,
    GraphQLRequest,
)
from qlient.core.plugins import Plugin, apply_pre, apply_post
from qlient.core.schema.models import Field as SchemaField
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings


class OperationProxy:
    """The operation proxy"""

    operation_type: str
    field: SchemaField
    proxy: "ServiceProxy"

    def __init__(
        self,
        operation_type: str,
        field: SchemaField,
        proxy: "ServiceProxy",
    ):
        self.operation_type = operation_type
        self.field = field
        self.proxy = proxy

        self.query_builder: TypedGQLQueryBuilder = TypedGQLQueryBuilder(
            self.operation_type,
            self.field,
            self.proxy.schema,
            self.proxy.settings,
        )
        self._request: GraphQLRequest = GraphQLRequest()

    def select(self, *args, **kwargs) -> "OperationProxy":
        """Method to select fields

        Args:
            *args: holds the fields to select
            **kwargs: holds nested fields to select

        Returns:
            self
        """
        self._request.variables.update(self.query_builder.fields(*args, **kwargs))
        return self

    def variables(self, **kwargs) -> "OperationProxy":
        """Method to register variables for the root level

        Args:
            **kwargs: holds variables for the root level

        Returns:
            self
        """
        self._request.variables.update(self.query_builder.variables(**kwargs))
        return self

    def context(self, context: GraphQLContextType) -> "OperationProxy":
        """Method to set the execution context for the operation

        Args:
            context: holds the context

        Returns:
            self
        """
        self._request.context = context
        return self

    def root(self, root: GraphQLRootType) -> "OperationProxy":
        """Method to set the execution root for the operation

        Args:
            root: holds the operation root

        Returns:
            self
        """
        self._request.root = root
        return self

    def execute(self) -> GraphQLResponse:
        """Method to execute the operation and return the graphql response.

        Returns:
            The graphql response as returned from the server
        """
        self._request.query = self.query
        self._request.operation_name = self.field.name
        response = self.proxy.send(self._request)
        self._request = GraphQLRequest()  # reset the request
        return response

    def __str__(self) -> str:
        """Return a simple string representation of this instance"""
        class_name = self.__class__.__name__
        return f"{class_name}(`{self.field.name}`)"

    def __repr__(self) -> str:
        """Return a detailed string representation of this instance"""
        class_name = self.__class__.__name__
        return f"{class_name}(field={self.field})"

    @property
    def query(self) -> GraphQLQueryType:
        """Property to build the graphql query string

        Returns:
            The GraphQL Query String
        """
        return self.query_builder.build()

    def __gql__(self) -> GraphQLQueryType:
        return self.query

    def __call__(
        self,
        _fields: Optional[Fields] = None,
        _context: GraphQLContextType = None,
        _root: GraphQLRootType = None,
        **query_variables,
    ) -> GraphQLResponse:
        if _fields:
            self.select(_fields)
        if query_variables:
            self.variables(**query_variables)
        if _context:
            self.context(_context)
        if _root:
            self.root(_root)
        return self.execute()


class AsyncOperationProxy(OperationProxy):
    """The async operation proxy"""

    # skipcq: PYL-W0236
    async def execute(self) -> GraphQLResponse:
        """Method to execute the operation and return the graphql response.

        Returns:
            The graphql response as returned from the server
        """
        self._request.query = self.query
        self._request.operation_name = self.field.name
        response = await await_if_coro(self.proxy.send(self._request))
        self._request = GraphQLRequest()  # reset the request
        return response

    # skipcq: PYL-W0236
    async def __call__(
        self,
        _fields: Optional[Fields] = None,
        _context: GraphQLContextType = None,
        _root: GraphQLRootType = None,
        **query_variables,
    ) -> GraphQLResponse:
        if _fields:
            self.select(_fields)
        if query_variables:
            self.variables(**query_variables)
        if _context:
            self.context(_context)
        if _root:
            self.root(_root)
        return await self.execute()


class QueryProxy(OperationProxy):
    """Represents the operation proxy for queries"""

    def __init__(self, proxy: "QueryServiceProxy", operation_field: SchemaField):
        super(QueryProxy, self).__init__("query", operation_field, proxy)


class AsyncQueryProxy(QueryProxy, AsyncOperationProxy):
    """Represents the async operation proxy for queries"""

    def __init__(self, proxy: "AsyncQueryServiceProxy", operation_field: SchemaField):
        super(QueryProxy, self).__init__(
            "query", operation_field, proxy
        )  # skipcq: PYL-E1003


class MutationProxy(OperationProxy):
    """Represents the operation proxy for mutations"""

    def __init__(self, proxy: "MutationServiceProxy", operation_field: SchemaField):
        super(MutationProxy, self).__init__("mutation", operation_field, proxy)


class AsyncMutationProxy(MutationProxy, AsyncOperationProxy):
    """Represents the async operation proxy for queries"""

    def __init__(
        self, proxy: "AsyncMutationServiceProxy", operation_field: SchemaField
    ):
        super(MutationProxy, self).__init__(
            "mutation", operation_field, proxy
        )  # skipcq: PYL-E1003


class SubscriptionProxy(OperationProxy):
    """Represents the operation proxy for subscriptions"""

    def __init__(self, proxy: "SubscriptionServiceProxy", operation_field: SchemaField):
        super(SubscriptionProxy, self).__init__("subscription", operation_field, proxy)


class AsyncSubscriptionProxy(SubscriptionProxy, AsyncOperationProxy):
    """Represents the async operation proxy for queries"""

    def __init__(
        self, proxy: "AsyncSubscriptionServiceProxy", operation_field: SchemaField
    ):
        super(SubscriptionProxy, self).__init__(
            "subscription", operation_field, proxy
        )  # skipcq: PYL-E1003


class ServiceProxy(abc.ABC):
    """Base class for all service proxies"""

    backend: Backend
    settings: Settings
    schema: Schema

    def __init__(
        self,
        backend: Backend,
        settings: Settings,
        schema: Schema,
        plugins: List[Plugin],
    ):
        self.backend = backend
        self.settings = settings
        self.schema = schema
        self.plugins = plugins
        self.operations: Dict[str, OperationProxy] = self.get_bindings()

    def __contains__(self, key: str) -> bool:
        return key in self.operations

    def __getattr__(self, key: str) -> OperationProxy:
        """Return the OperationProxy for the given key.

        Args:
            key: holds the operation key

        Returns:
            the according OperationProxy

        Raises:
            AttributeError when the no operation with that key exists.
        """
        return self[key]

    # skipcq: PYL-R1710
    def __getitem__(self, key: str) -> OperationProxy:
        """Return the OperationProxy for the given key.

        Args:
            key: holds the operation key

        Returns:
            the according OperationProxy

        Raises:
            AttributeError when the no operation with that key exists.
        """
        try:
            return self.operations[key]
        except KeyError:
            self.__missing__(key)

    def __missing__(self, key: str):
        raise AttributeError(f"No operation found for key {key}")

    def __iter__(self):
        """Return iterator for the services and their callables."""
        return iter(self.operations.items())

    def __dir__(self) -> Iterable[str]:
        """Return the names of the operations."""
        return list(itertools.chain(dir(super()), self.operations))

    def __str__(self) -> str:
        """Return a simple string representation of this instance"""
        class_name = self.__class__.__name__
        return f"{class_name}(bindings={len(self.operations)})"

    def __repr__(self) -> str:
        """Return a detailed string representation of this instance"""
        class_name = self.__class__.__name__
        return f"{class_name}(bindings={self.supported_bindings})"

    @property
    def supported_bindings(self) -> List[str]:
        """Property to list the supported bindings"""
        return list(self.operations.keys())

    @abc.abstractmethod
    def get_bindings(self) -> Dict[str, OperationProxy]:
        """Abstract base method to get the service bindings"""

    def send(self, request: GraphQLRequest) -> GraphQLResponse:
        """The method that sends the request through plugins onto the backend.

        Args:
            request: holds the request to send

        Returns:
            the response from the backend
        """
        request = apply_pre(self.plugins, request)
        response = self.execute(request)
        response = apply_post(self.plugins, response)
        return response

    @abc.abstractmethod
    def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Abstract base method that sends the query to the backend"""


class AsyncServiceProxy(ServiceProxy, abc.ABC):
    """Base class for all async service proxies"""

    # skipcq: PYL-W0236
    async def send(self, request: GraphQLRequest) -> GraphQLResponse:
        """The method that sends the request through plugins onto the backend asynchronously.

        Args:
            request: holds the request to send

        Returns:
            the awaited response from the backend
        """
        request = apply_pre(self.plugins, request)
        response = await await_if_coro(self.execute(request))
        response = apply_post(self.plugins, response)
        return response

    @abc.abstractmethod
    async def execute(
        self, request: GraphQLRequest
    ) -> GraphQLResponse:  # skipcq: PYL-W0236
        """Abstract base method that sends the query to the backend"""


class QueryServiceProxy(ServiceProxy):
    """Represents the query service"""

    _operation_proxy_type = QueryProxy

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the query service bindings"""
        bindings = {}
        if not self.schema.query_type:
            return bindings

        for field in self.schema.query_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings

    def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Send a query to the graphql server"""
        return self.backend.execute_query(request)


class AsyncQueryServiceProxy(QueryServiceProxy, AsyncServiceProxy):
    """Represents the async query service"""

    _operation_proxy_type = AsyncQueryProxy

    # skipcq: PYL-W0236
    async def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Send a query asynchronously to the graphql server"""
        return await await_if_coro(self.backend.execute_query(request))


class MutationServiceProxy(ServiceProxy):
    """Represents the mutation service"""

    _operation_proxy_type = MutationProxy

    def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Send a query to the graphql server"""
        return self.backend.execute_mutation(request)

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the mutation service bindings"""
        bindings = {}
        if not self.schema.mutation_type:
            return bindings

        for field in self.schema.mutation_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings


class AsyncMutationServiceProxy(MutationServiceProxy, AsyncServiceProxy):
    """Represents the async mutation service"""

    _operation_proxy_type = AsyncMutationProxy

    # skipcq: PYL-W0236
    async def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Send a mutation asynchronously to the graphql server"""
        return await await_if_coro(self.backend.execute_mutation(request))


class SubscriptionServiceProxy(ServiceProxy):
    """Represents the subscription service"""

    _operation_proxy_type = SubscriptionProxy

    def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Send a query to the graphql server"""
        return self.backend.execute_subscription(request)

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the subscription service bindings

        Returns:
            A dictionary with the service name bound to the subscription service proxy
        """
        bindings = {}
        if not self.schema.subscription_type:
            return bindings

        for field in self.schema.subscription_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings


class AsyncSubscriptionServiceProxy(SubscriptionServiceProxy, AsyncServiceProxy):
    """Represents the async subscription service"""

    _operation_proxy_type = AsyncSubscriptionProxy

    # skipcq: PYL-W0236
    async def execute(self, request: GraphQLRequest) -> GraphQLResponse:
        """Send a subscription asynchronously to the graphql server"""
        return await await_if_coro(self.backend.execute_subscription(request))
