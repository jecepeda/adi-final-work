import unittest
from urllib import quote_plus
from base64 import b64encode
import json

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from app import app
from tests.utils import BaseTestClass, build_auth_headers

class TestOrganismBaseEndpoint(BaseTestClass):

    def setUp(self):
        super(TestOrganismBaseEndpoint, self).setUp()
        self.user_info = {'id':'foo@bar.com',
                          'nick':'foo',
                          'name':'Foo',
                          'lastName':'bar',
                          'password':'foobar'}
        self.headers = build_auth_headers(self.user_info['id'], self.user_info['password'])
        self.app.post('/user',
                      data=json.dumps(self.user_info),
                      content_type='application/json')

    def testPOSTRequestCorretly(self):
        organism = {'name':'FOO',
                    'address':'Foo Bar Street',
                    'country':'Spain'}
        response = self.app.post('/organisms',
                                 data=json.dumps(organism),
                                 headers=self.headers,
                                 content_type='application/json')
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('created' in result)

    def testGETRequestObtainAll(self):
        for i in range(5):
            organism = {'name':'FOO{}'.format(i),
                        'address':'Foo Bar Street',
                        'country':'Spain'}
            self.app.post('/organisms',
                          data=json.dumps(organism),
                          headers=self.headers,
                          content_type='application/json')
        response = self.app.get('/organisms')
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 5)

    def testPOSTRequestNotEnoughInformation(self):
         organism = {'name':'FOO',
                    'country':'Spain'}
         response = self.app.post('/organisms',
                                  data=json.dumps(organism),
                                  headers=self.headers,
                                  content_type='application/json')
         self.assertTrue(response.status_code, 400)

class TestOrganismSpecificEndpoint(BaseTestClass):

    def setUp(self):
        super(TestOrganismSpecificEndpoint, self).setUp()
        self.user_info = {'id':'foo@bar.com',
                          'nick':'foo',
                          'name':'Foo',
                          'lastName':'bar',
                          'password':'foobar'}
        self.headers = build_auth_headers(self.user_info['id'], self.user_info['password'])

        self.app.post('/user',
                      data=json.dumps(self.user_info),
                      content_type='application/json')

        self.organism = {'name':'FOO',
                    'address':'Foo Bar Street',
                    'country':'Spain'}

        response = self.app.post('/organisms',
                                 data=json.dumps(self.organism),
                                 headers=self.headers,
                                 content_type='application/json')
        data = json.loads(response.data)
        self.organism_id = data['created']

    def testGETTheOrganismCorrectly(self):
        response = self.app.get('/organisms/{}'.format(self.organism_id))
        result = json.loads(response.data)
        self.organism['id'] = self.organism_id
        self.assertEqual(result, self.organism)

    def testGETOrganismNotExistent(self):
        response = self.app.get('/organisms/{}'.format('false_organism'))
        self.assertEqual(response.status_code, 404)

    def testDELETEOrganism(self):
        response = self.app.delete('organisms/{}'.format(self.organism_id),
                                   headers=self.headers)
        result = json.loads(response.data)
        expected_result = {'removed' : self.organism_id}
        self.assertEqual(result, expected_result)

    def testDELETENotExistentOrganism(self):
        response = self.app.delete('organisms/{}'.format('foobar'),
                                   headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def testDELETEWithoutPermissions(self):
        fake_auth = build_auth_headers('fake','fake')
        response = self.app.delete('organisms/{}'.format(self.organism_id), headers=fake_auth)
        self.assertEqual(response.status_code, 401)
