#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : OKF - Spending Stories
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU General Public License
# -----------------------------------------------------------------------------
# Creation : 14-Aug-2013
# Last mod : 11-Oct-2013
# -----------------------------------------------------------------------------
# This file is part of Spending Stories.
# 
#     Spending Stories is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     Spending Stories is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with Spending Stories.  If not, see <http://www.gnu.org/licenses/>.

from django.conf                     import settings
from django.test                     import TestCase
from django.test.client              import Client
from webapp.core.models              import Story
from webapp.currency.models          import Currency
from django.contrib.auth.models      import User
from rest_framework.authtoken.models import Token
from operator                        import itemgetter
from pprint                          import pprint as pp
from relevance                       import Relevance
import random
import warnings

class APIStoryTestCase(TestCase):
    """
    Major Test Case about API usage
    """

    fixtures = ['api_dataset.json',]

    def setUp(self):
        # Every test needs a client.
        staff_user             = User.objects.filter(is_staff=True)[0]
        staff_token,   created = Token.objects.get_or_create(user=staff_user)
        regular_user,  created = User.objects.get_or_create(username="pouet", email="pouet@pouet.org")
        regular_token, created = Token.objects.get_or_create(user=regular_user)
        self.regular_client    = Client(HTTP_AUTHORIZATION="Token %s" % regular_token.key)
        self.staff_client      = Client(HTTP_AUTHORIZATION="Token %s" % staff_token.key)
        self.client            = Client()

        self.story             =  {
            'type'       : "discrete",
            'country'    : 'BGR',
            'currency'   : u'EUR',
            'description': None,
            'source'     : 'http://www.okf.org',
            'status'     : 'published',
            'sticky'     : True,
            'themes'     : [],
            'title'      : 'Velit ipsum augue',
            'value'      : 1420000,
            'year'       : 2003
        }

        self.story_fr_args = {
            'type'        : 'discrete', 
            'country'     : 'FRA', 
            'currency'    : Currency.objects.get(iso_code=u'EUR'), 
            'lang'        : 'fr_FR',
            'description' : None,
            'source'      : 'http://www.okf.org',
            'status'      : 'published',
            'sticky'      : True,
            'title'       : 'Velit ipsum augue',
            'value'       : 1420000,
            'year'        : 2003
        }

        self.story_fr, created = Story.objects.get_or_create(**self.story_fr_args)
        self.story_fr.save()

    def test_api_story_list(self):
        response = self.client.get('/api/stories/')
        self.assertEquals(response.status_code, 200, response)
        assert len(response.data) > 0
        for story in response.data:
            assert story['status'] == 'published', "This story souldn't be there: %s" % story

    def test_api_story_retrieve(self):
        story    = Story.objects.public()[0]
        response = self.client.get('/api/stories/%s/' % story.pk)
        self.assertEquals(response.status_code, 200, response)

    def test_api_story_nested_list(self):
        response = self.client.get('/api/stories-nested/')
        self.assertEquals(response.status_code, 200, response)
        assert len(response.data) > 0
        for story in response.data:
            assert story['status'] == 'published', "This story souldn't be there: %s" % story

    def test_api_story_nested_retrieve(self):
        story    = Story.objects.public()[0]
        response = self.client.get('/api/stories-nested/%s/' % story.pk)
        self.assertEquals(response.status_code, 200, response)


    def test_create_story_staff(self):
        response = self.staff_client.post('/api/stories/', self.story)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['status'], 'published')
        self.assertEquals(response.data['sticky'], True)

    def test_create_story_no_auth(self):
        response = self.client.post('/api/stories/', self.story)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['status'], 'pending')
        self.assertEquals(response.data['sticky'], False)

    def test_create_story_user(self):
        response = self.regular_client.post('/api/stories/', self.story)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['status'], 'pending')
        self.assertEquals(response.data['sticky'], False)

    def test_created_story_fields(self):
        """
        Desc: test that every given object field will be set to a new story
        """
        story_args = {  
            'type'        : 'over_one_year', 
            'country'     : 'USA', 
            'currency'    : u'EUR', 
            'lang'        : 'fr_FR',
            'description' : 'My description',
            'source'      : 'http://www.okf.org',
            'title'       : 'Velit ipsum augue',
            'value'       : 33330000,
            'year'        : 2003
        }

        response = self.regular_client.post('/api/stories/', story_args)
        self.assertEquals(response.status_code, 201)
        latest_story = Story.objects.latest('created_at')
        for key in story_args:
            val = story_args[key]
            story_val = getattr(latest_story, key)
            field = Story._meta.get_field_by_name(key)[0]
            # if the current field is a related to another model story_val 
            # must be the related model primary key
            if hasattr(field, 'related'):
                story_val = story_val.pk 

            self.assertEquals(story_val, val)


    def test_filter_by_lang_en(self):
        lang = 'en_GB'
        response = self.client.get('/api/stories/?lang=%s' % lang) 
        for story in response.data:
            self.assertEquals(story['lang'], lang)

    def test_filter_by_lang_fr(self):
        lang = 'fr_FR'
        response = self.client.get('/api/stories/?lang=%s' % lang) 
        for story in response.data:
            self.assertEquals(story['lang'], lang)
        find_fr = lambda x: x['id'] == self.story_fr.pk
        self.assertIsNotNone(filter(find_fr, response.data))

    def test_filter_list(self):
        response = self.client.get('/api/filters/')
        data = response.data
        lang = data.get('lang')
        self.assertIsNotNone(lang)
        self.assertGreater(len(lang), 0)

    def test_language_list(self):
        response = self.client.get('/api/languages/')
        self.assertIsNotNone(response.data)
        self.assertEquals(len(response.data), len(settings.LANGUAGES))
        for lang in settings.LANGUAGES:
            find_lang = lambda x: x['code'] == lang[0]
            response_lang = filter(find_lang, response.data)[0]
            self.assertIsNotNone(response_lang)
            self.assertTrue(response_lang['name'] == lang[1])




    def test_api_relevances(self):
        TOLERENCE = 97
        count     = {}
        for x in range(100):
            relevance_for = random.randint(1,200) * int("1" + "0" * random.randint(1,15))
            if relevance_for in count:
                continue
            count[relevance_for] = 0
            response = self.client.get("/api/stories-nested/?relevance_for=%s" % (relevance_for))
            self.assertEquals(response.status_code, 200)
            assert len(response.data) > 0
            for story in response.data:
                self.assertIsNotNone(story['relevance_score'])
                if story['relevance_score'] > 8:
                    count[relevance_for] += 1
                    if story['type'] is 'over_one_year':
                        accepted_types = (
                            Relevance.RELEVANCE_TYPE_MULTIPLE, 
                            Relevance.RELEVANCE_TYPE_EQUIVALENCE,
                            Relevance.RELEVANCE_TYPE_HALF,
                        )
                        self.asserTrue(story['relevance_type'] in accepted_types)
                    if story['relevance_type'] in (Relevance.RELEVANCE_TYPE_MULTIPLE, Relevance.RELEVANCE_TYPE_HALF) :
                        reverse_computing = float(story['relevance_value']) * story['current_value_usd']
                        accuracy = min(reverse_computing, relevance_for) / max(reverse_computing, relevance_for) * 100
                        debug = "\n"
                        debug += "\n{0:20}: {1}"          .format('user query'       , relevance_for)
                        debug += "\n{0:20}: {1} (id: {2})".format('story value'      , story['current_value_usd'], story['id'])
                        debug += "\n{0:20}: {1}"          .format('relevance_score'  , story['relevance_score'])
                        debug += "\n{0:20}: {1}"          .format('relevance_type'   , story['relevance_type'])
                        debug += "\n{0:20}: {1}"          .format('relevance_value'  , story['relevance_value'])
                        debug += "\n{0:20}: {1}"          .format("reverse_computing", reverse_computing)
                        debug += "\n{0:20}: {1}%"         .format("accuracy"         , accuracy)
                        debug += "\n--------------------------------------"
                        if accuracy < TOLERENCE:
                            warnings.warn("accurency under %s%%: %s" % (TOLERENCE, debug))
                if story['relevance_type'] in (Relevance.RELEVANCE_TYPE_WEEK, Relevance.RELEVANCE_TYPE_MONTH, Relevance.RELEVANCE_TYPE_DAY) :
                    if story['relevance_type'] == Relevance.RELEVANCE_TYPE_WEEK:
                        reverse_computing = float(story['relevance_value']) * story['current_value_usd']/52
                    elif story['relevance_type'] == Relevance.RELEVANCE_TYPE_MONTH:
                        reverse_computing = float(story['relevance_value']) * story['current_value_usd']/12
                    elif story['relevance_type'] == Relevance.RELEVANCE_TYPE_DAY:
                        reverse_computing = float(story['relevance_value']) * story['current_value_usd']/365.25
                    accuracy = min(reverse_computing, relevance_for) / max(reverse_computing, relevance_for) * 100
                    debug = "\n"
                    debug += "\n{0:20}: {1}"          .format('user query'       , relevance_for)
                    debug += "\n{0:20}: {1} (id: {2})".format('story value'      , story['current_value_usd'], story['id'])
                    debug += "\n{0:20}: {1}"          .format('relevance_score'  , story['relevance_score'])
                    debug += "\n{0:20}: {1}"          .format('relevance_type'   , story['relevance_type'])
                    debug += "\n{0:20}: {1}"          .format('relevance_value'  , story['relevance_value'])
                    debug += "\n{0:20}: {1}"          .format("reverse_computing", reverse_computing)
                    debug += "\n{0:20}: {1}%"         .format("accuracy"         , accuracy)
                    debug += "\n--------------------------------------"
                    if accuracy < TOLERENCE:
                        warnings.warn("accurency under %s%%: %s" % (TOLERENCE, debug))
        count = sorted(count.iteritems(), key=itemgetter(1), reverse=True)
        # pp(count[:5])

# EOF
