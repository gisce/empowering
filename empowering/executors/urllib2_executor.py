import urllib2
import httplib
import logging
from urlparse import urlparse, urlunparse
from libsaas.executors.urllib2_executor import RequestWithMethod


logger = logging.getLogger('empowering.executors.urllib2_executor')


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    """HTTPS Client Auth Handler.

    (c) Kalys Osmonov - http://www.osmonov.com/2009/04/client-certificates-with-urllib2.html
    """
    def __init__(self, key_file, cert_file):
        urllib2.HTTPSHandler.__init__(self)
        self.key_file = key_file
        self.cert_file = cert_file

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key_file,
                                       cert_file=self.cert_file)


class HTTPEmpoweringFilterHandler(urllib2.BaseHandler):

    def http_request(self, request):
        if request.get_method() == 'GET':
            url = urlparse(request.get_full_url())
            newurl = urlunparse((
                url.scheme,
                url.netloc,
                url.path,
                url.params,
                urllib2.unquote(url.query),
                url.fragment
            ))
            logger.debug("New url set to %s" % newurl)
            newr = RequestWithMethod(newurl, request.data, request.headers,
                                    request.origin_req_host,
                                    request.unverifiable)
            newr.timeout = request.timeout
            newr.set_method(request.get_method())
            return newr
        else:
            return request
    https_request = http_request
