import unittest
from urllib import quote_plus
from base64 import b64encode
import json

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from app import app
from tests.utils import BaseTestClass, build_auth_headers


class TestAuthorBaseEndpoint(BaseTestClass):

    def setUp(self):
        super(TestAuthorBaseEndpoint, self).setUp()
        self.user_info = {
            'id': 'foo@bar.com',
            'nick': 'foo',
            'name': 'Foo',
            'lastName': 'bar',
            'password': 'foobar'
        }
        self.organism = {
            'name': 'FOO',
            'address': 'Foo Bar Street',
            'country': 'Spain'
        }
        self.headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])

        self.app.post('/user',
                      data=json.dumps(self.user_info),
                      content_type='application/json')

        response = self.app.post('/organisms',
                                 data=json.dumps(self.organism),
                                 headers=self.headers,
                                 content_type='application/json')
        data = json.loads(response.data)
        self.organism_id = data['created']
        self.fake_author = {
            'id': 'foobar@foo.com',
            'name': 'Foo',
            'lastName': 'Bar',
            'organism': self.organism_id
        }

    def testAuthorInsertedCorretly(self):
        response = self.app.post('/author',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_author),
                                 content_type='application/json')
        result = json.loads(response.data)
        expected_result = {'created': self.fake_author['id']}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, expected_result)

    def testAuthorNotExistingOrganism(self):
        del self.fake_author['organism']
        response = self.app.post('/author',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_author),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testAuthorFalseOrganism(self):
        self.fake_author['organism'] = 'fake'
        response = self.app.post('/author',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_author),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testAuthorIncompleteInformation(self):
        del self.fake_author['name']
        del self.fake_author['lastName']
        response = self.app.post('/author',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_author),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testAuthorFalseEmail(self):
        self.fake_author['id'] = 'incorrect email'
        response = self.app.post('/author',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_author),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)


class TestAuthorSpecificEndpoint(BaseTestClass):

    def setUp(self):
        super(TestAuthorSpecificEndpoint, self).setUp()
        self.user_info = {
            'id': 'foo@bar.com',
            'nick': 'foo',
            'name': 'Foo',
            'lastName': 'bar',
            'password': 'foobar'
        }
        self.organism = {
            'name': 'FOO',
            'address': 'Foo Bar Street',
            'country': 'Spain'
        }
        self.headers = build_auth_headers(
            self.user_info['id'], self.user_info['password'])

        self.app.post('/user',
                      data=json.dumps(self.user_info),
                      content_type='application/json')

        response = self.app.post('/organisms',
                                 data=json.dumps(self.organism),
                                 headers=self.headers,
                                 content_type='application/json')
        data = json.loads(response.data)
        self.organism_id = data['created']
        self.fake_author = {
            'id': 'foobar@foo.com',
            'name': 'Foo',
            'lastName': 'Bar',
            'organism': self.organism_id
        }
        self.app.post('/author',
                      headers=self.headers,
                      data=json.dumps(self.fake_author),
                      content_type='application/json')

    def testAuthorGETRequestCorrectly(self):
        quoted_url = quote_plus(self.fake_author['id'])
        response = self.app.get('/author/{}'.format(quoted_url))
        result = json.loads(response.data)
        expected_result = dict(self.fake_author)
        expected_result['organism'] = self.organism
        expected_result['organism']['id'] = self.organism_id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, expected_result)

    def testAuthorGETRequestFalseAuthor(self):
        response = self.app.get('author/fakeuser')
        self.assertEqual(response.status_code, 404)

    def testAuthorDELETERequestCorrectly(self):
        quoted_url = quote_plus(self.fake_author['id'])
        response = self.app.delete(
            '/author/{}'.format(quoted_url), headers=self.headers)
        result = json.loads(response.data)
        expected_result = {'removed': self.fake_author['id']}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result, expected_result)

    def testAuthorDELETERequestNotExistentUser(self):
        response = self.app.delete(
            '/author/{}'.format('wrong!'), headers=self.headers)
        self.assertEqual(response.status_code, 404)
