"""
empowering.service
~~~~~~~~~~~~~~

:copyrigth: (c) 2013 by GISCE-TI, S.L. See AUTHORS for more details.
:licese: EUPL, see LICENSE for more details.
"""


import json

from libsaas.services import base
from libsaas import http, parsers


class EtagConcurrencyError(Exception):
    pass


def parse_eve(body, code, headers):
    if code == 412:
        raise EtagConcurrencyError
    else:
        return parsers.parse_json(body, code, headers)


class EmpoweringResource(base.RESTResource):

    @base.apimethod
    def update(self, obj, etag):
        self.require_item()
        request = http.Request('PATCH', self.get_url(), self.wrap_object(obj),
                               headers={"If-Match": etag})
        return request, parse_eve

    @base.apimethod
    def delete(self, obj, etag):
        self.require_item()
        request = http.Request('DELETE', self.get_url(), self.wrap_object(obj),
                               headers={"If-Match": etag})
        return request, parse_eve


class Contracts(EmpoweringResource):
    path = 'contracts'


class AmonMeasures(EmpoweringResource):
    path = 'amon_measures'

    @base.apimethod
    def get(self):
        raise base.MethodNotSupported

    @base.apimethod
    def update(self, obj, etag):
        raise base.MethodNotSupported

    @base.apimethod
    def delete(self, obj, etag):
        raise base.MethodNotSupported


class Measures(EmpoweringResource):
    path = 'measures'

    @base.apimethod
    def get(self):
        raise base.MethodNotSupported

    @base.apimethod
    def create(self, obj):
        raise base.MethodNotSupported

    @base.apimethod
    def update(self, obj, etag):
        raise base.MethodNotSupported

    @base.apimethod
    def delete(self, start=None, end=None):
        params = base.get_params(('start', 'end'), locals())
        request = http.Request('DELETE', self.get_url())
        return request, parsers.parse_json

class Empowering(base.Resource):
    """
    Empowering Insight Engine Service API.
    """
    def __init__(self, company_id, version='v1'):
        self.token = company_id
        endpoint = "http://91.121.140.152:5001"
        #endpoint = "http://localhost:5000"
        self.apiroot = '%s/%s' % (endpoint, version)
        self.add_filter(self.use_json)

    def use_json(self, request):
        if request.method.upper() not in http.URLENCODE_METHODS:
            request.headers['Content-Type'] = 'application/json'
            request.params = json.dumps(request.params)

    def get_url(self):
        return self.apiroot

    @base.resource(AmonMeasures)
    def amon_measures(self):
        return AmonMeasures(self)

    @base.resource(Measures)
    def measures(self):
        return Measures(self)

    @base.resource(Contracts)
    def contract(self, contract_id):
        return Contracts(self, contract_id)

    @base.resource(Contracts)
    def contracts(self):
        return Contracts(self)