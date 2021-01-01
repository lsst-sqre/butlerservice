from __future__ import annotations

__all__ = [
    "MessageDictT",
    "Requestor",
    "assert_bad_response",
    "assert_good_response",
    "expected_exposure_id_list",
    "expected_day_obs_list",
]

import typing

from butlerservice.format_http_request import format_http_request

if typing.TYPE_CHECKING:
    import aiohttp
    import aiohttp.test_utils


# Type annotation aliases
MessageDictT = typing.Dict[str, typing.Any]
ArgDictT = typing.Dict[str, typing.Any]


class Requestor:
    """Functor to issue GraphQL requests.

    Parameters
    ----------
    client
        aiohttp client.
    category
        Default request category: "mutation" or "query"
    command
        Default command.
    fields
        Fields to return.
    url_suffix
        URL suffix for requests, e.g. butler
    """

    def __init__(
        self,
        client: aiohttp.test_utils.TestClient,
        category: str,
        command: str,
        fields: typing.Sequence[str],
        url_suffix: str,
    ):
        if category not in ("mutation", "query"):
            raise ValueError(f"category={category} must be mutation or query")
        self.client = client
        self.category = category
        self.command = command
        self.fields = fields
        self.url_suffix = url_suffix

    async def __call__(
        self,
        args_dict: dict,
        category: typing.Optional[str] = None,
        command: typing.Optional[str] = None,
    ) -> aiohttp.ClientResponse:
        """Issue a request.

        Parameters
        ----------
        command
            Command to issue.
        args_dict
            Arguments for the command.

        Returns
        -------
        response
            Client response.
        """
        if category is None:
            category = self.category
        if command is None:
            command = self.command
        args_data, headers = format_http_request(
            category=category,
            command=command,
            args_dict=args_dict,
            fields=self.fields,
        )
        return await self.client.post(
            self.url_suffix, json=args_data, headers=headers
        )


async def assert_bad_response(response: aiohttp.ClientResponse) -> dict:
    """Check the response from an unsuccessful request.

    Parameters
    ----------
    response
        Response to HTTP request.

    Returns
    -------
    data
        The full data returned from response.json()
    """
    assert response.status == 200
    data = await response.json()
    assert "errors" in data
    return data


async def assert_good_response(
    response: aiohttp.ClientResponse, command: str = None
) -> typing.Any:
    """Assert that a response is good and return the data.

    Parameters
    ----------
    command
        The command. If None then return the whole response, else return
        the response from the command (response["data"][command]) --
        a single message dict or a list of messages dicts.
    """
    data = await response.json()
    assert (
        response.status == 200
    ), f"response={response.status} != 200; data={data}"
    assert "errors" not in data, f"errors={data['errors']}"
    if command:
        return data["data"][command]
    return data


# day_obs values from the exposure table.
expected_day_obs_list = [
    20130617,
    20130617,
    20130617,
    20130617,
    20131102,
    20131102,
    20131102,
    20130617,
    20131102,
    20131102,
    20130617,
]

# id values from the exposure table.
expected_exposure_id_list = [
    903344,
    903336,
    903338,
    903346,
    904014,
    903990,
    904010,
    903342,
    903988,
    903986,
    903334,
]
