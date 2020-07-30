"""Main app module for loading the routes."""
import logging
import sys
import argparse
from flask import Flask, Response, request
from uiucprescon import getmarc2
from .config import get_config, check_config

app = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.DEBUG)
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/', methods=['GET'])
def index() -> str:
    """Root page of the api. Something will go here sometime.

    Returns:
        Nothing really goes here yet
    """
    return "Sample!"


@app.route('/record')
def get_record() -> Response:
    """Get the record data for a given bibid.

    Returns:
        XML data

    """
    bibid = request.args.get("bibid")

    if bibid is None:
        app.logger.debug("Missing bibid request")
        return Response("Missing required param bibid", status=422)

    get_config(app)
    domain = app.config.get('API_DOMAIN')
    if domain is None:
        return Response("Missing domain", status=500)

    api_key = app.config.get('API_KEY')
    if api_key is None:
        return Response("Missing api key", status=500)
    bibid_value = str(bibid).strip()
    try:
        server = getmarc2.records.RecordServer(domain, api_key)
        data = server.bibid_record(bibid)
        header = {"x-api-version": "v1"}
        app.logger.info(f"Retrieved record for bibid {bibid_value}")
        return Response(data, headers=header, content_type="text/xml")
    except AttributeError as error:
        app.logger.info(f"Failed to retrieve bibid {bibid_value}")
        return Response(f"Failed. {error}", 400, content_type="text")


def get_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action='store_true')
    return parser


def main():
    get_config(app)

    args = get_cli_parser().parse_args()
    if args.check:
        sys.exit(1) if check_config(app) is False else sys.exit()

    return app.run()


if __name__ == '__main__':
    main()
