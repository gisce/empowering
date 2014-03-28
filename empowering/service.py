"""
empowering.service
~~~~~~~~~~~~~~

:copyrigth: (c) 2013 by GISCE-TI, S.L. See AUTHORS for more details.
:licese: EUPL, see LICENSE for more details.
"""


import json

from libsaas.services import base
from libsaas import http, parsers
from libsaas.executors import urllib2_executor
from .executors.urllib2_executor import HTTPSClientAuthHandler, HTTPEmpoweringFilterHandler

from empowering.results import *


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

    @base.apimethod
    def get(self, where=None, sort=None):
        sort = sort and sort.replace(' ', '')
        params = base.get_params(('where', 'sort'), locals())
        request = http.Request('GET', self.get_url(), params)

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
    def __init__(self, company_id, key_file, cert_file, version='v1'):
        self.company_id = company_id
        self.key_file = key_file
        self.cert_file = cert_file
        endpoint = "https://api.empowering.cimne.com"
        self.apiroot = '%s/%s' % (endpoint, version)
        self.add_filter(self.use_json)
        self.add_filter(self.add_company_id)

        # We have to use SSL Client
        https_handler = HTTPSClientAuthHandler(self.key_file, self.cert_file)
        filter_handler = HTTPEmpoweringFilterHandler()
        urllib2_executor.use(extra_handlers=(https_handler, filter_handler))

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

    @base.resource(OT101Results)
    def ot101_result(self, result_id):
        return OT101Results(self, result_id)

    @base.resource(OT101Results)
    def ot101_results(self):
        return OT101Results(self)

    @base.resource(OT103Results)
    def ot103_result(self, result_id):
        return OT103Results(self, result_id)

    @base.resource(OT103Results)
    def ot103_results(self):
        return OT103Results(self)

    @base.resource(OT106Results)
    def ot106_result(self, result_id):
        return OT106Results(self, result_id)

    @base.resource(OT106Results)
    def ot106_results(self):
        return OT106Results(self)

    @base.resource(OT201Results)
    def ot201_result(self, result_id):
        return OT201Results(self, result_id)

    @base.resource(OT201Results)
    def ot201_results(self):
        return OT201Results(self)

    @base.resource(OT204Results)
    def ot204_result(self, result_id):
        return OT204Results(self, result_id)

    @base.resource(OT204Results)
    def ot204_results(self):
        return OT204Results(self)

    @base.resource(BT111Results)
    def bt111_result(self, result_id):
        return BT111Results(self, result_id)

    @base.resource(BT111Results)
    def bt111_results(self):
        return BT111Results(self)