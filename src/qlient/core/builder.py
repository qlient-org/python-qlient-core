"""This file contains the query builder and fields"""
from typing import Optional, List, Dict, Any, Union, Iterable

from qlient.core._types import JSON, GraphQLContextType, GraphQLRootType
from qlient.core.models import Fields, GraphQLRequest, auto, Field, PreparedFields
from qlient.core.schema.models import (
    Input as SchemaInput,
    Type as SchemaType,
    Field as SchemaField,
)
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings

_AnyField = Union[
    Fields, Field, Iterable[Union[Field, str]], List[Union[Field, str]], None
]


class GQLQueryBuilder:
    """Class to programmatically build graphql queries"""

    @staticmethod
    def remove_duplicate_spaces(query: str) -> str:
        """Static method to remove duplicate spaces from a string

        Args:
            query: holds the string from which to drop the duplicate white spaces

        Returns:
            a string with no duplicate white spaces
        """
        return " ".join(query.split())

    @staticmethod
    def build_input(variables: Dict[str, Any], initial_str: str) -> str:
        """Static method to build the input with variables

        Args:
            variables: holds a dictionary with the var key mapped to the var value
            initial_str: holds the initial string (prefixed the input)

        Returns:
            a full-fledged graphql input string
        """
        inputs: List[str] = []

        final_str = initial_str

        if variables:
            key = list(variables.keys())[0]
            nested_keys = []

            while isinstance(variables[key], dict):
                nested_keys.append(key)
                variables: Dict = variables[key]
                key = list(variables.keys())[0]

            for key, value in variables.items():
                if nested_keys:
                    inputs.append(
                        f'{key}: "{value}"'
                    )  # Nested input won't have double quotes

                else:
                    inputs.append(f"{key}: {value}")

            final_str += "("

            for key in nested_keys:
                final_str = final_str + key + ": {"

            final_str = final_str + ", ".join(inputs)

            for _ in nested_keys:
                final_str += "}"

            final_str += ")"

        return final_str

    def __init__(self):
        self.operation_field: str = ""
        self.action_field: str = ""
        self.fields_field: Optional[str] = None

    def fields(self, fields: str) -> "GQLQueryBuilder":
        """Method to register a field selection

        Do not put leading and trailing curly brackets

        Args:
            fields: holds the fields as a string (e.g. "name friends { name }")
        Returns:
            self
        """
        self.fields_field = fields
        return self

    def action(
        self, action: str, variables: Dict[str, Any] = None
    ) -> "GQLQueryBuilder":
        """Method to register the graphql action/resolver you wish to execute

        Args:
            action: holds the graphql action/resolver (e.g. getUser)
            variables: holds the action variables

        Returns:
             self
        """
        action = self.build_input(variables, action)
        self.action_field = action
        return self

    def operation(
        self, operation: str, name: str = "", variables: Dict[str, Any] = None
    ) -> "GQLQueryBuilder":
        """Method to register the graphql operation

        Args:
            operation: holds the operation type (query, mutation, subscription)
            name: optional, holds the name of the operation,
                required for usage with variables
            variables: optional, holds query variables

        Returns:
            self
        """
        if name:
            operation = f"{operation} {name}"
            operation = self.build_input(variables, operation)
        self.operation_field = operation
        return self

    def build(self) -> str:
        """Method to build the graphql query

        Returns:
            the complete graphql query with operation, action and fields.
        """
        query_parts = [self.operation_field, "{", self.action_field]
        if self.fields_field:
            query_parts.append("{")
            query_parts.append(self.fields_field)
            query_parts.append("}")
        query_parts.append("}")
        final_query = " ".join(query_parts)
        return self.remove_duplicate_spaces(final_query)


class RequestBuilder:
    """Class that represents a typed GraphQL Query Builder

    The typed graphql builder takes the operation type,
    operation field, schema and settings
    as input arguments to ensure type safety in the graphql query.

    The operation_field is the action that you are trying to execute.
    Say you want to register a new user with your graphql mutation "registerUser".
    Then a "registerUser" field will be present in the schema.
    """

    def __init__(
        self,
        operation_type: str,
        operation_field: SchemaField,
        schema: Schema,
        settings: Settings,
    ):
        self.settings: Settings = settings
        self.operation_type: str = operation_type
        self.operation_field: SchemaField = operation_field
        self.operation_name: str = self.operation_field.name
        self.operation_inputs: Dict[
            str, SchemaInput
        ] = self.operation_field.arg_name_to_arg
        self.operation_output: SchemaType = schema.types_registry[
            self.operation_field.output_type_name
        ]
        self.schema: Schema = schema

        self._fields: _AnyField = None
        self._context: Any = None
        self._root: Any = None
        self._inputs: Optional[Dict[str, JSON]] = None

    def context(self, context: GraphQLContextType) -> "RequestBuilder":
        """Method to set the request context"""
        self._context = context
        return self

    def root(self, root: GraphQLRootType) -> "RequestBuilder":
        """Method to set the request root"""
        self._root = root
        return self

    def fields(
        self,
        fields: _AnyField,
    ) -> "RequestBuilder":
        """Method to set the field selection"""
        self._fields = fields
        return self

    def variables(self, **inputs: JSON) -> "RequestBuilder":
        """Method to set the request variables"""
        self._inputs = inputs
        return self

    def build(self) -> GraphQLRequest:
        """Method to build the graphql query string from all given inputs

        Returns:
            the graphql query string
        """
        query_builder: GQLQueryBuilder = GQLQueryBuilder()
        query_builder.operation(self.operation_type, self.operation_name)
        query_builder.action(self.operation_name)

        _operation_variables: Dict[str, JSON] = {}
        _action_variables: Dict[str, JSON] = {}

        # build fields
        _fields = self._fields
        _inputs = self._inputs.copy()

        if _fields is auto and self.settings.allow_auto_lookup:
            # automatically build a Fields structure
            _fields = self._auto_build_fields()
        if isinstance(_fields, (list, set, tuple, Iterable)):
            # convert the list, set, tuple or iterable to a Fields object
            _fields = Fields(*_fields)
        if isinstance(_fields, Fields):
            # prepare the fields
            _fields = _fields.prepare(
                self.operation_output,
                self.schema,
            )

        #
        if _fields and isinstance(_fields, PreparedFields):
            query_builder.fields(_fields.__gql__())

        # add the variables from the input
        for key in _inputs:
            if key not in self.operation_inputs:
                raise KeyError(f"Input {key} not supported for {self.operation_name}")

            _input = self.operation_inputs[key]
            _operation_variables[f"${key}"] = _input.type.graphql_representation
            _action_variables[key] = f"${key}"

        if _operation_variables is not None:
            query_builder.operation(
                self.operation_type, self.operation_name, _operation_variables
            )
        if _action_variables is not None:
            query_builder.action(self.operation_name, _action_variables)

        query = query_builder.build()

        return GraphQLRequest(
            query=query,
            variables=_inputs,
            operation_name=self.operation_name,
            context=self._context,
            root=self._root,
        )

    # skipcq: PY-D0003
    def _auto_build_fields(self) -> Fields:
        return self._lookup_fields_for_type(self.operation_output, 0)

    # skipcq: PY-D0003
    def _lookup_fields_for_type(self, _type: SchemaType, depth: int) -> Fields:
        _fields = Fields()
        for field in _type.fields:
            if field.is_object_kind:
                if depth >= self.settings.lookup_recursion_depth:
                    continue

                _fields += {
                    field.name: self._lookup_fields_for_type(
                        _type=field.output_type,
                        depth=depth + 1,
                    )
                }
            elif field.is_scalar_kind:
                _fields += field.name
        return _fields
