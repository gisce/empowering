import urllib2
import httplib
import logging
import json
from urlparse import urlparse, urlunparse
from libsaas.executors import base, urllib2_executor


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
        logger.debug('using https connection (key file:{} Cert file:{})'.format(
            self.key_file, self.cert_file
        ))
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
            newr = urllib2_executor.RequestWithMethod(
                newurl, request.data, request.headers, request.origin_req_host,
                request.unverifiable
            )
            newr.timeout = request.timeout
            newr.set_method(request.get_method())
            return newr
        else:
            return request
    https_request = http_request


class HTTPAuthEmpowering(urllib2.BaseHandler):

    def __init__(self, username, password, endpoint):
        self.username = username
        self.password = password
        self.token = None
        self.endpoint = endpoint
        self.retried = 0
        self.max_retries = 1

    def http_error_401(self, req, fp, code, msg, headers):
        logger.debug("Login required. Retry auth")
        response = self.retry_auth(req, headers)
        self.reset_retry_count()
        return response

    def login(self):
        data = json.dumps({
            "username": self.username, "password": self.password
        })
        req = urllib2.Request(self.endpoint, data)
        req.headers['Content-Type'] = 'application/json'
        response = urllib2.urlopen(req)
        auth = json.loads(response.read())
        self.token = auth['token']
        response.close()
        return auth

    def reset_retry_count(self):
        self.retried = 0

    def retry_auth(self, req, headers):
        if self.retried >= self.max_retries:
            return urllib2.HTTPError(
                req.get_full_url(), 401, "Auth failed", headers, None
            )
        auth = self.login()
        self.reset_retry_count()
        req.headers['Cookie'] = "iPlanetDirectoryPro={}".format(auth['token'])
        return self.parent.open(req, timeout=req.timeout)


class Urllib2Executor(urllib2_executor.Urllib2Executor):
    def __init__(self, extra_handlers):
        self.handlers = extra_handlers


def use(extra_handlers=()):
    base.use_executor(Urllib2Executor(extra_handlers=extra_handlers))