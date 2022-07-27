# The *ServiceProxy Objects

The `*ServiceProxy` objects (`QueryServiceProxy`, ...) are simple objects
that check if an operation exists for the attribute or item requested.

If the operation exists then it will return a `*OperationProxy` object (callable)
that is responsible for creating the request and sending it to the backend.

```python 
{% include "../examples/proxies.py" %}
```

## Create the raw request

```python 
{% include "../examples/create_request.py" %}
```

