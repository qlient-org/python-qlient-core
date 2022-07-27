from qlient.core import GraphQLResponse, Client

client = Client(...)

response: GraphQLResponse = client.query.film(id="ZmlsbXM6MQ==")

print(response.request.query)
