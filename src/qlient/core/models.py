"""This module contains the qlient models"""
from qlient.core._types import (
    GraphQLVariablesType,
    GraphQLQueryType,
    GraphQLOperationNameType,
    GraphQLErrors,
    GraphQLExtensions,
    GraphQLData,
    GraphQLReturnType,
)


class GraphQLResponse:
    """Represents the graph ql response type"""

    def __init__(
        self,
        response: GraphQLReturnType,
        query: GraphQLQueryType,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
    ):
        self.raw: GraphQLReturnType = response

        # request information
        self.query: GraphQLQueryType = query
        self.variables: GraphQLVariablesType = variables
        self.operation_name: GraphQLOperationNameType = operation_name

        # response parsing
        self.data: GraphQLData = self.raw.get("data")
        self.errors: GraphQLErrors = self.raw.get("errors")
        self.extensions: GraphQLExtensions = self.raw.get("extensions")


class GraphQLResponseGenerator:
    pass


class AsyncGraphQLResponseGenerator(GraphQLResponseGenerator):
    pass
