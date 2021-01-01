"""Configuration definition."""

__all__ = ["SimpleRecordType"]

import graphql

SimpleRecordType = graphql.GraphQLObjectType(
    name="SimpleRecord",
    fields=dict(
        record=graphql.GraphQLField(
            graphql.GraphQLNonNull(graphql.GraphQLString),
            description="Data record as a json-encoded dict of name: value. "
            "All values are plain old data types. "
            "Dates are TAI, represented as ISO strings. "
            "Time spans are normally instances of lsst.daf.butler.Timespan, "
            "but are represented here by a tuple of (begin date, end date). "
            "Regions are normally instances of lsst.sphgeom.Region, "
            "but are represented here by their serialization.",
        ),
    ),
)
