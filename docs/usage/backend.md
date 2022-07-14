# Backends

A backend is a service that can take a query, variables and an operation name to create a response. The most common
backend is probably going to be some sort of web server.

## Writing Backends

Although a GraphQL API is mostly used in combination with a http backend, it's not solely bound serve over http.

For example when using [strawberry](https://strawberry.rocks/) you can generally just execute queries locally.

```python 
{% include "../examples/strawberry_schema_example.py" %}
```

_(This script is complete and should run "as is")_