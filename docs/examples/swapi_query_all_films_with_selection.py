from qlient.core import GraphQLResponse, Fields, Client

client = Client(...)

response: GraphQLResponse = client.query.allFilms(
    Fields("totalCount", films=["id", "title", "director", "releaseDate"])
)

print(response.request.query)
