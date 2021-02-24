"""Main app module for loading the routes."""
import logging
import sys
import argparse
from typing import Tuple, Optional, Mapping, Callable, TypedDict, List

from flask import Flask, Response, request, render_template, jsonify
from werkzeug.routing import Rule
from uiucprescon import getmarc2
from uiucprescon.getmarc2 import modifiers
from .records import RecordGetter

from . import config

app: Flask = Flask(__name__)

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
        The front page with basic about and help information/
    """
    return render_template("layout.html")


def arg_issues(args: Mapping[str, str]) -> Optional[Tuple[str, int]]:
    """Validate the request arguments.

    Args:
        args:

    Returns:
        Issues discovered in the arguments and a recommended return code

    """
    bibid = args.get("bib_id")
    mms_id = args.get("mms_id")
    if bibid is None and mms_id is None:
        return "Missing bib_id or mms_id request", 422

    return None


@app.route('/api', endpoint="api_documentation")
def api_documentation() -> Response:
    """Get the API documentation in json format.

    Returns:
        API documentation in json format

    """
    ignored_rules = ['static']

    class SerializedRoute(TypedDict):
        """Method listing for a route."""

        route: str
        methods: List[str]

    def serialize(data: Rule) -> SerializedRoute:
        return {
            "route": str(data),
            "methods": list(data.methods),
        }

    results = list(
        map(serialize, filter(lambda x: x.endpoint not in ignored_rules,
                              app.url_map.iter_rules()))
    )
    return jsonify(results)


@app.route('/api/record', endpoint="record_api")
def get_record() -> Response:
    """Get the record data for a given bibid.

    Returns:
        XML data

    """
    issue = arg_issues(request.args)
    if issue:
        issue_text, recommended_status_code = issue
        app.logger.debug(issue_text)  # pylint: disable=no-member
        return Response(issue_text, status=recommended_status_code)

    config.get_config(app)
    domain = app.config.get('API_DOMAIN')
    if domain is None:
        return Response("Missing domain", status=500)

    api_key = app.config.get('API_KEY')
    if api_key is None:
        return Response("Missing api key", status=500)

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

        if 'bib_id' in request.args:
            field_adder = modifiers.Add955()
            bibid = request.args["bib_id"]
            field_adder.bib_id = bibid
            if "v" in bibid:
                field_adder.contains_v = True

            metadata_record = field_adder.enrich(metadata_record)

        return \
            Response(metadata_record, headers=header, content_type="text/xml")

    except AttributeError as error:
        # pylint: disable=no-member
        app.logger.info("Failed to retrieve record")
        return Response(f"Failed. {error}", 400, content_type="text")


def get_cli_parser() -> argparse.ArgumentParser:
    """Get the parser for command line arguments.

    Returns:
        Parser for cli args

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action='store_true')
    return parser


def main(
        args: Optional[argparse.Namespace] = None,
        config_checker: Optional[Callable[[Flask], bool]] = None
) -> None:
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
