"""Main app module for loading the routes."""
import logging
import sys
import argparse
from flask import Flask, Response, request
from uiucprescon import getmarc2
from uiucprescon.getmarc2 import modifiers
from .records import RecordGetter

from . import config

app = Flask(__name__)

if __name__ != '__main__':
    # pylint: disable=no-member
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
        app.logger.debug("Missing bibid request")  # pylint: disable=no-member
        return Response("Missing required param bibid", status=422)

    config.get_config(app)
    domain = app.config.get('API_DOMAIN')
    if domain is None:
        return Response("Missing domain", status=500)

    api_key = app.config.get('API_KEY')
    if api_key is None:
        return Response("Missing api key", status=500)
    bibid_value = str(bibid).strip()
    try:
        record_lookup_strategy = RecordGetter(request.args)
        identifier = record_lookup_strategy.get_identifier(request.args)
        metadata_record = \
            record_lookup_strategy.get_record(
                server=getmarc2.records.RecordServer(domain, api_key),
                identifier=identifier
            )

        header = {"x-api-version": "v1"}
        app.logger.info(f"Retrieved record for {identifier}")

        field_adder = modifiers.Add955()
        field_adder.bib_id = bibid
        if "v" in bibid:
            field_adder.contains_v = True

        metadata_record = field_adder.enrich(metadata_record)

        return \
            Response(metadata_record, headers=header, content_type="text/xml")

    except AttributeError as error:
        # pylint: disable=no-member
        app.logger.info(f"Failed to retrieve bibid {bibid_value}")
        return Response(f"Failed. {error}", 400, content_type="text")


def get_cli_parser() -> argparse.ArgumentParser:
    """Get the parser for command line arguments.

    Returns:
        Parser for cli args

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action='store_true')
    return parser


def main(args=None, config_checker=None) -> None:
    """Run the main entry point for the CLI.

    Args:
        args: Command line Arguments
        config_checker: Checker for validating configuration

    """
    config.get_config(app)

    args = args or get_cli_parser().parse_args()
    if args.check:
        check_config = config_checker or config.check_config
        if check_config(app) is False:
            sys.exit(1)
        else:
            sys.exit(0)

    app.run()


if __name__ == '__main__':
    main()
