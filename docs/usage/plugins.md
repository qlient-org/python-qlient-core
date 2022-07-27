# Plugins

You can write plugins for qlient which can be used to process/modify data before it is sent to (``pre``)
and after it is received from (``post``) the backend.

Writing a plugin is really simple and best explained via an example.

```python
from qlient.core import Plugin, GraphQLRequest, GraphQLResponse


class MyLoggingPlugin(Plugin):
    def pre(self, request: GraphQLRequest) -> GraphQLRequest:
        print(f"About to send {request} to the backend")
        return request

    def post(self, response: GraphQLResponse) -> GraphQLResponse:
        print(f"Received {response} from the backend")
        return response
```

A plugin can implement two methods: ``pre`` and ``post``.
The ``pre`` method receives the request as input and should always return a request.
In contrast, the ``post`` method receives the response from the backend and should always return a response.

To register this plugin you need to pass it to the client.

**Plugins are always executed sequentially.**

```python
from qlient.core import Client

client = Client(..., plugins=[MyLoggingPlugin()])
```

