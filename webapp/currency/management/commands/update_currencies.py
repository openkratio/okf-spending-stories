#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : OKF - Spending Stories
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU General Public License
# -----------------------------------------------------------------------------
# Creation : 17-Dec-2013
# Last mod : 17-Dec-2013
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

from django.core.management.base import BaseCommand
from webapp.currency.models import Currency
import requests
import os
from django.conf import settings
from django.core import management
from optparse import make_option

os.environ['PYTHONPATH'] = ROOT_PATH = settings.ROOT_PATH
OER_API_BASE_URL = "http://openexchangerates.org/api/latest.json?app_id=%s"
FIXTURES_PATH    = ROOT_PATH + '/webapp/currency/fixtures/initial_data.json'

class Command(BaseCommand):
	args = 'api_key'
	help = 'Update the currencies rate change'
	option_list = BaseCommand.option_list + (
        make_option('--update_fixtures',
            action  = 'store_true',
            dest    = 'update_fixtures',
            default = False,
            help    = 'Update the fixture file (%s)' % (FIXTURES_PATH)),
        )

	def handle(self, *args, **options):
		assert len(args) == 1
		rates = requests.get(OER_API_BASE_URL % args[0]).json()['rates']
		counter = 0
		for currency in Currency.objects.all():
			new_rate = rates[currency.iso_code]
			if new_rate != currency.rate:
				currency.rate = new_rate
				currency.save()
				counter += 1
		self.stdout.write('%s currencies updated' % (counter))
		# save in fixtures
		if options.get("update_fixtures", False):
			with open(FIXTURES_PATH, 'w') as f:
				print 'file %s saved' % (FIXTURES_PATH)
				management.call_command('dumpdata', 'currency', indent=4, stdout=f)

# EOF
