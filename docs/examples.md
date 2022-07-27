# Examples

To better show you what you can do once you have a suitable backend, I've created a few examples.

These examples are all based on the official [SWAPI GraphQL API](http://graphql.org/swapi-graphql).

## Query a film by id

```python 
{% include "examples/swapi_query_film_by_id.py" %}
```
_(Which **automatically** selects fields and generates the following query)_
```graphql
{% include "examples/swapi_query_film_by_id.graphql" %}
```

## Query all films with selection

```python 
{% include "examples/swapi_query_all_films_with_selection.py" %}
```
_(Which generates the following query)_
```graphql
{% include "examples/swapi_query_all_films_with_selection.graphql" %}
```