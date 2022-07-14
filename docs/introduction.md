# Quick Introduction

## Walk-through

Below is a walk-through for the implementation of a [strawberry](https://strawberry.rocks/) backend.

If you do not want to follow the walk-through and just see the result,
I suggest you skip to the [full script](#full-script).

Otherwise, with no further ado lets get these fingers warm and ready for copy and paste.

### Creating the user type

Let's start by creating a simple type we can query and mutate.

```python
import strawberry  # must be installed separately


@strawberry.type
class User:
    name: str
    age: int
```

### Defining the data storage

Next, we make a "database" that stores all our users.

```python
all_users: List[User] = [
    User(name="Patrick", age=100)
]
```

### Creating the query type

With an initial user in that list, we can now create the Query type and schema.

```python
@strawberry.type
class Query:

    @strawberry.field
    async def get_users(self) -> List[User]:
        return all_users


schema = strawberry.Schema(query=Query)
```

### Implement an AsyncBackend

Now, moving on to creating the qlient Backend.

```python
from qlient.core import AsyncBackend, GraphQLRequest, GraphQLResponse


class StrawberryBackend(AsyncBackend):

    async def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
        # get the result from the strawberry graphql schema
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
            }
        )
```

### Create the AsyncClient

And now finally, instantiating the Client:

```python
import asyncio
from qlient.core import AsyncClient, GraphQLResponse


async def main():
    async with AsyncClient(StrawberryBackend()) as client:
        # strawberry automatically converts snake_case to camelCase
        result: GraphQLResponse = await client.query.getUsers(["name", "age"])
        print(result.data)


asyncio.run(main())
```

```json
{
  "getUsers": [
    {
      "name": "Patrick",
      "age": 100
    }
  ]
}
```

## Full Script

```python
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


all_users: List[User] = [
    User(name="Patrick", age=100)
]


@strawberry.type
class Query:

    @strawberry.field
    async def get_users(self) -> List[User]:
        return all_users


schema = strawberry.Schema(query=Query)


class StrawberryBackend(AsyncBackend):

    async def execute_query(
            self, request: GraphQLRequest
    ) -> GraphQLResponse:
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
            }
        )


async def main():
    async with AsyncClient(StrawberryBackend()) as client:
        # strawberry automatically converts snake_case to camelCase
        result: GraphQLResponse = await client.query.getUsers(["name", "age"])
        print(result.data)


asyncio.run(main())
```