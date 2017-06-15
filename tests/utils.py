import unittest
from base64 import b64encode

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from app import app

def build_auth_headers(username, password):
    headers = {
        'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password))
    }
    return headers

class BaseTestClass(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.app = app.test_client()
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()


