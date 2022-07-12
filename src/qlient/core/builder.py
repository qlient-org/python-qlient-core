"""This file contains the query builder and fields"""
from typing import Optional, List, Dict, Any

from qlient.core.models import PreparedFields, Fields
from qlient.core.schema.models import (
    Input as SchemaInput,
    Type as SchemaType,
    Field as SchemaField,
)
from qlient.core.schema.schema import Schema
from qlient.core.settings import Settings


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


class TypedGQLQueryBuilder:
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
        self.op_type: str = operation_type
        self.op_field: SchemaField = operation_field
        self.op_name: str = self.op_field.name
        self.op_inputs: Dict[str, SchemaInput] = self.op_field.arg_name_to_arg
        self.op_output: Optional[SchemaType] = schema.types_registry.get(
            self.op_field.output_type_name
        )
        self.schema: Schema = schema
        self.builder: GQLQueryBuilder = GQLQueryBuilder()
        self.builder.operation(self.op_type, self.op_name)
        self.builder.action(self.op_name)

        self._fields: Optional[PreparedFields] = None
        self._operation_variables: Optional[Dict[str, Any]] = {}
        self._action_variables: Optional[Dict[str, Any]] = {}

    def fields(self, *args, **kwargs) -> Dict[str, Any]:
        """Method to programmatically create a type safe field selection.

        This method takes the *args and **kwargs and creates a "Fields" instances.
        It then prepares this Fields instance.

        Args:
            *args: holds an iterable of fields (e.g. "firstname", "lastname", ...)
            **kwargs: holds a dictionary for simple deeper field selection.

        Returns:
            a dictionary with declared variable references mapped to their values
        """
        self._fields = Fields(*args, **kwargs).prepare(self.op_output, self.schema)
        for var_ref, var_type_ref in self._fields.var_ref_to_var_type.items():
            prefixed_key = f"${var_ref}"
            self._operation_variables[prefixed_key] = var_type_ref.__gql__()

        return self._fields.var_ref_to_var_value

    def variables(self, **kwargs) -> Dict[str, Any]:
        """Method to register operation level variables.

        Args:
            **kwargs: holds a dictionary with variable key mapped to variable value

        Returns:
            a dictionary with declared variable references mapped to their values
        """
        for key in kwargs:
            if self.settings.validate_variables and key not in self.op_inputs:
                raise KeyError(
                    f"Input `{key}` not supported "
                    f"for {self.op_type} operation `{self.op_name}`"
                )
            _input: SchemaInput = self.op_inputs[key]
            prefixed_key = f"${key}"
            self._operation_variables[prefixed_key] = _input.type.__gql__()
            self._action_variables[key] = prefixed_key

        return kwargs

    def build(self) -> str:
        """Method to build the graphql query string from all given inputs

        Returns:
            the graphql query string
        """
        if self._fields is not None:
            self.builder.fields(self._fields.__gql__())
        if self._operation_variables is not None:
            self.builder.operation(
                self.op_type, self.op_name, self._operation_variables
            )
        if self._action_variables is not None:
            self.builder.action(self.op_name, self._action_variables)
        return self.builder.build()

    def __gql__(self) -> str:
        """Method to build the graphql query string from all given inputs

        Returns:
            the graphql query string
        """
        return self.build()
