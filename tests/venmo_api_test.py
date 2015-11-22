"""
Unit tests for Venmo API
"""

import unittest
from src.venmo_api import Workflow, Venmo, wf
import src.httpretty as httpretty
from src.config import TOKEN_URL
from tests.sample_data import sample_friends, sample_user
from src.config import FRIENDS_URL, LOGIN, LOGOUT, CLEAR_CACHE, INVALID
import json
import os
import sys

CachedData = {}
Passwords = {}
StoredData = {}

sample_access_token = 'test'


class TestVenmoAPI(unittest.TestCase):

    @httpretty.activate
    def test_get_friends(self):
        httpretty.register_uri(httpretty.GET, FRIENDS_URL % (sample_user['username'], sample_access_token),
            body=json.dumps({"data" : sample_friends }),
            content_type='application/json')
        friends = Venmo.get_friends()
        self.assertTrue(isinstance(friends, list))

    def test_show_friends(self):
        pass

    def test_show_filtered_friends(self):
        pass

    @httpretty.activate
    def test_find_friends(self):
        httpretty.register_uri(httpretty.GET, FRIENDS_URL % (sample_user['username'], sample_access_token),
            body=json.dumps({"data" : sample_friends }),
            content_type='application/json')

        self.assertEquals(len(Venmo.findFriends('And')), 2)
        self.assertEquals(len(Venmo.findFriends('Andrew Staub')), 1)
        self.assertEquals(len(Venmo.findFriends('Nobody')), 0)

    def test_show_options(self):
        wf._items = []

        Venmo.show_options('')
        self.assertEquals(len(wf._items), 3)
        self.assertEquals(wf._items[0].title, LOGIN['title'])
        self.assertEquals(wf._items[1].title, LOGOUT['title'])
        self.assertEquals(wf._items[2].title, CLEAR_CACHE['title'])
        wf._items = []

        Venmo.show_options('login')
        self.assertEquals(wf._items[0].title, LOGIN['title'])
        self.assertEquals(wf._items[0].arg, LOGIN['arg'])
        self.assertEquals(wf._items[0].autocomplete, LOGIN['autocomplete'])
        wf._items = []

        Venmo.show_options('logout')
        self.assertEquals(wf._items[0].title, LOGOUT['title'])
        self.assertEquals(wf._items[0].arg, LOGOUT['arg'])
        self.assertEquals(wf._items[0].autocomplete, LOGOUT['autocomplete'])
        wf._items = []

        Venmo.show_options('clear cache')
        self.assertEquals(wf._items[0].title, CLEAR_CACHE['title'])
        self.assertEquals(wf._items[0].arg, CLEAR_CACHE['arg'])
        self.assertEquals(wf._items[0].autocomplete, CLEAR_CACHE['autocomplete'])
        wf._items = []


        Venmo.show_options('not result')
        self.assertEquals(wf._items[0].title, INVALID['title'])
        wf._items = []

    @httpretty.activate
    def test_exchange_token(self):
        httpretty.register_uri(httpretty.POST, TOKEN_URL,
            body='{"access_token" : "string", "user" : {"username": "test"}}',
            content_type='application/json')

        self.assertIsInstance(Venmo.exchange_token('code'), dict)

    def test_generate_payload(self):

        # must be first friend
        friend = sample_friends[0]

        self.assertEqual(Venmo.generate_payload([''], friend),{
            'user_id' : friend['id'],
            'amount' : '[amount]',
            'note' : '[note]',
            'display_name' : friend['display_name']
            })

        self.assertEqual(Venmo.generate_payload(['1'], friend),{
            'user_id' : friend['id'],
            'amount' : '1.00',
            'note' : '[note]',
            'display_name' : friend['display_name']
            })

        self.assertEqual(Venmo.generate_payload(['-'], friend),{
            'user_id' : friend['id'],
            'amount' : '[amount]',
            'note' : '[note]',
            'display_name' : friend['display_name']
            })

        self.assertEqual(Venmo.generate_payload(['1',''], friend),{
            'user_id' : friend['id'],
            'amount' : '1.00',
            'note' : '[note]',
            'display_name' : friend['display_name']
            })

        self.assertEqual(Venmo.generate_payload(['1','t'], friend),{
            'user_id' : friend['id'],
            'amount' : '1.00',
            'note' : 't',
            'display_name' : friend['display_name']
            })

        self.assertEqual(Venmo.generate_payload(['1','test test'], friend),{
            'user_id' : friend['id'],
            'amount' : '1.00',
            'note' : 'test test',
            'display_name' : friend['display_name']
            })

    def test_format_title(self):
        # must be first friend
        friend = sample_friends[0]

        payload = {
            'user_id' : friend['id'],
            'amount' : '[amount]',
            'note' : '[note]',
            }
        self.assertEqual(Venmo.format_title(payload, friend), '%s [amount] [note]' % friend['display_name'])

        payload = {
            'user_id' : friend['id'],
            'amount' : '1.00',
            'note' : '[note]',
            }
        self.assertEqual(Venmo.format_title(payload, friend), 'pay %s $1.00 [note]' % friend['display_name'])

        payload = {
            'user_id' : friend['id'],
            'amount' : '-1.00',
            'note' : '[note]',
            }
        self.assertEqual(Venmo.format_title(payload, friend), 'charge %s $1.00 [note]' % friend['display_name'])

        payload = {
            'user_id' : friend['id'],
            'amount' : '-1.00',
            'note' : 't',
            }
        self.assertEqual(Venmo.format_title(payload, friend), 'charge %s $1.00 for t' % friend['display_name'])

    @httpretty.activate
    def test_show_formatting(self):
        httpretty.register_uri(httpretty.GET, FRIENDS_URL % (sample_user['username'], sample_access_token),
            body=json.dumps({"data" : sample_friends }),
            content_type='application/json')

        wf._items = []

        Venmo.show_formatting('Andrew Kortina')
        self.assertEquals(wf._items[0].title, 'Andrew Kortina [amount] [note]')
        wf._items = []

        Venmo.show_formatting('Andrew Kortina ')
        self.assertEquals(wf._items[0].title, 'Andrew Kortina [amount] [note]')
        wf._items = []

        Venmo.show_formatting('Andrew Kortina 1')
        self.assertEquals(wf._items[0].title, 'pay Andrew Kortina $1.00 [note]')
        wf._items = []

        Venmo.show_formatting('Andrew Kortina -')
        self.assertEquals(wf._items[0].title, 'Andrew Kortina [amount] [note]')
        wf._items = []

        Venmo.show_formatting('Andrew Kortina -1')
        self.assertEquals(wf._items[0].title, 'charge Andrew Kortina $1.00 [note]')
        wf._items = []

        Venmo.show_formatting('Andrew Kortina 1 food')
        self.assertEquals(wf._items[0].title, 'pay Andrew Kortina $1.00 for food')
        wf._items = []

        Venmo.show_formatting('Andrew Kortina -11.0 test')
        self.assertEquals(wf._items[0].title, 'charge Andrew Kortina $11.00 for test')
        wf._items = []


    def setUp(self):
        f = open(os.devnull, 'w')
        sys.stdout = f

        CachedData.clear()
        StoredData.clear()
        Passwords.clear()

        logging.disable(logging.CRITICAL)

        # replaces cache
        def cached_data(key, callback, max_age=None):
            CachedData[key] = callback()
            return CachedData.get(key)
        wf.cached_data = cached_data

        def store_data(key, value):
            StoredData[key] = value
        wf.store_data = store_data

        def stored_data(key, max_age=None):
            return StoredData[key]
        wf.stored_data = stored_data

        def save_password(key, value):
            Passwords[key] = value
        wf.save_password = save_password

        def get_password(key):
            return Passwords.get(key)
        wf.get_password = get_password

        def delete_password(key):
            if key in Passwords:
                del Passwords[key]
        wf.delete_password = delete_password

        wf.save_password('venmo_access_token', sample_access_token)
        wf.store_data('venmo_user', sample_user)

if __name__ == '__main__':
    unittest.main()

