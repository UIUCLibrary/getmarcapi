import os
from typing import Mapping
from .config import get_config
from flask import Flask, Response, request
from uiucprescon import getmarc2
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index() -> str:
    return "Sample"


@app.route('/record')
def get_record() -> Response:
    bibid = request.args.get("bibid")
    if bibid is None:
        return Response("Missing required param bibid", status=422)

    get_config(app)
    domain = app.config.get('API_DOMAIN')
    if domain is None:
        return Response("Missing domain", status=500)

    api_key = app.config.get('API_KEY')
    if api_key is None:
        return Response("Missing api key", status=500)

    try:
        server = getmarc2.records.RecordServer(domain, api_key)
        data = server.bibid_record(bibid)
        header = {"x-api-version": "v1"}
        return Response(data, headers=header, content_type="text/xml")
    except AttributeError as e:
        return Response(f"Failed. {e}", 400, content_type="text")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
