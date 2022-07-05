# -*- coding: utf-8 -*-
from urlparse import urlparse, parse_qs

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
    def get(self, where=None, sort=None, rid=None):
        sort = sort and sort.replace(' ', '')
        params = base.get_params(('where', 'sort'), locals())
        url = self.get_url()
        if rid:
            url = '{}/{}'.format(url, rid)
        request = http.Request('GET', url, params)

        return request, parsers.parse_json

    def multiget(self, where=None, sort=None, max_results=None):
        query = where or ''
        if max_results:
            query += '&max_results=%d' % max_results
        page = 0
        all_results = {'_items': []}
        more_items = True
        while more_items:
            more_items = False

            if page:
                paged_query = query + '&page=%s' % page
            else:
                paged_query = query
            result = self.get(where=paged_query, sort=sort)
            if '_items' in result:
                all_results['_items'].extend(result['_items'])

            if 'next' in result['_links']:
                qs = urlparse(result['_links']['next']['href']).query
                page = parse_qs(qs).get('page', ['0'])[0]
                more_items = True
        return all_results


