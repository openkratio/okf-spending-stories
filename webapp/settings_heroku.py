#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : OKF - Spending Stories
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU General Public License
# -----------------------------------------------------------------------------
# Creation : 07-Aug-2013
# Last mod : 07-Aug-2013
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

"""
Heroku environment variables needed:

	AWS_ACCESS_KEY_ID:       <AWS_KEY>
	AWS_SECRET_ACCESS_KEY:   <AWS_PWD>
	AWS_STORAGE_BUCKET_NAME: <BUCKET_NAME>
	BUILDPACK_URL:           git://github.com/vied12/heroku-buildpack-django.git
	HEROKU:                  True
	PATH:                    bin:node_modules/.bin:/app/bin:/usr/local/bin:/usr/bin:/bin
	PYTHONPATH:              webapp/:libs/
	DATABASE_URL             postgres://<POSTGRES_URL>

"""
HEROKU = True

from settings import *

DEBUG = True

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config()
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

INSTALLED_APPS         += ('storages',)
DEFAULT_FILE_STORAGE    = 'storages.backends.s3boto.S3BotoStorage'
# Static storage
STATICFILES_STORAGE     = DEFAULT_FILE_STORAGE
AWS_ACCESS_KEY_ID       = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY   = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_QUERYSTRING_AUTH    = False
AWS_S3_FILE_OVERWRITE   = True
STATIC_URL              = 'https://%s.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

COMPRESS_URL            = STATIC_URL
COMPRESS_STORAGE        = STATICFILES_STORAGE

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
# Activate CSS minifier in
COMPRESS_CSS_FILTERS = (
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
)

# TinyMCE configuration
TINYMCE_JS_URL = os.path.join(STATIC_URL, "tiny_mce", "tiny_mce.js")
