"""This module contains the qlient models"""
from qlient.core._types import (
    GraphQLVariablesType,
    GraphQLQueryType,
    GraphQLOperationNameType,
    GraphQLErrors,
    GraphQLExtensions,
    GraphQLData,
    GraphQLReturnType,
    GraphQLReturnTypeGenerator,
    GraphQLContextType,
    GraphQLRootType,
)


class GraphQLRequest:
    """Represents the graph ql request"""

    def __init__(
        self,
        query: GraphQLQueryType = None,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ):
        self.query: GraphQLQueryType = query
        self.variables: GraphQLVariablesType = variables
        self.operation_name: GraphQLOperationNameType = operation_name
        self.context: GraphQLContextType = context
        self.root: GraphQLRootType = root


class GraphQLResponse:
    """Represents the graph ql response type"""

    def __init__(
        self,
        request: GraphQLRequest,
        response: GraphQLReturnType,
    ):
        self.request: GraphQLRequest = request
        self.raw: GraphQLReturnType = response

        # response parsing
        self.data: GraphQLData = self.raw.get("data")
        self.errors: GraphQLErrors = self.raw.get("errors")
        self.extensions: GraphQLExtensions = self.raw.get("extensions")


class GraphQLResponseGenerator:
    def __init__(
        self,
        request: GraphQLRequest,
        response: GraphQLReturnTypeGenerator,
    ):
        self.request: GraphQLRequest = request
        self.generator: GraphQLReturnTypeGenerator = response
