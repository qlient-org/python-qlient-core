from qlient.core import GraphQLResponse, Fields


def test_film(swapi_client):
    response: GraphQLResponse = swapi_client.query.film(id="ZmlsbXM6MQ==")

    assert (
        response.request.query
        == "query film($id: ID) { film(id: $id) { title episodeID openingCrawl director producers releaseDate speciesConnection { totalCount } starshipConnection { totalCount } vehicleConnection { totalCount } characterConnection { totalCount } planetConnection { totalCount } created edited id } }"
    )
    assert response.request.variables == {"id": "ZmlsbXM6MQ=="}


def test_all_films_with_selection(swapi_client):
    response: GraphQLResponse = swapi_client.query.allFilms(
        Fields("totalCount", films=["id", "title", "director", "releaseDate"])
    )

    assert (
        response.request.query
        == "query allFilms { allFilms { totalCount films { id title director releaseDate } } }"
    )
    assert response.request.variables == {}
