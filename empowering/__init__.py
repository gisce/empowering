try:
    VERSION = __import__('pkg_resources') \
        .get_distribution(__name__).version
except Exception, e:
    VERSION = 'unknown'

from service import Empowering
from utils import fix_ssl_verify

fix_ssl_verify()
