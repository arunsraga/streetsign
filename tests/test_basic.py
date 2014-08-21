'''
    First file on the noble epic tast of unit testing.
'''

import sys
import os
import tempfile
import unittest
import html5lib
import json

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server
import streetsign_server.models as models
from peewee import SqliteDatabase, create_model_tables

# pylint: disable=too-many-public-methods

class StreetSignTestCase(unittest.TestCase):
    ''' Base Class, initialises and tears down a streetsign_server context. '''

    def setUp(self):
        ''' initialise temporary new database. '''

        self.db_fd, streetsign_server.app.config['DATABASE_FILE'] = \
            tempfile.mkstemp()

        streetsign_server.app.config['TESTING'] = True

        models.DB = SqliteDatabase(None, threadlocals=True, autocommit=False)
        models.DB.init(streetsign_server.app.config['DATABASE_FILE'])

        model_list = []

        for modelname in models.__all__:
            model = getattr(models, modelname)
            try:
                model._meta.database = models.DB
                model_list.append(model)
            except AttributeError:
                pass

        create_model_tables(model_list)
        models.DB.set_autocommit(False)

        self.client = streetsign_server.app.test_client()

    def tearDown(self):
        ''' delete temporary database '''

        models.DB.close()
        os.close(self.db_fd)
        os.unlink(streetsign_server.app.config['DATABASE_FILE'])

class TestSetup(StreetSignTestCase):
    ''' First basic sanity checks '''

    def test_empty_db(self):
        ''' test that with the new database, there are no posts. '''

        request = self.client.get('/')
        assert 'Dashboard' in request.data # it is the front page
        assert 'Login' in request.data # not logged in

        request = self.client.get('/posts/')
        assert '<span class="post_count">No Posts at all!' in request.data

class TestHTML(StreetSignTestCase):
    ''' test for valid HTML '''

    def validate(self, url):
        ''' test that a URL is actually HTML5 compliant '''

        request = self.client.get(url)
        parser = html5lib.HTMLParser(strict=True)
        doc = parser.parse(request.data)

    def test_non_logged_in_pages(self):
        ''' test HTML validity of all non-logged-in pages '''

        self.validate('/')
        self.validate('/posts/')

class TestDB(StreetSignTestCase):
    ''' test basic database interactions '''
    def test_empty(self):
        self.assertEqual(models.Post.select().count(), 0)
        self.assertEqual(models.Feed.select().count(), 0)

    def test_create_basics(self):
        f = models.Feed.create(name='first feed')
        self.assertEqual(models.Feed.select().count(), 1)

        u = models.User.create(name='test user', loginname='test', emailaddress='test@example.com',
            passwordhash='')
        u.set_password('test pass')

        p = models.Post.create(feed=f, type='html', content='{"content":"text"}', author=u)

        self.assertEqual(models.Post.select().count(), 1)

        self.assertEqual(f.posts.count(), 1)

        # check that our views are displaying it correctly...

        self.assertEqual(json.loads(self.client.get('/screens/posts_from_feeds/%5B' + str(f.id) + '%5D').data),
                         {'posts':[]})

        p.published = True



if __name__ == '__main__':
    unittest.main()
