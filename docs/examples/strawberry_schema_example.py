import asyncio
from typing import List, Optional

import strawberry  # must be installed separately

from qlient.core import (
    AsyncClient,
    AsyncBackend,
    GraphQLRequest,
    GraphQLResponse,
)


@strawberry.type
class User:
    name: str
    age: int


all_users: List[User] = [
    User(name="Patrick", age=100),
    User(name="Daniel", age=9999),
]


@strawberry.type
class Query:
    """The strawberry query type"""

    @strawberry.field
    async def get_user(self, index: int) -> Optional[User]:
        """Get a user by index"""
        try:
            return all_users[index]
        except IndexError:
            return None

    @strawberry.field
    async def get_users(self) -> List[User]:
        """Get all users"""
        return all_users


schema = strawberry.Schema(query=Query)


class StrawberryBackend(AsyncBackend):
    """The strawberry backend"""

    async def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
        """Execute a query on this backend"""
        # get the result
        result = await schema.execute(
            query=request.query,
            operation_name=request.operation_name,
            variable_values=request.variables,
            root_value=request.root,
            context_value=request.context,
        )

        # create the graphql response object
        return GraphQLResponse(
            request,
            {
                "data": result.data,
                "errors": result.errors,
                "extensions": result.extensions,
            },
        )


async def main():
    """The main coroutine"""

    async with AsyncClient(StrawberryBackend()) as client:
        # strawberry automatically converts snake_case to camelCase
        result_1: GraphQLResponse = await client.query.getUsers(["name", "age"])
        print(result_1.data)

        result_2: GraphQLResponse = await client.query.getUser(index=1)
        print(result_2.data)


asyncio.run(main())
