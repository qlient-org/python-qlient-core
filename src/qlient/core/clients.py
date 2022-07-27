from typing import Optional, List

from qlient.core.backends import Backend
from qlient.core.exceptions import OutOfAsyncContext
from qlient.core.plugins import Plugin
from qlient.core.proxies import (
    QueryServiceProxy,
    AsyncQueryServiceProxy,
    MutationServiceProxy,
    AsyncMutationServiceProxy,
    SubscriptionServiceProxy,
    AsyncSubscriptionServiceProxy,
)
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings


class Client:
    """The qlient Client.

    Args:
        backend: holds the backend to use for executing operations
        schema: holds a pre-fetched schema
        plugins: a list of plugins to apply before and after executing an operation
        settings: the settings to use for this client
    """

    def __init__(
        self,
        backend: Backend,
        schema: Optional[Schema] = None,
        plugins: Optional[List[Plugin]] = None,
        settings: Optional[Settings] = None,
    ):
        if settings is None:
            settings = Settings()

        self.settings: Settings = settings
        self.backend: Backend = backend

        self.plugins: List[Plugin] = plugins if plugins is not None else []

        self._schema: Optional[Schema] = schema if schema is not None else None

        self._query_service: Optional[QueryServiceProxy] = None
        self._mutation_service: Optional[MutationServiceProxy] = None
        self._subscription_service: Optional[SubscriptionServiceProxy] = None

    @property
    def schema(self) -> Schema:
        """Property to lazy load the schema

        Returns:
            The schema to inspect
        """
        if self._schema is None:
            from qlient.core.schema.providers import BackendSchemaProvider

            provider = BackendSchemaProvider(self.backend)
            self._schema = provider.load_schema()
        return self._schema

    @property
    def query(self) -> QueryServiceProxy:
        """Property to lazy load the query service proxy

        Returns:
            The default query service proxy instance
        """
        if self._query_service is None:
            schema = self.schema
            self._query_service = QueryServiceProxy(
                self.backend, self.settings, schema, self.plugins
            )
        return self._query_service

    @property
    def mutation(self) -> MutationServiceProxy:
        """Property to lazy load the mutation service proxy

        Returns:
            The default mutation service proxy instance
        """
        if self._mutation_service is None:
            schema = self.schema
            self._mutation_service = MutationServiceProxy(
                self.backend, self.settings, schema, self.plugins
            )
        return self._mutation_service

    @property
    def subscription(self) -> SubscriptionServiceProxy:
        """Property to lazy load the subscription service proxy

        Returns:
            The default subscription service proxy instance
        """
        if self._subscription_service is None:
            schema = self.schema
            self._subscription_service = SubscriptionServiceProxy(
                self.backend, self.settings, schema, self.plugins
            )
        return self._subscription_service

    def __str__(self) -> str:
        """Return a simple string representation of the client"""
        class_name = self.__class__.__name__
        return f"{class_name}(backend={self.backend})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the client"""
        class_name = self.__class__.__name__
        props = ", ".join(
            [
                f"backend={self.backend}",
                f"settings={self.settings}",
            ]
        )
        return f"<{class_name}({props})>"


class AsyncClient(Client):
    """The async qlient Client."""

    @property
    def schema(self) -> Schema:
        """Property to lazy load the schema

        Returns:
            The schema to inspect
        """
        if self._schema is None:
            raise OutOfAsyncContext(
                "Did you use 'async with AsyncClient() as client:'?"
            )
        return self._schema

    @property
    def query(self) -> AsyncQueryServiceProxy:
        """Property to lazy load the query service proxy

        Returns:
            The default query service proxy instance
        """
        if self._query_service is None:
            schema = self.schema
            self._query_service = AsyncQueryServiceProxy(
                self.backend, self.settings, schema, self.plugins
            )
        return self._query_service

    @property
    def mutation(self) -> AsyncMutationServiceProxy:
        """Property to lazy load the mutation service proxy

        Returns:
            The default mutation service proxy instance
        """
        if self._mutation_service is None:
            schema = self.schema
            self._mutation_service = AsyncMutationServiceProxy(
                self.backend, self.settings, schema, self.plugins
            )
        return self._mutation_service

    @property
    def subscription(self) -> AsyncSubscriptionServiceProxy:
        """Property to lazy load the subscription service proxy

        Returns:
            The default subscription service proxy instance
        """
        if self._subscription_service is None:
            schema = self.schema
            self._subscription_service = AsyncSubscriptionServiceProxy(
                self.backend, self.settings, schema, self.plugins
            )
        return self._subscription_service

    async def __aenter__(self):
        if self._schema is None:
            # load the schema
            from qlient.core.schema.providers import AsyncBackendSchemaProvider

            provider = AsyncBackendSchemaProvider(self.backend)
            self._schema = await provider.load_schema()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
