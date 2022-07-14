# Welcome to Qlient Core

[![DeepSource](https://deepsource.io/gh/qlient-org/python-qlient-core.svg/?label=active+issues&token=B71TvEVbDX-5GynnxfPlumBi)](https://deepsource.io/gh/qlient-org/python-qlient-core/?ref=repository-badge)
[![DeepSource](https://deepsource.io/gh/qlient-org/python-qlient-core.svg/?label=resolved+issues&token=B71TvEVbDX-5GynnxfPlumBi)](https://deepsource.io/gh/qlient-org/python-qlient-core/?ref=repository-badge)
[![pypi](https://img.shields.io/pypi/v/qlient-core.svg)](https://pypi.python.org/pypi/qlient-core)
[![versions](https://img.shields.io/pypi/pyversions/qlient-core.svg)](https://github.com/qlient-org/python-qlient-core)
[![license](https://img.shields.io/github/license/qlient-org/python-qlient-core.svg)](https://github.com/qlient-org/python-qlient-core/blob/master/LICENSE)

This is the core for a blazingly fast and modern graphql (async) client that was designed with simplicity in mind.

## Key Features

* Support both synchronous and asynchronous clients
* Automatic query generation
* Offline query validation
* Support for different backends
* Easily extend your client through plugins.

## Quick Preview

```python
from qlient.core import Client, Backend, GraphQLResponse


class MyBackend(Backend):
    """Must be implemented by you"""


client = Client(MyBackend())

res: GraphQLResponse = client.query.get_my_thing("name")

print(res.request.query)  # "query get_my_thing { get_my_thing { name } }"
```
