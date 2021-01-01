from __future__ import annotations

__all__ = ["simple_query_dimension_records"]

import asyncio
import functools
import json
import typing

import lsst.daf.butler
import lsst.sphgeom

from ..utils import StrOrRegexList, combine_strs_and_regex

if typing.TYPE_CHECKING:
    import aiohttp
    import graphql


def encode_record_dict(raw_dict: dict) -> str:
    """Convert the values in a record dict returned by the registry
    into plain old data types and json-encode the result.

    Encode `sphgeom.Region` using `sphgeom.Region.encode`.
    Encode `lsst.daf.butler.Timespan` as ``(begin time, end time)``,
    where both times are ISO strings.
    """
    encoded_dict = {}
    for key, raw_value in raw_dict.items():
        if isinstance(raw_value, lsst.daf.butler.Timespan):
            encoded_value = (raw_value.begin.isot, raw_value.end.isot)
        elif isinstance(raw_value, lsst.sphgeom.Region):
            encoded_value = raw_value.encode()
        else:
            encoded_value = raw_value
        encoded_dict[key] = encoded_value
    return json.dumps(encoded_dict)


async def simple_query_dimension_records(
    app: aiohttp.web.Application,
    _info: graphql.GraphQLResolveInfo,
    element: str,
    dataid: typing.Optional[str] = None,
    datasets: typing.Optional[list] = None,
    datasetregexs: typing.Optional[list] = None,
    collections: typing.Optional[list] = None,
    collectionregexs: typing.Optional[list] = None,
    where: typing.Optional[str] = None,
    components: typing.Optional[bool] = None,
    bind: typing.Optional[str] = None,
    check: bool = True,
    kwargs: typing.Optional[str] = None,
) -> typing.List[dict]:
    """Call registry.queryDimensionRecords and return plain old data.

    Parameters
    ----------
    app
        aiohttp application.
    _info
        Information about this request (ignored).
    The remaining parameters are described in the schema.

    Returns
    -------
    record_list
        Found records.
    """
    registry = app["butlerservice/butler"].registry

    if dataid is not None:
        try:
            dataid = json.loads(dataid)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Cannot decode dataid: {e}")
    if bind is not None:
        try:
            bind = json.loads(bind)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Cannot decode bind: {e}")

    all_collections = combine_strs_and_regex(
        str_list=collections, regex_list=collectionregexs
    )
    all_datasets = combine_strs_and_regex(
        str_list=datasets, regex_list=datasetregexs
    )
    if kwargs is None:
        kwargs_dict = {}
    else:
        kwargs_dict = json.loads(kwargs)

    loop = asyncio.get_running_loop()
    query_func = functools.partial(
        query_dimension_records,
        registry=registry,
        element=element,
        dataid=dataid,
        datasets=all_datasets,
        collections=all_collections,
        where=where,
        components=components,
        bind=bind,
        check=check,
        **kwargs_dict,
    )
    return await loop.run_in_executor(
        None,
        query_func,
    )


def query_dimension_records(
    registry: lsst.daf.butler.Registry,
    element: str,
    dataid: dict,
    datasets: StrOrRegexList,
    collections: StrOrRegexList,
    where: typing.Optional[str],
    components: list,
    bind: dict,
    check: bool,
    **kwargs: dict,
) -> typing.List[dict]:
    """Call queryDimensionRecords on a butler registry.

    Parameters
    ----------
    registry
        Butler registry.
    The remaining fields are described in
    `lsst.daf.butler.Registry.queryDimensionRecords`.

    Returns
    -------
    record_list
        List of data IDs as dicts with key=record, value=json-encoded dict.
    """
    recordclasses = registry.queryDimensionRecords(
        element=element,
        dataId=dataid,
        datasets=datasets,
        collections=collections,
        where=where,
        components=components,
        bind=bind,
        check=check,
        **kwargs,
    )
    return [
        dict(record=encode_record_dict(record.toDict()))
        for record in recordclasses
    ]
