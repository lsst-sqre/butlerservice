"""Configuration definition."""

__all__ = ["SimpleDataIdType"]

import graphql

SimpleDataIdType = graphql.GraphQLObjectType(
    name="SimpleDataId",
    fields=dict(
        data_id=graphql.GraphQLField(
            graphql.GraphQLNonNull(graphql.GraphQLString),
            description="Data ID as a json-encoded dict of name: value. "
            "All values are plain old data types.",
        ),
    ),
)
