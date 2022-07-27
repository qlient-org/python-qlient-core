import qlient.core
from qlient.core.plugins import apply_pre, apply_post, Plugin


def test_base_plugin(graphql_response, graphql_request):
    base_plugin = Plugin()

    assert graphql_request == base_plugin.pre(graphql_request)
    assert graphql_response == base_plugin.post(graphql_response)


def test_custom_plugin(strawberry_backend, my_plugin):
    client = qlient.core.Client(strawberry_backend, plugins=[my_plugin])

    assert my_plugin in client.plugins

    client.query.getBooks(["title", "author"])

    assert my_plugin.pre_called
    assert my_plugin.post_called


def test_apply_pre(my_plugin, graphql_request):
    apply_pre([my_plugin], graphql_request)
    assert my_plugin.pre_called
    assert not my_plugin.post_called


def test_apply_post(my_plugin, graphql_response):
    apply_post([my_plugin], graphql_response)
    assert my_plugin.post_called
    assert not my_plugin.pre_called
