import os

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
    domain = os.environ.get('domain')
    if domain is None:
        return Response("Missing domain", status=500)

    api_key = os.environ.get('api_key')
    if api_key is None:
        return Response("Missing api key", status=500)
    try:
        server = getmarc2.records.RecordServer(domain, api_key)
        data = server.bibid_record(bibid)
        header = {"x-api-version": "v1"}
        return Response(data, headers=header, content_type="text/xml")
    except AttributeError as e:
        return Response(f"Failed. {e}", 400, content_type="text")

# TODO: load configuration


if __name__ == '__main__':
    app.run(host='0.0.0.0')
