"""Configuration definition."""

__all__ = ["simple_query_data_ids_field"]

import graphql

from butlerservice.resolvers.simple_query_data_ids import simple_query_data_ids
from butlerservice.schemas.simple_data_id_type import SimpleDataIdType

simple_query_data_ids_field = graphql.GraphQLField(
    graphql.GraphQLList(SimpleDataIdType),
    args=dict(
        dimensions=graphql.GraphQLArgument(
            graphql.GraphQLNonNull(graphql.GraphQLList(graphql.GraphQLString)),
            description="The dimensions of the data IDs to yield. "
            "Will be automatically expanded to a complete DimensionGraph.",
        ),
        dataid=graphql.GraphQLArgument(
            graphql.GraphQLString,
            description="Data ID dict encoded as json. "
            "If provided, the key-value pairs are used as "
            "equality constraints in the query.",
        ),
        datasets=graphql.GraphQLArgument(
            graphql.GraphQLList(graphql.GraphQLString),
            description="Each element fully or partially identifies "
            "dataset types that should constrain the yielded data IDs. "
            "For example 'raw' constrains the yielded instrument, exposure, "
            "detector, and physical_filter values to only those "
            "for which at least one 'raw' dataset exists in collections. "
            "If any datasets or datasetregexs are specified then you must "
            "also specify collections and/or collectionregexs.",
        ),
        datasetregexs=graphql.GraphQLArgument(
            graphql.GraphQLList(graphql.GraphQLString),
            description="Like datasets, but each element "
            "is a regular expression.",
        ),
        collections=graphql.GraphQLArgument(
            graphql.GraphQLList(graphql.GraphQLString),
            description="Each element is an expression that fully "
            "or partially identifies the collections to search for datasets. "
            "At least one entry in collections or collectionregexs "
            "is required if any datasets or datasetregexs are specified; "
            "ignored otherwise.",
        ),
        collectionregexs=graphql.GraphQLArgument(
            graphql.GraphQLList(graphql.GraphQLString),
            description="Like collections, but each element "
            "is a regular expression.",
        ),
        where=graphql.GraphQLArgument(
            graphql.GraphQLString,
            description="A string expression similar to a SQL WHERE clause. "
            "May involve any column of a dimension table or (as a shortcut "
            "for the primary key column of a dimension table) dimension name.",
        ),
        components=graphql.GraphQLArgument(
            graphql.GraphQLBoolean,
            description="If True, apply all dataset expression patterns "
            "to component dataset type names as well. "
            "If False, never apply patterns to components. "
            "If None (default), apply patterns to components only if "
            "their parent datasets were not matched by the expression. "
            "Fully-specified component datasets are always included.",
        ),
        bind=graphql.GraphQLArgument(
            graphql.GraphQLString,
            description="Mapping containing literal values that should be "
            "injected into the where expression, keyed by the identifiers "
            "they replace. A json-encoded dict.",
        ),
        check=graphql.GraphQLArgument(
            graphql.GraphQLBoolean,
            default_value=True,
            description="If True (default) check the query for consistency "
            "before executing it. This may reject some valid queries "
            "that resemble common mistakes (e.g. queries for visits "
            "without specifying an instrument).",
        ),
        kwargs=graphql.GraphQLArgument(
            graphql.GraphQLString,
            description="Additional keyword arguments dict encoded as json. "
            "These arguments are forwarded to DataCoordinate.standardize "
            "when processing the dataId argument (and may be used to provide "
            "a constraining data ID even when the dataId argument is None).",
        ),
    ),
    resolve=simple_query_data_ids,
    description="Query for data IDs matching user-provided criteria.",
)
