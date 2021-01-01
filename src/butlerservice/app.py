"""The main application definition for butler service."""

__all__ = ["create_app"]

import typing

from aiohttp import web
from graphql_server.aiohttp import GraphQLView
from lsst.daf.butler import Butler
from safir.http import init_http_session
from safir.logging import configure_logging
from safir.metadata import setup_metadata
from safir.middleware import bind_logger

from butlerservice.config import Configuration
from butlerservice.schemas.app_schema import app_schema


def create_app(**configs: typing.Any) -> web.Application:
    """Create and configure the aiohttp.web application."""
    # Cast all values to str to support butler URIs as pathlib.Path.
    configs = {key: str(value) for key, value in configs.items()}
    config = Configuration(**configs)
    configure_logging(
        profile=config.profile,
        log_level=config.log_level,
        name=config.logger_name,
    )

    if not config.butler_uri:
        raise ValueError("Must specify BUTLER_URI")
    butler = Butler(config.butler_uri)

    root_app = web.Application()
    root_app["safir/config"] = config
    root_app["butlerservice/butler"] = butler
    setup_metadata(package_name="butlerservice", app=root_app)
    setup_middleware(root_app)
    root_app.cleanup_ctx.append(init_http_session)

    GraphQLView.attach(
        root_app,
        schema=app_schema,
        route_path="/butlerservice",
        root_value=root_app,
        enable_async=True,
        graphiql=True,
    )

    sub_app = web.Application()
    setup_middleware(sub_app)
    root_app.add_subapp(f'/{root_app["safir/config"].name}', sub_app)

    return root_app


def setup_middleware(app: web.Application) -> None:
    """Add middleware to the application."""
    app.middlewares.append(bind_logger)
