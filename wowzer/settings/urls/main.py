from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^madhouse/', include('wowzer.apps.madhouse.urls.madhouse')),
    (r'^toons/', include('wowzer.apps.toons.urls.toons')),
    # Example:
    # (r'^wowzer/', include('wowzer.apps.foo.urls.foo')),
    )
