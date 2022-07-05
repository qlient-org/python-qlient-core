from typing import (
    Union,
    Dict,
    List,
    Optional,
    Any,
    Iterator,
    AsyncIterator,
    Generator,
    AsyncGenerator,
)

JSON = Union[str, int, float, bool, None, Dict[str, "JSON"], List["JSON"]]

RawSchema = Dict[str, JSON]

GraphQLQueryType = str
GraphQLVariablesType = Optional[Dict[str, JSON]]
GraphQLOperationNameType = Optional[str]
GraphQLReturnType = Dict[str, JSON]
GraphQLReturnTypeIterator = Union[
    Iterator[GraphQLReturnType], Generator[GraphQLReturnType, None, None]
]
AsyncGraphQLReturnTypeIterator = Union[
    AsyncIterator[GraphQLReturnType], AsyncGenerator[GraphQLReturnType, None]
]
GraphQLContextType = Any
GraphQLRootType = Any

GraphQLData = Optional[Dict[str, JSON]]
GraphQLErrors = Optional[List[Dict[str, JSON]]]
GraphQLExtensions = Optional[List[Dict[str, JSON]]]
