import unittest
from urllib import quote_plus
from base64 import b64encode
import json

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from app import app
from tests.utils import BaseTestClass, build_auth_headers


class UserEndpointTest(BaseTestClass):

    def testUserCreated(self):
        user_info = {'id': 'foo@bar.com', 'nick': 'foo',
                     'name': 'Foo', 'lastName': 'bar', 'password': 'foobar'}
        response = self.app.post(
            '/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.data)
        self.assertEqual(content, {'created': 'foo@bar.com'})

    def testUserNotValidNotEnoughData(self):
        user_info = {'id': 'bar@foo.com', 'nick': 'foobar'}
        response = self.app.post(
            '/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testUserExistsAndFails(self):
        user_info = {'id': 'foo@bar.com', 'nick': 'foo',
                     'name': 'Foo', 'lastName': 'bar', 'password': 'foobar'}
        response = self.app.post(
            '/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = self.app.post(
            '/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testFalseEmail(self):
        user_info = {'id': 'foobar.com', 'nick': 'foo',
                     'name': 'Foo', 'lastName': 'bar', 'password': 'foobar'}
        response = self.app.post(
            '/user', data=json.dumps(user_info), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testGetAll(self):
        user_info = {'id': 'foo@bar.com', 'nick': 'foo',
                     'name': 'Foo', 'lastName': 'bar', 'password': 'foobar'}
        self.app.post('/user', data=json.dumps(user_info),
                      content_type='application/json')
        response = self.app.get('/user')
        content = json.loads(response.data)
        expected_content = [{'id': 'foo@bar.com',
                             'nick': 'foo', 'name': 'Foo', 'lastName': 'bar'}]
        self.assertEqual(content, expected_content)

    def testGetAllEmptyTable(self):
        response = self.app.get('/user')
        content = json.loads(response.data)
        expected_content = []
        self.assertEqual(content, expected_content)


class UserAuthenticationTest(BaseTestClass):

    def setUp(self):
        super(UserAuthenticationTest, self).setUp()
        self.user_info = {'id': 'foo@bar.com', 'nick': 'foo',
                          'name': 'Foo', 'lastName': 'bar', 'password': 'foobar'}
        self.app.post('/user', data=json.dumps(self.user_info),
                      content_type='application/json')

    def testUserAuthenticatedWhenPUTRequest(self):
        quoted_url = quote_plus(self.user_info['id'])
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        response = self.app.put('/user/{}'.format(quoted_url),
                                headers=auth_headers,
                                data=json.dumps(self.user_info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def testUserAuthenticatedButAccessingOtherUser(self):
        # create new user to authenticate with it
        new_user = {'id': 'bar@foo.com', 'nick': 'foo',
                    'name': 'bar', 'lastName': 'Foobar', 'password': 'foobar'}
        self.app.post('/user', data=json.dumps(new_user),
                      content_type='application/json')
        # build url and headers
        auth_headers = build_auth_headers(new_user['id'], new_user['password'])
        quoted_url = quote_plus(self.user_info['id'])
        response = self.app.put('/user/{}'.format(quoted_url),
                                headers=auth_headers,
                                data=json.dumps(self.user_info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 401)


class UserEndpointGETTest(BaseTestClass):

    def setUp(self):
        super(UserEndpointGETTest, self).setUp()
        self.user_info = {'id': 'foo@bar.com', 'nick': 'foo',
                          'name': 'Foo', 'lastName': 'bar', 'password': 'foobar'}
        self.app.post('/user', data=json.dumps(self.user_info),
                      content_type='application/json')

    def testGETRequest(self):
        quoted_url = quote_plus(self.user_info['id'])
        response = self.app.get('/user/{}'.format(quoted_url))
        self.assertEqual(response.status_code, 200)
        expected_content = {'id': 'foo@bar.com',
                            'nick': 'foo', 'name': 'Foo', 'lastName': 'bar'}
        content = json.loads(response.data)
        self.assertEqual(content, expected_content)


class UserEndpointPUTAndPOSTTest(BaseTestClass):

    def setUp(self):
        super(UserEndpointPUTAndPOSTTest, self).setUp()
        self.user_info = {'id': 'foo@bar.com',
                          'nick': 'foo',
                          'name': 'Foo',
                          'lastName': 'bar',
                          'password': 'foobar'}
        self.app.post('/user',
                      data=json.dumps(self.user_info),
                      content_type='application/json')

    def testPUTRequestSuccessfullChangingAllPossibleParameters(self):
        quoted_url = quote_plus(self.user_info['id'])
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        custom_changes = {'nick': 'FOO',
                          'name': 'FOOBAR',
                          'lastName': 'BARFOO'}
        response = self.app.put('/user/{}'.format(quoted_url),
                                headers=auth_headers,
                                data=json.dumps(custom_changes),
                                content_type='application/json')
        expected_result = custom_changes
        expected_result['id'] = 'foo@bar.com'
        result = json.loads(response.data)
        self.assertEqual(result, expected_result)

    def testPUTRequestFailingNotEnoughData(self):
        quoted_url = quote_plus(self.user_info['id'])
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        custom_changes = {'nick': 'FOO', 'lastName': 'BARFOO'}
        response = self.app.put('/user/{}'.format(quoted_url),
                                headers=auth_headers,
                                data=json.dumps(custom_changes),
                                content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def testPUTRequestUserDoesNotExist(self):
        quoted_url = quote_plus('doesnotexist@foo.com')
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        custom_changes = {}
        response = self.app.put('/user/{}'.format(quoted_url),
                                headers=auth_headers,
                                data=json.dumps(custom_changes),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)


class UserEndpointDELETETest(BaseTestClass):

    def setUp(self):
        super(UserEndpointDELETETest, self).setUp()
        self.user_info = {'id': 'foo@bar.com',
                          'nick': 'foo',
                          'name': 'Foo',
                          'lastName': 'bar',
                          'password': 'foobar'}
        self.app.post('/user',
                      data=json.dumps(self.user_info),
                      content_type='application/json')

    def testDELETERequestSuccessful(self):
        quoted_url = quote_plus(self.user_info['id'])
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        response = self.app.delete(
            '/user/{}'.format(quoted_url), headers=auth_headers)
        result = json.loads(response.data)
        expected_result = {'removed': 'foo@bar.com'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, expected_result)

    def testDELETERequestFailRemoveDifferentUser(self):
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        custom_info = self.user_info
        custom_info['id'] = 'foobar@foobar.com'
        quoted_url = quote_plus('foobar@foobar.com')
        self.app.post('/user', data=json.dumps(custom_info),
                      content_type='application/json')
        response = self.app.delete('/user/{}'.format(quoted_url),
                                   headers=auth_headers)
        self.assertEqual(response.status_code, 401)

    def testDELETERequestFailNoUser(self):
        quoted_url = quote_plus('foobar@foobar.com')
        auth_headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])
        response = self.app.delete(
            '/user/{}'.format(quoted_url), headers=auth_headers)
        self.assertEqual(response.status_code, 404)
