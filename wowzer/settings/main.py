# Django settings for wowzer project.

DEBUG = True

ADMINS = (
    ('Scanner', 'scanner@apricot.com'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

LANGUAGE_CODE = 'en-us'

DATABASE_ENGINE = 'sqlite3' # 'postgresql', 'mysql', or 'sqlite3'.
DATABASE_NAME = '/Users/scanner/src/wowzer/data/wowzer.db'       # Or path to database file if using sqlite3.
#DATABASE_NAME = 'wowzer'       # Or path to database file if using sqlite3.
DATABASE_USER = 'wowzer'       # Not used with sqlite3.
DATABASE_PASSWORD = 'ohikoloo' # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/usr/local/www/wowzer/media/media/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = 'http://wow.apricot.com/media'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '59%=o6!mzu2jl^ig)55-lt3xfwwiyc6(_zcg=0!1$ty$@q-#06'

ROOT_URLCONF = 'wowzer.settings.urls.main'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    "/usr/local/www/wowzer/templates",
    "/home/scanner/src/wowzer/templates",
    "/Users/scanner/src/wowzer/templates",
)

INSTALLED_APPS = (
    'wowzer.apps.toons',
    'wowzer.apps.items',
    'wowzer.apps.madhouse',
)
