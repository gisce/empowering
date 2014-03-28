from flask import Flask, request
from hashlib import sha1
import json
from uuid import uuid1

app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH'])
def main(path):
    print 'Path requested: %s %s' % (request.method, path)
    for key, value in request.headers:
        print "%s: %s" % (key, value)
    if request.json:
        print 'JSON: %s' % request.json
    else:
        print 'DATA: %s' % request.data
    if request.method in ('PATCH', 'POST') and request.json:
        if isinstance(request.json, list):
            res = []
            for item in request.json:
                res.append({
                    'etag': sha1(str(uuid1())).hexdigest(),
                    'orig': request.json
                })
        else:
            res = {'etag': sha1(str(uuid1())).hexdigest(),
                    'orig': request.json}
        print "======>"
        print "%s" % res
    else:
        res = {}
    return json.dumps(res)

if __name__ == '__main__':
    app.run(debug=True)
