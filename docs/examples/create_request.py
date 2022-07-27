from qlient.core import Client, GraphQLRequest

client = Client(...)

request: GraphQLRequest = client.query.X.create_request(["foo", "bar"], foo="test")

print(request.query)  # "query X($foo: String) { X(foo: $foo) { foo bar } }"
print(request.variables)  # {"foo": "test"}
