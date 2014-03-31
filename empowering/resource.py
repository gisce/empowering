# -*- coding: utf-8 -*-

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

    @base.apimethod
    def get(self, where=None, sort=None):
        sort = sort and sort.replace(' ', '')
        params = base.get_params(('where', 'sort'), locals())
        request = http.Request('GET', self.get_url(), params)

        return request, parsers.parse_json