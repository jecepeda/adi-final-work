import unittest
from urllib import quote_plus
from base64 import b64encode
import json

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from app import app
from tests.utils import BaseTestClass, build_auth_headers


class TestPaperBaseClass(BaseTestClass):

    def setUp(self):
        super(TestPaperBaseClass, self).setUp()
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
        self.organism['id'] = self.organism_id
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


class TestBasePaperEndpoint(TestPaperBaseClass):

    def setUp(self):
        super(TestBasePaperEndpoint, self).setUp()
        self.fake_paper_congress = {'title': 'The Lord of the Foos',
                                    'type': 'congress',
                                    'author': self.fake_author['id']}
        self.fake_paper_journal = {'title': 'The Lord of the Foos 2',
                                   'type': 'journal',
                                   'author': self.fake_author['id']}

    def testPaperPOSTRequestCorrectlyJournal(self):
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_congress),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue('created' in result)

    def testPaperPOSTRequestCorrectlyCongress(self):
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_journal),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue('created' in result)

    def testPaperPOSTRequestFalseNotExistentAuthor(self):
        self.fake_paper_congress['author'] = 'fake'
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_congress),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testPaperPOSTRequestNotEnoughInformation(self):
        del self.fake_paper_congress['author']
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_congress),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def testPaperGETRequestCorrectly(self):
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_congress),
                                 content_type='application/json')
        result = json.loads(response.data)
        self.fake_paper_congress['id'] = result['created']
        response = self.app.get('/papers')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        # Since we don't know exactly the date when the element was inserted,
        # we check if exists, and then remove it to know that the rest of the
        # elements are ok
        self.assertTrue('updated' in result[0])
        del result[0]['updated']
        self.assertEqual(result, [self.fake_paper_congress])


class TestSpecificPaperEndpoint(TestPaperBaseClass):

    def setUp(self):
        super(TestSpecificPaperEndpoint, self).setUp()
        self.fake_paper = {'title': 'The Lord of the Foos',
                           'type': 'congress',
                           'author': self.fake_author['id']}
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper),
                                 content_type='application/json')
        result = json.loads(response.data)
        self.fake_paper['id'] = result['created']

    def testPaperGETRequestCorrectly(self):
        response = self.app.get('/papers/{}'.format(self.fake_paper['id']))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        # check if there is a date in the response
        self.assertTrue('updated' in result)
        del result['updated']
        self.assertEqual(result, self.fake_paper)

    def testPaperDELETERequestCorrectly(self):
        response = self.app.delete('/papers/{}'.format(self.fake_paper['id']),
                                   headers=self.headers)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        expected_result = {'removed': self.fake_paper['id']}
        self.assertEqual(result, expected_result)

    def testPaperDELETERequestWrongUser(self):
        fake_auth = build_auth_headers('fake', 'user')
        response = self.app.delete(
            '/papers/{}'.format(self.fake_paper['id']), headers=fake_auth)
        self.assertEqual(response.status_code, 401)


class TestPaperTypeEndpoint(TestPaperBaseClass):

    def setUp(self):
        super(TestPaperTypeEndpoint, self).setUp()
        self.fake_paper_congress = {'title': 'The Lord of the Foos',
                                    'type': 'congress',
                                    'author': self.fake_author['id']}
        self.fake_paper_journal = {'title': 'The Lord of the Foos 2',
                                   'type': 'journal',
                                   'author': self.fake_author['id']}
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_congress),
                                 content_type='application/json')
        result = json.loads(response.data)
        self.fake_paper_congress['id'] = result['created']
        response = self.app.post('/papers',
                                 headers=self.headers,
                                 data=json.dumps(self.fake_paper_journal),
                                 content_type='application/json')
        result = json.loads(response.data)
        self.fake_paper_journal['id'] = result['created']

    def testObtainPapersByCongressCorrectly(self):
        response = self.app.get('/papers/type/congress')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        del result[0]['updated']
        self.assertEqual(result, [self.fake_paper_congress])

    def testObtainPapersByJournalCorrectly(self):
        response = self.app.get('/papers/type/journal')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        del result[0]['updated']
        self.assertEqual(result, [self.fake_paper_journal])

    def testObtainPapersInvalid(self):
        response = self.app.get('/papers/type/foo')
        self.assertEqual(response.status_code, 400)

