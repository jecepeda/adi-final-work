# tests/handlers/test_api.py
import unittest
from urllib import quote_plus
from base64 import b64encode
import json

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


class UserEndpointTest(BaseTestClass):

    def testUserCreated(self):
        user_info = {'id':'foo@bar.com', 'nick':'foo', 'name':'Foo', 'lastName':'bar', 'password':'foobar'}
        response = self.app.post('/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.data)
        self.assertEqual(content, {'created':'foo@bar.com'})

    def testUserNotValidNotEnoughData(self):
        user_info = {'id':'bar@foo.com', 'nick':'foobar'}
        response = self.app.post('/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testUserExistsAndFails(self):
        user_info = {'id':'foo@bar.com', 'nick':'foo', 'name':'Foo', 'lastName':'bar', 'password':'foobar'}
        response = self.app.post('/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testFalseEmail(self):
        user_info = {'id':'foobar.com', 'nick':'foo', 'name':'Foo', 'lastName':'bar', 'password':'foobar'}
        response = self.app.post('/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testGetAll(self):
        user_info = {'id':'foo@bar.com', 'nick':'foo', 'name':'Foo', 'lastName':'bar', 'password':'foobar'}
        self.app.post('/user', data=json.dumps(user_info), content_type='application/json')
        response = self.app.get('/user')
        content = json.loads(response.data)
        expected_content = [{'id':'foo@bar.com', 'nick':'foo','name':'Foo','lastName':'bar'}]
        self.assertEqual(content, expected_content)

    def testGetAllEmptyTable(self):
        response = self.app.get('/user')
        content = json.loads(response.data)
        expected_content = []
        self.assertEqual(content, expected_content)


class UserEndpointSpecificUser(BaseTestClass):

    def setUp(self):
        super(UserEndpointSpecificUser, self).setUp()
        self.user_info = {'id':'foo@bar.com', 'nick':'foo', 'name':'Foo', 'lastName':'bar', 'password':'foobar'}
        self.app.post('/user', data=json.dumps(self.user_info), content_type='application/json')

    def testGetCorrectlyTheUser(self):
        quoted_url = quote_plus(self.user_info['id'])
        response = self.app.get('/user/{}'.format(quoted_url))
        self.assertEqual(response.status_code, 200)
        expected_content = {'id':'foo@bar.com', 'nick':'foo','name':'Foo','lastName':'bar'}
        content = json.loads(response.data)
        self.assertEqual(content, expected_content)
        self.assertEqual(content, expected_content)

    def testUserAuthenticatedWhenMakingChanges(self):
        quoted_url = quote_plus(self.user_info['id'])
        auth_headers = build_auth_headers(self.user_info['id'], self.user_info['password'])
        response = self.app.put('/user/{}'.format(quoted_url),
                                headers=auth_headers,
                                data=json.dumps(self.user_info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)


