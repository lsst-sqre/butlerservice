from __future__ import annotations

__all__ = ["simple_query_data_ids"]

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


async def simple_query_data_ids(
    app: aiohttp.web.Application,
    _info: graphql.GraphQLResolveInfo,
    dimensions: typing.List[str],
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
    """Call registry.queryDataIds and return plain old data.

    Parameters
    ----------
    app
        aiohttp application.
    _info
        Information about this request (ignored).
    The remaining parameters are described in the schema.

    Returns
    -------
    data_id_list
        List of data IDs as json-encoded dicts.
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

    query_func = functools.partial(
        query_dimension_records,
        registry=registry,
        dimensions=dimensions,
        dataid=dataid,
        datasets=all_datasets,
        collections=all_collections,
        where=where,
        components=components,
        bind=bind,
        check=check,
        **kwargs_dict,
    )

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        query_func,
    )


def query_dimension_records(
    registry: lsst.daf.butler.Registry,
    dimensions: typing.List[str],
    dataid: dict,
    datasets: StrOrRegexList,
    collections: StrOrRegexList,
    where: typing.Optional[str],
    components: list,
    bind: dict,
    check: bool,
    **kwargs: dict,
) -> typing.List[dict]:
    """Call queryDataIds on a butler registry.

    Parameters
    ----------
    registry
        Butler registry.
    The remaining fields are described in
    `lsst.daf.butler.Registry.queryDataIds`.

    Returns
    -------
    data_id_list
        List of data IDs as dicts with key=data_id, value=json-encoded dict.
    """
    try:
        data_id_list = registry.queryDataIds(
            dimensions=dimensions,
            dataId=dataid,
            datasets=datasets,
            collections=collections,
            where=where,
            components=components,
            bind=bind,
            check=check,
            **kwargs,
        ).toSequence()
        data_id_dicts = [
            {key.name: value for key, value in data_id.items()}
            for data_id in data_id_list
        ]
        return [
            dict(data_id=json.dumps(data_id_dict))
            for data_id_dict in data_id_dicts
        ]
    except Exception as e:
        print(f"Error in Registry.queryDataIds: {e}")
    return []
