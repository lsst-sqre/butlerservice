from __future__ import annotations

import json
import pathlib
import typing

from butlerservice.app import create_app
from butlerservice.testutils import (
    Requestor,
    assert_good_response,
    expected_exposure_id_list,
)

if typing.TYPE_CHECKING:
    import aiohttp
    from aiohttp.pytest_plugin.test_utils import TestClient


class doc_str:
    """Decorator to add a doc string to a function.

    Unlike the standard technique, this works with f strings
    """

    def __init__(self, doc: str):
        self.doc = doc

    def __call__(self, func: typing.Callable) -> typing.Callable:
        func.__doc__ = self.doc
        return func


async def assert_good_query_response(
    response: aiohttp.ClientResponse,
) -> typing.Sequence[dict]:
    raw_records = await assert_good_response(
        response, command="simple_query_data_ids"
    )
    data_ids = [json.loads(raw_rec["data_id"]) for raw_rec in raw_records]
    assert len(data_ids) == 11
    assert [
        data_id["exposure"] for data_id in data_ids
    ] == expected_exposure_id_list
    return data_ids


async def test_simple_query_data_ids(
    aiohttp_client: TestClient,
) -> None:
    repo_path = pathlib.Path(__file__).parent / "data" / "hsc_raw"
    app = create_app(butler_uri=repo_path)
    name = app["safir/config"].name

    client = await aiohttp_client(app)

    requestor = Requestor(
        client=client,
        category="query",
        command="simple_query_data_ids",
        fields=["data_id"],
        url_suffix=name,
    )

    # Query with dataid
    query_record_args = dict(
        dimensions=["exposure"],
        dataid=json.dumps(dict(instrument="HSC")),
    )
    response = await requestor(args_dict=query_record_args)
    await assert_good_query_response(response)

    # Query with where
    query_record_args = dict(dimensions=["exposure"], where="instrument='HSC'")
    response = await requestor(args_dict=query_record_args)
    await assert_good_query_response(response)

    # Query with kwargs
    query_record_args = dict(
        dimensions=["exposure"],
        kwargs=json.dumps(dict(instrument="HSC")),
    )
    response = await requestor(args_dict=query_record_args)
    await assert_good_query_response(response)
