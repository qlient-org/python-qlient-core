from qlient.core import Client

client = Client(...)

# "query" is a QueryServiceProxy object.
# It will check if there is an operation
# with the name "X" defined in the query type
# and if that is the case it will return an QueryOperationProxy.
client.query.X()

# The operation cal also be called via an __getitem__ call.
# This is useful if the operation name is not a valid
# python attribute name.
client.query["X-Y"]()
