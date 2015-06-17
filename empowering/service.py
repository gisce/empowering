"""
empowering.service
~~~~~~~~~~~~~~

:copyrigth: (c) 2013 by GISCE-TI, S.L. See AUTHORS for more details.
:licese: EUPL, see LICENSE for more details.
"""


import json
from warnings import warn

from libsaas.services import base
from libsaas import http, parsers
from libsaas.executors import urllib2_executor as base_executor
from empowering.executors import urllib2_executor
from empowering.executors.urllib2_executor import (
    HTTPSClientAuthHandler, HTTPEmpoweringFilterHandler, HTTPAuthEmpowering,
)
from empowering.resource import EmpoweringResource
from empowering.results import *


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


class AmonMeasuresMeasurements(EmpoweringResource):
    path = 'amon_measures_measurements'

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


class Measures(AmonMeasuresMeasurements):
    def __init__(self, *args, **kwargs):
        super(AmonMeasuresMeasurements, self).__init__(*args, **kwargs)
        warn('Deprecated class. Use AmonMeasuresMeasurements',
             DeprecationWarning)


class Empowering(base.Resource):
    """
    Empowering Insight Engine Service API.
    """
    def __init__(self, company_id, username=None, password=None, key_file=None,
                 cert_file=None, version='v1', debug=False):
        self.company_id = str(company_id)
        self.key_file = key_file
        self.cert_file = cert_file
        self.version = version
        self.apiroot = "https://api.empowering.cimne.com"
        if debug:
            self.apiroot = "https://91.121.140.152"
        self.login_handler = None
        self.add_filter(self.use_json)
        self.add_filter(self.add_company_id)
        self.add_filter(self.add_cookie_token)
        self.setup_executor()
        if username and password:
            self.login(username, password)

    @property
    def token(self):
        return self.login_handler and self.login_handler.token

    def setup_executor(self, extra_handlers=None):
        if extra_handlers is None:
            extra_handlers = ()
        extra_handlers += (HTTPEmpoweringFilterHandler(), )
        if self.key_file and self.cert_file:
            extra_handlers += (
                HTTPSClientAuthHandler(self.key_file, self.cert_file),
            )

        urllib2_executor.use(extra_handlers)

    def use_json(self, request):
        if request.method.upper() not in http.URLENCODE_METHODS:
            request.headers['Content-Type'] = 'application/json'
            request.params = json.dumps(request.params)

    def add_company_id(self, request):
        request.headers['X-CompanyId'] = self.company_id

    def add_cookie_token(self, request):
        if self.token:
            request.headers['Cookie'] = "iPlanetDirectoryPro=%s" % self.token

    def get_url(self):
        return "{0}/{1}".format(self.apiroot, self.version)

    def login(self, user, password):
        if self.login_handler and self.token:
            return {'success': True, 'token': self.token}
        endpoint = "{}/authn/login".format(self.apiroot)
        self.login_handler = HTTPAuthEmpowering(user, password, endpoint)
        auth = self.login_handler.login()
        self.setup_executor((self.login_handler, ))
        return auth

    def logout(self):
        if not self.token:
            return {'success': True}
        else:
            endpoint = '{0}/authn/logout'.format(self.apiroot)
            request = http.Request('GET', endpoint)
            self.use_json(request)
            self.add_company_id(request)
            self.add_cookie_token(request)

            executor = base_executor.base.current_executor()
            auth = executor(request, parsers.parse_json)
            if auth.get('success'):
                self.login_handler.token = None
            return auth

    @base.resource(AmonMeasures)
    def amon_measures(self):
        return AmonMeasures(self)

    @base.resource(Measures)
    def measures(self):
        warn('Deprecated. Use amon_measures_measurements', DeprecationWarning)
        return Measures(self)

    @base.resource(AmonMeasuresMeasurements)
    def amon_measures_measurements(self):
        return AmonMeasuresMeasurements(self)

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

    @base.resource(OT503Results)
    def ot503_results(self):
        return OT503Results(self)

    @base.resource(OT900Results)
    def ot900_results(self):
        return OT900Results(self)

    @base.resource(BT111Results)
    def bt111_result(self, result_id):
        return BT111Results(self, result_id)

    @base.resource(BT111Results)
    def bt111_results(self):
        return BT111Results(self)
