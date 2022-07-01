import abc
import itertools
from typing import Dict, Iterable, List, Optional, Union, Type

from qlient.core._types import (
    GraphQLVariablesType,
    GraphQLContextType,
    GraphQLRootType,
    GraphQLQueryType,
    GraphQLOperationNameType,
)
from qlient.core.backends import Backend, AsyncBackend
from qlient.core.builder import TypedGQLQueryBuilder, Fields
from qlient.core.models import (
    GraphQLResponse,
    GraphQLResponseGenerator,
    AsyncGraphQLResponseGenerator,
)
from qlient.core.schema.models import Field as SchemaField
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings


class OperationProxy:
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
        self._variables: GraphQLVariablesType = {}
        self._context: GraphQLContextType = None
        self._root: GraphQLRootType = None

    def select(self, *args, **kwargs) -> "OperationProxy":
        """Method to select fields

        Args:
            *args: holds the fields to select
            **kwargs: holds nested fields to select

        Returns:
            self
        """
        self._variables.update(self.query_builder.fields(*args, **kwargs))
        return self

    def variables(self, **kwargs) -> "OperationProxy":
        """Method to register variables for the root level

        Args:
            **kwargs: holds variables for the root level

        Returns:
            self
        """
        self._variables.update(self.query_builder.variables(**kwargs))
        return self

    def context(self, context: GraphQLContextType) -> "OperationProxy":
        """Method to set the execution context for the operation

        Args:
            context: holds the context

        Returns:
            self
        """
        self._context = context
        return self

    def root(self, root: GraphQLRootType) -> "OperationProxy":
        """Method to set the execution root for the operation

        Args:
            root: holds the operation root

        Returns:
            self
        """
        self._root = root
        return self

    def execute(self) -> GraphQLResponse:
        """Method to execute the operation and return the graphql response.

        Returns:
            The graphql response as returned from the server
        """
        return self.proxy.send(
            query=self.query,
            operation=self.field.name,
            variables=self._variables,
            context=self._context,
            root=self._root,
        )

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


class QueryProxy(OperationProxy):
    """Represents the operation proxy for queries"""

    def __init__(self, proxy: "QueryServiceProxy", operation_field: SchemaField):
        super(QueryProxy, self).__init__("query", operation_field, proxy)


class MutationProxy(OperationProxy):
    """Represents the operation proxy for mutations"""

    def __init__(self, proxy: "MutationServiceProxy", operation_field: SchemaField):
        super(MutationProxy, self).__init__("mutation", operation_field, proxy)


class SubscriptionProxy(OperationProxy):
    """Represents the operation proxy for subscriptions"""

    def __init__(self, proxy: "SubscriptionServiceProxy", operation_field: SchemaField):
        super(SubscriptionProxy, self).__init__("subscription", operation_field, proxy)


class AsyncOperationProxy(OperationProxy):
    proxy: "AsyncServiceProxy"

    def __init__(
        self,
        operation_type: str,
        field: SchemaField,
        proxy: "AsyncServiceProxy",
    ):
        super(AsyncOperationProxy, self).__init__(
            operation_type,
            field,
            proxy,
        )

    async def execute(self) -> GraphQLResponse:
        """Method to execute the operation and return the graphql response.

        Returns:
            The graphql response as returned from the server
        """
        return await self.proxy.send(
            query=self.query,
            operation=self.field.name,
            variables=self._variables,
            context=self._context,
            root=self._root,
        )


class AsyncQueryProxy(QueryProxy, AsyncOperationProxy):
    """Represents the operation proxy for queries"""

    def __init__(self, proxy: "AsyncQueryServiceProxy", operation_field: SchemaField):
        super(QueryProxy, self).__init__("query", operation_field, proxy)


class AsyncMutationProxy(MutationProxy, AsyncOperationProxy):
    """Represents the operation proxy for mutations"""

    def __init__(
        self, proxy: "AsyncMutationServiceProxy", operation_field: SchemaField
    ):
        super(MutationProxy, self).__init__("mutation", operation_field, proxy)


class AsyncSubscriptionProxy(SubscriptionProxy, AsyncOperationProxy):
    """Represents the operation proxy for subscriptions"""

    def __init__(
        self, proxy: "AsyncSubscriptionServiceProxy", operation_field: SchemaField
    ):
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
    ):
        self.backend = backend
        self.settings = settings
        self.schema = schema
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
        """Property to list the supported bindings aka the keys of the operations dict"""
        return list(self.operations.keys())

    @abc.abstractmethod
    def get_bindings(self) -> Dict[str, OperationProxy]:
        """Abstract base method to get the service bindings"""

    @abc.abstractmethod
    def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> Union[GraphQLResponse, GraphQLResponseGenerator]:
        """Abstract base method that sends the query to the backend"""


class QueryServiceProxy(ServiceProxy):
    """Represents the query service"""

    _operation_proxy_type: Type[OperationProxy] = QueryProxy

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the query service bindings"""
        bindings = {}
        if not self.client.schema.query_type:
            return bindings

        for field in self.client.schema.query_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings

    def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> GraphQLResponse:
        """Send a query to the graphql server"""
        response_body = self.client.backend.execute_query(
            query, variables, operation, context, root
        )
        return GraphQLResponse(
            response=response_body,
            query=query,
            variables=variables,
            operation_name=operation,
        )


class MutationServiceProxy(ServiceProxy):
    """Represents the mutation service"""

    _operation_proxy_type: Type[OperationProxy] = MutationProxy

    def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> GraphQLResponse:
        """Send a query to the graphql server"""
        response_body = self.client.backend.execute_mutation(
            query, variables, operation, context, root
        )
        return GraphQLResponse(
            response=response_body,
            query=query,
            variables=variables,
            operation_name=operation,
        )

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the mutation service bindings"""
        bindings = {}
        if not self.client.schema.mutation_type:
            return bindings

        for field in self.client.schema.mutation_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings


class SubscriptionServiceProxy(ServiceProxy):
    """Represents the subscription service"""

    _operation_proxy_type: Type[OperationProxy] = SubscriptionProxy

    def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> GraphQLResponseGenerator:
        """Send a query to the graphql server"""
        pass

    def get_bindings(self) -> Dict[str, _operation_proxy_type]:
        """Method to get the subscription service bindings

        Returns:
            A dictionary with the service name bound to the subscription service proxy
        """
        bindings = {}
        if not self.client.schema.subscription_type:
            return bindings

        for field in self.client.schema.subscription_type.fields:
            bindings[field.name] = self._operation_proxy_type(self, field)
        return bindings


class AsyncServiceProxy(ServiceProxy, abc.ABC):
    """Base class for all async service proxies"""

    backend: AsyncBackend

    def __init__(
        self,
        backend: AsyncBackend,
        settings: Settings,
        schema: Schema,
    ):
        super(AsyncServiceProxy, self).__init__(backend, settings, schema)

    @abc.abstractmethod
    async def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> Union[GraphQLResponse, AsyncGraphQLResponseGenerator]:
        """Abstract base method that sends the query to the backend"""


class AsyncQueryServiceProxy(QueryServiceProxy, AsyncServiceProxy):
    """Represents the async query service"""

    _operation_proxy_type = AsyncQueryProxy

    async def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> GraphQLResponse:
        """Send a query to the graphql server"""
        response_body = await self.client.backend.execute_query(
            query, variables, operation, context, root
        )
        return GraphQLResponse(
            response=response_body,
            query=query,
            variables=variables,
            operation_name=operation,
        )


class AsyncMutationServiceProxy(MutationServiceProxy, AsyncServiceProxy):
    """Represents the async mutation service"""

    _operation_proxy_type = AsyncMutationProxy

    async def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> GraphQLResponse:
        """Send a query to the graphql server"""
        response_body = await self.client.backend.execute_mutation(
            query, variables, operation, context, root
        )
        return GraphQLResponse(
            response=response_body,
            query=query,
            variables=variables,
            operation_name=operation,
        )


class AsyncSubscriptionServiceProxy(SubscriptionServiceProxy, AsyncServiceProxy):
    """Represents the async subscription service"""

    _operation_proxy_type = AsyncSubscriptionProxy

    async def send(
        self,
        query: GraphQLQueryType,
        *,
        operation: GraphQLOperationNameType = None,
        variables: GraphQLVariablesType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
        **kwargs,
    ) -> AsyncGraphQLResponseGenerator:
        """Send a query to the graphql server"""
        pass
