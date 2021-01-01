from __future__ import annotations

import asyncio
import json
import os
import pathlib
import shutil
import subprocess
from typing import Optional

import aiohttp
import pytest

from butlerservice.format_http_request import format_http_request

# Time limit for `butlerservice create-table` (sec).
CREATE_TIMEOUT = 5

# Time limit for terminating a process (sec).
TERMINATE_TIMEOUT = 5

# Time to pause after executing `butlerservice run`
# before trying to use it (sec).
RUN_DELAY = 2


@pytest.mark.asyncio
async def test_cli() -> None:
    """Test butlerservice create-table and run command-line commands."""
    repo_path = pathlib.Path(__file__).parent / "data" / "hsc_raw"
    os.environ["BUTLER_URI"] = str(repo_path)

    exe_path = shutil.which("butlerservice")
    assert (
        exe_path is not None
    ), "Could not find 'butlerservice' bin script; you must build this package"

    # Check `butlerservice run` with and without the --port argument
    for port in (None, 8001):
        await check_run(port=port)


async def check_run(
    port: Optional[int],
) -> None:
    """Run `butlerservice run` and use it to add one message.

    Before calling this you must have a database running.

    Parameters
    ----------
    port
        Port on which to run the butlerservice service.
        If None then run without specifying a port,
        which uses the default port 8080.
    message_id
        Expected ID of the added message.
    """

    cmdline_args = ["butlerservice", "run"]
    if port is None:
        port = 8080
    else:
        cmdline_args += ["--port", str(port)]

    run_process = await asyncio.create_subprocess_exec(
        *cmdline_args,
        stderr=subprocess.PIPE,
    )
    try:
        async with aiohttp.ClientSession() as session:

            # Give the exposure log service time to start.
            await asyncio.sleep(RUN_DELAY)

            # Find an item
            query_record_args = dict(
                element="exposure",
                dataid=json.dumps(dict(instrument="HSC")),
            )
            query_data, headers = format_http_request(
                category="query",
                command="simple_query_dimension_records",
                args_dict=query_record_args,
                fields=["record"],
            )
            r = await session.post(
                f"http://localhost:{port}/butlerservice",
                data=query_data,
                headers=headers,
            )
            assert r.status == 200
            reply_data = await r.json()
            assert "error" not in reply_data
            assert (
                len(reply_data["data"]["simple_query_dimension_records"]) == 11
            )

    finally:
        if run_process.returncode is None:
            # `butlerservice run` is still running, as it should be. Stop it.
            run_process.terminate()
            await asyncio.wait_for(
                run_process.wait(), timeout=TERMINATE_TIMEOUT
            )
        else:
            # The `butlerservice run` process unexpectedly quit.
            # This would likely cause other test failures,
            # so report process termination instead of any other errors.
            # Try to include stderr from the process in the error message.
            try:
                stderr_bytes = await run_process.stderr.read()  # type: ignore
                stderr_msg = stderr_bytes.decode()
            except Exception as e:
                stderr_msg = f"could not read stderr: {e}"
            raise AssertionError(f"run_process failed: {stderr_msg}")
