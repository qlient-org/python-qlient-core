from typing import Optional

from qlient.core.backends import Backend, AsyncBackend
from qlient.core.caches import Cache
from qlient.core.proxies import (
    QueryServiceProxy,
    MutationServiceProxy,
    SubscriptionServiceProxy,
    AsyncQueryServiceProxy,
    AsyncMutationServiceProxy,
    AsyncSubscriptionServiceProxy,
)
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings


class Client:
    settings: Settings
    backend: Backend
    cache: Optional[Cache]

    _query_service: Optional[QueryServiceProxy]
    _mutation_service: Optional[MutationServiceProxy]
    _subscription_service: Optional[SubscriptionServiceProxy]

    def __init__(
        self,
        backend: Backend,
        schema: Optional[Schema] = None,
        settings: Optional[Settings] = None,
        cache: Optional[Cache] = None,
    ):
        if settings is None:
            settings = Settings()

        self.settings: Settings = settings
        self.backend: Backend = backend
        self.cache: Optional[Cache] = cache

        self.__schema: Optional[Schema] = schema if schema is not None else None

        self._query_service = None
        self._mutation_service = None
        self._subscription_service = None

    @property
    def schema(self):
        if self.__schema is None:
            from qlient.core.schema.providers import BackendSchemaProvider

            provider = BackendSchemaProvider(self.backend)
            self.__schema = Schema.load(provider, self.settings, self.cache)
        return self.__schema

    @property
    def query(self) -> QueryServiceProxy:
        if self._query_service is None:
            schema = self.schema
            self._query_service = QueryServiceProxy(self.backend, self.settings, schema)
        return self._query_service

    @property
    def mutation(self) -> MutationServiceProxy:
        if self._mutation_service is None:
            schema = self.schema
            self._mutation_service = MutationServiceProxy(
                self.backend, self.settings, schema
            )
        return self._mutation_service

    @property
    def subscription(self) -> SubscriptionServiceProxy:
        if self._subscription_service is None:
            schema = self.schema
            self._subscription_service = SubscriptionServiceProxy(
                self.backend, self.settings, schema
            )
        return self._subscription_service

    def __str__(self) -> str:
        """Return a simple string representation of the client"""
        class_name = self.__class__.__name__
        return f"{class_name}(backend=`{self.backend}`)"

    def __repr__(self) -> str:
        """Return a detailed string representation of the client"""
        class_name = self.__class__.__name__
        props = ", ".join(
            [
                f"endpoint=`{self.backend}`",
                f"settings={self.settings}",
                f"cache={self.cache}",
            ]
        )
        return f"<{class_name}({props})>"


class AsyncClient(Client):
    backend: AsyncBackend

    _query_service: Optional[AsyncQueryServiceProxy]
    _mutation_service: Optional[AsyncMutationServiceProxy]
    _subscription_service: Optional[AsyncSubscriptionServiceProxy]

    def __init__(
        self,
        backend: AsyncBackend,
        schema: Optional[Schema] = None,
        settings: Optional[Settings] = None,
        cache: Optional[Cache] = None,
    ):
        super(AsyncClient, self).__init__(backend, schema, settings, cache)

    @property
    async def schema(self):
        if self.__schema is None:
            from qlient.core.schema.providers import AsyncBackendSchemaProvider

            provider = AsyncBackendSchemaProvider(self.backend)
            self.__schema = await Schema.load_async(provider, self.settings, self.cache)
        return self.__schema

    @property
    async def query(self) -> AsyncQueryServiceProxy:
        if self._query_service is None:
            schema = await self.schema
            self._query_service = AsyncQueryServiceProxy(
                self.backend, self.settings, schema
            )
        return self._query_service

    @property
    async def mutation(self) -> AsyncMutationServiceProxy:
        if self._mutation_service is None:
            schema = await self.schema
            self._mutation_service = AsyncMutationServiceProxy(
                self.backend, self.settings, schema
            )
        return self._mutation_service

    @property
    async def subscription(self) -> AsyncSubscriptionServiceProxy:
        if self._subscription_service is None:
            schema = await self.schema
            self._subscription_service = AsyncSubscriptionServiceProxy(
                self.backend, self.settings, schema
            )
        return self._subscription_service
