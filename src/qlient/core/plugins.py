import abc

from qlient.core.models import GraphQLRequest, GraphQLResponse


class Plugin(abc.ABC):
    """Base plugin"""

    @abc.abstractmethod
    def pre(self, request: GraphQLRequest) -> GraphQLRequest:
        """Override to make changes to the request before giving it to the backend

        Args:
            request: holds the request

        Returns:
            the request
        """
        return request

    @abc.abstractmethod
    def post(self, response: GraphQLResponse) -> GraphQLResponse:
        """Override to update the response when the result is in

        Args:
            response: holds the response

        Returns:
            the response
        """
        return response
