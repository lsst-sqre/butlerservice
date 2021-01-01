"""Configuration definition."""

__all__ = ["app_schema"]

import graphql

from butlerservice.schemas.simple_query_data_ids_field import (
    simple_query_data_ids_field,
)
from butlerservice.schemas.simple_query_dimension_records_field import (
    simple_query_dimension_records_field,
)

app_schema = graphql.GraphQLSchema(
    query=graphql.GraphQLObjectType(
        name="Query",
        fields=dict(
            simple_query_data_ids=simple_query_data_ids_field,
            simple_query_dimension_records=simple_query_dimension_records_field,  # noqa
        ),
    ),
)
