"""
empowering.service
~~~~~~~~~~~~~~

:copyrigth: (c) 2013 by GISCE-TI, S.L. See AUTHORS for more details.
:licese: EUPL, see LICENSE for more details.
"""


import json

from libsaas.services import base
from libsaas import http, parsers


class EmpoweringResource(base.RESTResource):

    @base.apimethod
    def update(self, obj, etag):
        self.require_item()
        request = http.Request('PATCH', self.get_url(), self.wrap_object(obj),
                               headers={"If-Match": etag})
        return request, parsers.parse_json

    @base.apimethod
    def delete(self, etag):
        request = http.Request('DELETE', self.get_url(),
                               headers={"If-Match": etag})
        return request, parsers.parse_json


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
        self.company_id = company_id
        endpoint = "https://api.empowering.cimne.com"
        self.apiroot = '%s/%s' % (endpoint, version)
        self.add_filter(self.use_json)
        self.add_filter(self.add_company_id)

    def use_json(self, request):
        if request.method.upper() not in http.URLENCODE_METHODS:
            request.headers['Content-Type'] = 'application/json'
            request.params = json.dumps(request.params)

    def add_company_id(self, request):
        request.headers['X-CompanyId'] = self.company_id

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