# Quick Introduction

## Walk-through

Below is a walk-through for the implementation of a [strawberry](https://strawberry.rocks/) backend.

If you do not want to follow the walk-through and just see the result,
I suggest you skip to the [full script](#full-script).

Otherwise, with no further ado lets get these fingers warm and ready for copy and paste.

### Creating the user type

First things first, we have to set up everything related to the strawberry schema.

Let's start by creating a simple `User` type we can query and mutate.

```python
import strawberry  # must be installed separately


@strawberry.type
class User:
    """The User object"""

    name: str
    age: int
```

### Defining the data storage

Next, we make a "database" that stores all our users.

```python
all_users: List[User] = [
    User(name="Patrick", age=100),
    User(name="Daniel", age=9999),
]
```

### Creating the query type

With a few initial users in that list, we can now create the Query type and schema.

```python
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


my_schema = strawberry.Schema(query=Query)
```

### Implement an AsyncBackend

Now, moving on to creating the qlient Backend.

```python
from qlient.core import AsyncBackend, GraphQLRequest, GraphQLResponse


class StrawberryBackend(AsyncBackend):
    """The strawberry backend"""

    def __init__(self, schema: strawberry.Schema):
        self.schema = schema

    async def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
        """Execute a query on this backend"""
        result = await self.schema.execute(
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
```

### Create the AsyncClient

And now finally, instantiating the Client:

```python
import asyncio
from qlient.core import AsyncClient, GraphQLResponse


async def main():
    """The main coroutine"""
    async with AsyncClient(StrawberryBackend(my_schema)) as client:
        # strawberry automatically converts snake_case to camelCase
        result_1: GraphQLResponse = await client.query.getUsers(["name", "age"])
        print(result_1.data)

        result_2: GraphQLResponse = await client.query.getUser(index=1)
        print(result_2.data)


asyncio.run(main())
```
_(result_1.data)_
```json
{
  "getUsers": [
    {
      "name": "Patrick",
      "age": 100
    },
    {
      "name": "Daniel",
      "age": 9999
    }
  ]
}
```
_(result_2.data)_
```json
{
  "getUser": {
      "name": "Daniel",
      "age": 9999
    }
}
```

## Full Script

```python 
{% include "examples/strawberry_schema_example.py" %}
```