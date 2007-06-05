#
# File: $Id$
#
#
# Django settings for wowzer project.
#

# The settings are partially specified in this file and partially
# sucked in from a config file. The things that are different between
# installations are expected to be captured in the config file which is
# not under source control.
#
import os
from ConfigParser import RawConfigParser

config = RawConfigParser()

if 'DJANGO_CONFIG_FILE' in os.environ:
    config.read([os.environ['DJANGO_CONFIG_FILE']])
else:
    if os.path.exists("etc/test-config.ini"):
        config.read(["etc/test-config.ini"])
    elif os.path.exists("../etc/test-config.ini"):
        config.read(["../etc/test-config.ini"])
    else:
        raise "Unable to load a test configuration"

# We should do some checks to make sure the config file we read
# has the necessary sections and items in those sections.
#
DEBUG = config.getboolean('debug','DEBUG')
TEMPLATE_DEBUG = config.getboolean('debug','TEMPLATE_DEBUG')

ADMINS = tuple(config.items('error mail'))
MANAGERS = tuple(config.items('404 mail'))

# Make this unique, and don't share it with anybody.
#
SECRET_KEY = config.get('secrets','SECRET_KEY')

LANGUAGE_CODE = config.get('locale', 'LANGUAGE_CODE')
TIME_ZONE = config.get('locale', 'TIME_ZONE')

DATABASE_USER = config.get('database', 'DATABASE_USER')
DATABASE_PASSWORD = config.get('database', 'DATABASE_PASSWORD')
DATABASE_HOST = config.get('database', 'DATABASE_HOST')
DATABASE_PORT = config.get('database', 'DATABASE_PORT')
DATABASE_ENGINE = config.get('database', 'DATABASE_ENGINE')
DATABASE_NAME = config.get('database', 'DATABASE_NAME')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = config.get('directories', 'ADMIN_MEDIA_PREFIX')
MEDIA_ROOT = config.get('directories', 'MEDIA_ROOT')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = config.get('directories', 'MEDIA_URL')

TEMPLATE_DIRS = []
TEMPLATE_DIRS.append(config.get('directories', 'TEMPLATES'))

# For the 'registration' app
#
ACCOUNT_ACTIVATION_DAYS = config.get('registration','ACCOUNT_ACTIVATION_DAYS')
EMAIL_HOST = config.get('registration','EMAIL_HOST')
EMAIL_PORT = config.get('registration','EMAIL_PORT')
EMAIL_HOST_USER = config.get('registration','EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('registration','EMAIL_HOST_PASSWORD')

###########################################################################
###########################################################################
#
# That is it for configurable items.
#
SITE_ID = 1

# Our "user profile" extension object.
#
AUTH_PROFILE_MODULE = 'main.UserProfile'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    'django.core.context_processors.media',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'wowzer.text.middleware.Markup.Markup',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'wowzer.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'tagging',
    'typogrify',
    'wowzer.registration',
    'wowzer.main',
    'wowzer.toons',
    'wowzer.items',
    'wowzer.raidtracker',
    'wowzer.asforums',
    'wowzer.main',
    'wowzer.users',
#    'wowzer.madhouse',
#    'wowzer.gatherbox',
#    'wowzer.realm',
)
