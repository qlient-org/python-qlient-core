import asyncio
from typing import List

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


all_users: List[User] = [User(name="Patrick", age=100)]


@strawberry.type
class Query:
    @strawberry.field
    async def get_users(self) -> List[User]:
        return all_users


schema = strawberry.Schema(query=Query)


class StrawberryBackend(AsyncBackend):
    async def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
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
    async with AsyncClient(StrawberryBackend()) as client:
        # strawberry automatically converts snake_case to camelCase
        result: GraphQLResponse = await client.query.getUsers(["name", "age"])
        print(result.data)


asyncio.run(main())
