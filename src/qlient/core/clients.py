from typing import Optional, List

from qlient.core.backends import Backend
from qlient.core.plugins import Plugin
from qlient.core.proxies import (
    QueryServiceProxy,
    MutationServiceProxy,
    SubscriptionServiceProxy,
)
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings


class Client:
    settings: Settings
    backend: Backend

    _query_service: Optional[QueryServiceProxy]
    _mutation_service: Optional[MutationServiceProxy]
    _subscription_service: Optional[SubscriptionServiceProxy]

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

        self.plugins = plugins if plugins is not None else []

        self.__schema: Optional[Schema] = schema if schema is not None else None

        self._query_service = None
        self._mutation_service = None
        self._subscription_service = None

    @property
    def schema(self):
        if self.__schema is None:
            from qlient.core.schema.providers import BackendSchemaProvider

            provider = BackendSchemaProvider(self.backend)
            self.__schema = provider.load_schema()
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
            ]
        )
        return f"<{class_name}({props})>"
