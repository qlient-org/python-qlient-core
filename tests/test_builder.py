from qlient.core.builder import GQLQueryBuilder


# skipcq: PY-D0003
def test_query_builder():
    builder = GQLQueryBuilder()
    expected = "{ }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_operation_query():
    builder = GQLQueryBuilder().operation("query")
    expected = "query { }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_operation_query_name():
    builder = GQLQueryBuilder().operation("query", name="MyQuery")
    expected = "query MyQuery { }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_operation_query_name_variables():
    builder = GQLQueryBuilder().operation(
        "query", name="MyQueryVar", variables={"$foo": "String!"}
    )
    expected = "query MyQueryVar($foo: String!) { }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_operation_mutation():
    builder = GQLQueryBuilder().operation("mutation")
    expected = "mutation { }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_operation_mutation_name():
    builder = GQLQueryBuilder().operation("mutation", name="MyMutation")
    expected = "mutation MyMutation { }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_operation_mutation_name_variables():
    builder = GQLQueryBuilder().operation(
        "mutation", name="MyMutationVar", variables={"$foo": "String!"}
    )
    expected = "mutation MyMutationVar($foo: String!) { }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_action():
    builder = GQLQueryBuilder().action("foo")
    expected = "{ foo }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_action_variables():
    builder = GQLQueryBuilder().action("foo", variables={"bar": 1})
    expected = "{ foo(bar: 1) }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_fields_simple():
    builder = GQLQueryBuilder()
    builder = builder.action("get_person")
    builder = builder.fields("first_name last_name")
    expected = "{ get_person { first_name last_name } }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_full_query():
    builder = GQLQueryBuilder()
    builder = builder.operation(
        "query", name="PersonQuery", variables={"$search": "String"}
    )
    builder = builder.action("get_person", variables={"search": "$search"})
    builder = builder.fields("first_name last_name hobby { title description }")
    expected = "query PersonQuery($search: String) { get_person(search: $search) { first_name last_name hobby { title description } } }"
    actual = builder.build()
    assert expected == actual


# skipcq: PY-D0003
def test_query_builder_full_mutation():
    builder = GQLQueryBuilder()
    builder = builder.operation(
        "mutation", name="UpdatePerson", variables={"$id": "ID!"}
    )
    builder = builder.action("update_person", variables={"id": "$id"})
    builder = builder.fields("first_name last_name")
    expected = "mutation UpdatePerson($id: ID!) { update_person(id: $id) { first_name last_name } }"
    actual = builder.build()
    assert expected == actual


def test_query_a_single_field():
    expected = "query { hero { name } }"
    actual = GQLQueryBuilder().fields("name").action("hero").operation("query").build()
    assert expected == actual


def test_query_nesting_fields():
    expected = "query { hero { name friends { name } } }"
    actual = (
        GQLQueryBuilder()
        .action("hero")
        .fields("name friends { name }")
        .operation("query")
        .build()
    )
    assert expected == actual


def test_query_input():
    expected = 'query { human(id: "1000") { name height } }'
    actual = (
        GQLQueryBuilder()
        .fields("name height")
        .action("human", variables={"id": '"1000"'})
        .operation("query")
        .build()
    )
    assert expected == actual


def test_query_with_nested_input():
    expected = (
        'query { human(input: {data: {id: "1000", name: "test"}}) { name height } }'
    )
    actual = (
        GQLQueryBuilder()
        .fields("name height")
        .action("human", variables={"input": {"data": {"id": "1000", "name": "test"}}})
        .operation("query")
        .build()
    )

    assert expected == actual


def test_query_input_with_arguments():
    expected = 'query { human(id: "1000") { name height(unit: FOOT) } }'
    actual = (
        GQLQueryBuilder()
        .fields("name height(unit: FOOT)")
        .action("human", variables={"id": '"1000"'})
        .operation("query")
        .build()
    )
    assert expected == actual


def test_query_with_variables():
    expected = "query HeroNameAndFriends($episode: Episode) { hero(episode: $episode) { name friends { name } } }"
    actual = (
        GQLQueryBuilder()
        .fields("name friends { name }")
        .action("hero", variables={"episode": "$episode"})
        .operation(
            "query", name="HeroNameAndFriends", variables={"$episode": "Episode"}
        )
        .build()
    )
    assert expected == actual


def test_mutation():
    expected = "mutation CreateReviewForEpisode($ep: Episode!, $review: ReviewInput!) { createReview(episode: $ep, review: $review) { stars commentary } }"
    actual = (
        GQLQueryBuilder()
        .fields("stars commentary")
        .action("createReview", variables={"episode": "$ep", "review": "$review"})
        .operation(
            "mutation",
            name="CreateReviewForEpisode",
            variables={"$ep": "Episode!", "$review": "ReviewInput!"},
        )
        .build()
    )
    assert expected == actual


def test_remove_duplicate_spaces():
    expected = "{ query { hero { name } } }"
    actual = GQLQueryBuilder().remove_duplicate_spaces(
        " {  query  {  hero  {  name  }  }  } "
    )
    assert expected == actual
