# File: $Id$
#
from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^madhouse/', include('wowzer.apps.madhouse.urls.madhouse')),
    (r'^toons/', include('wowzer.apps.toons.urls.toons')),
    (r'^items/', include('wowzer.apps.items.urls.items')),
    )
