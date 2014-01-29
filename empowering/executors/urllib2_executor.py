import urllib2
import httplib


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
