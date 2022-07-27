"""This module contains the operation proxy instances"""
import abc
import itertools
from typing import Dict, Iterable, List, Any, Union

from qlient.core._internal import await_if_coro
from qlient.core._types import GraphQLContextType, GraphQLRootType
from qlient.core.backends import Backend
from qlient.core.builder import RequestBuilder, Fields
from qlient.core.models import (
    GraphQLResponse,
    GraphQLRequest,
    GraphQLSubscriptionRequest,
    auto,
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

        if proxy.settings.use_schema_description and field.description:
            self.__doc__ = field.description

    def __str__(self) -> str:
        """Return a simple string representation of this instance"""
        class_name = self.__class__.__name__
        return f"{class_name}(`{self.field.name}`)"

    def __repr__(self) -> str:
        """Return a detailed string representation of this instance"""
        class_name = self.__class__.__name__
        return f"{class_name}(field={self.field})"

    def create_request(
        self,
        _fields: Union[Fields, Iterable[str], List[str], None] = auto,
        _context: GraphQLContextType = None,
        _root: GraphQLRootType = None,
        **inputs,
    ) -> GraphQLRequest:
        """Method to create the request instance

        Args:
            _fields: holds the selected fields
            _context: holds the request context
            _root: holds the request root
            **inputs: holds the request inputs

        Returns:
            The GraphQLRequest instance
        """
        return (
            RequestBuilder(
                self.operation_type,
                self.field,
                self.proxy.schema,
                self.proxy.settings,
            )
            .context(_context)
            .root(_root)
            .fields(_fields)
            .variables(**inputs)
        ).build()

    def __call__(
        self,
        *args,
        **kwargs,
    ) -> GraphQLResponse:
        request = self.create_request(*args, **kwargs)
        return self.proxy.send(request)


class AsyncOperationProxy(OperationProxy):
    """The async operation proxy"""

    # skipcq: PYL-W0236
    async def __call__(
        self,
        *args,
        **kwargs,
    ) -> GraphQLResponse:
        request = self.create_request(*args, **kwargs)
        return await await_if_coro(self.proxy.send(request))


class QueryProxy(OperationProxy):
    """Represents the operation proxy for queries"""

    def __init__(self, proxy: "QueryServiceProxy", operation_field: SchemaField):
        super(QueryProxy, self).__init__("query", operation_field, proxy)


class AsyncQueryProxy(QueryProxy, AsyncOperationProxy):
    """Represents the async operation proxy for queries"""

    def __init__(self, proxy: "AsyncQueryServiceProxy", operation_field: SchemaField):
        # skipcq: PYL-E1003
        super(QueryProxy, self).__init__("query", operation_field, proxy)


class MutationProxy(OperationProxy):
    """Represents the operation proxy for mutations"""

    def __init__(self, proxy: "MutationServiceProxy", operation_field: SchemaField):
        super(MutationProxy, self).__init__("mutation", operation_field, proxy)


class AsyncMutationProxy(MutationProxy, AsyncOperationProxy):
    """Represents the async operation proxy for queries"""

    def __init__(
        self, proxy: "AsyncMutationServiceProxy", operation_field: SchemaField
    ):
        # skipcq: PYL-E1003
        super(MutationProxy, self).__init__("mutation", operation_field, proxy)


class SubscriptionProxy(OperationProxy):
    """Represents the operation proxy for subscriptions"""

    def __init__(self, proxy: "SubscriptionServiceProxy", operation_field: SchemaField):
        super(SubscriptionProxy, self).__init__("subscription", operation_field, proxy)

    def create_request(
        self,
        _fields: Union[Fields, Iterable[str], List[str], None] = auto,
        _context: GraphQLContextType = None,
        _root: GraphQLRootType = None,
        _subscription_id: str = None,
        _options: Dict[str, Any] = None,
        **inputs,
    ) -> GraphQLSubscriptionRequest:
        """Method to create the request instance

        Args:
            _fields: holds the selected fields
            _context: holds the request context
            _root: holds the request root
            _subscription_id: holds the identifier of the subscription
            _options: holds the subscription options
            **inputs: holds the request inputs

        Returns:
            The GraphQLRequest instance
        """
        request = super(SubscriptionProxy, self).create_request(
            _fields=_fields, _context=_context, _root=_root, **inputs
        )
        request = GraphQLSubscriptionRequest(
            query=request.query,
            variables=request.variables,
            operation_name=request.operation_name,
            context=request.context,
            root=request.root,
            subscription_id=_subscription_id,
            options=_options,
        )
        return request


class AsyncSubscriptionProxy(SubscriptionProxy, AsyncOperationProxy):
    """Represents the async operation proxy for queries"""

    def __init__(
        self, proxy: "AsyncSubscriptionServiceProxy", operation_field: SchemaField
    ):
        # skipcq: PYL-E1003
        super(SubscriptionProxy, self).__init__("subscription", operation_field, proxy)


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
        """Method to send the request through plugins onto the backend asynchronously.

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
    async def execute(  # skipcq: PYL-W0236
        self, request: GraphQLRequest
    ) -> GraphQLResponse:
        """Abstract base method that sends the query to the backend"""


class QueryServiceProxy(ServiceProxy):
    """Represents the query service"""

    _operation_proxy_type = QueryProxy

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the query service bindings"""
        bindings = {}
        if not self.schema.query_type and not self.schema.query_type.fields:
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
        if not self.schema.mutation_type and not self.schema.mutation_type.fields:
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

    def execute(self, request: GraphQLSubscriptionRequest) -> GraphQLResponse:
        """Send a query to the graphql server"""
        return self.backend.execute_subscription(request)

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the subscription service bindings

        Returns:
            A dictionary with the service name bound to the subscription service proxy
        """
        bindings = {}
        if (
            not self.schema.subscription_type
            and not self.schema.subscription_type.fields
        ):
            return bindings

        for field in self.schema.subscription_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings


class AsyncSubscriptionServiceProxy(SubscriptionServiceProxy, AsyncServiceProxy):
    """Represents the async subscription service"""

    _operation_proxy_type = AsyncSubscriptionProxy

    # skipcq: PYL-W0236
    async def execute(self, request: GraphQLSubscriptionRequest) -> GraphQLResponse:
        """Send a subscription asynchronously to the graphql server"""
        return await await_if_coro(self.backend.execute_subscription(request))
