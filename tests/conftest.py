import asyncio
import json
import pathlib
from typing import List, AsyncGenerator

import pytest
import strawberry
from strawberry.types import ExecutionResult

from qlient.core import (
    Backend,
    AsyncBackend,
    GraphQLRequest,
    GraphQLResponse,
)

project_dir = pathlib.Path(pathlib.Path().resolve())

if project_dir.is_dir() and project_dir.name == "tests":
    tests_dir = project_dir
else:
    tests_dir = project_dir / "tests"

schema_files_dir = tests_dir / "schema_files"
path_to_swapi_schema = schema_files_dir / "swapi_schema.json"
path_to_spacex_schema = schema_files_dir / "spacex_schema.json"
path_to_dex_schema = schema_files_dir / "dex_schema.json"


@pytest.fixture(scope="session")
def raw_swapi_schema():
    with open(path_to_swapi_schema) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def raw_spacex_schema():
    with open(path_to_spacex_schema) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def raw_dex_schema():
    with open(path_to_dex_schema) as f:
        return json.load(f)


@pytest.fixture
def swapi_schema(raw_swapi_schema):
    from qlient.core.schema.schema import Schema

    return Schema(raw_swapi_schema, None)


@pytest.fixture
def dex_schema(raw_dex_schema):
    from qlient.core.schema.schema import Schema

    return Schema(raw_dex_schema, None)


@pytest.fixture
def spacex_schema(raw_spacex_schema):
    from qlient.core.schema.schema import Schema

    return Schema(raw_spacex_schema, None)


@pytest.fixture
def strawberry_schema() -> strawberry.Schema:
    @strawberry.type
    class Book:
        title: str
        author: str

    my_books = [
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
        )
    ]

    @strawberry.type
    class Query:
        @strawberry.field
        def get_books(self) -> List[Book]:
            return my_books

    @strawberry.type
    class Mutation:
        @strawberry.mutation
        def add_book(self, title: str, author: str) -> Book:
            book = Book(title=title, author=author)
            my_books.append(book)
            return book

    @strawberry.type
    class Subscription:
        @strawberry.subscription
        async def count(self, target: int = 10) -> AsyncGenerator[int, None]:
            for i in range(target):
                yield i
                await asyncio.sleep(0.1)

    # this line creates the strawberry schema
    return strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)


@pytest.fixture
def strawberry_backend(strawberry_schema) -> Backend:
    class StrawberryBackend(Backend):

        # skipcq: PYL-R0201
        def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
            result = strawberry_schema.execute_sync(
                query=request.query,
                operation_name=request.operation_name,
                variable_values=request.variables,
                root_value=request.root,
                context_value=request.context,
            )
            return GraphQLResponse(
                request,
                {
                    "data": result.data,
                    "errors": result.errors,
                    "extensions": result.extensions,
                },
            )

        def execute_mutation(self, request: GraphQLRequest) -> GraphQLResponse:
            return self.execute_query(request)

        # skipcq: PYL-R0201
        def execute_subscription(self, request: GraphQLRequest) -> GraphQLResponse:
            raise NotImplementedError

    return StrawberryBackend()


@pytest.fixture
def async_strawberry_backend(strawberry_schema) -> AsyncBackend:
    class AsyncStrawberryBackend(AsyncBackend):

        # skipcq: PYL-R0201
        async def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
            result = await strawberry_schema.execute(
                query=request.query,
                operation_name=request.operation_name,
                variable_values=request.variables,
                root_value=request.root,
                context_value=request.context,
            )
            return GraphQLResponse(
                request,
                {
                    "data": result.data,
                    "errors": result.errors,
                    "extensions": result.extensions,
                },
            )

        async def execute_mutation(self, request: GraphQLRequest) -> GraphQLResponse:
            return await self.execute_query(request)

        # skipcq: PYL-R0201
        async def execute_subscription(
            self, request: GraphQLRequest
        ) -> GraphQLResponse:
            generator = await strawberry_schema.subscribe(
                query=request.query,
                variable_values=request.variables,
                operation_name=request.operation_name,
                context_value=request.context,
                root_value=request.root,
            )
            if isinstance(generator, ExecutionResult):
                raise ValueError(f"Failed to initiate subscription: {generator}")
            return GraphQLResponse(request, generator)

    return AsyncStrawberryBackend()
