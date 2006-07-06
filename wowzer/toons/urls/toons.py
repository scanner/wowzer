from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.apps.toons.views',
    (r'^$', 'toons.index'),
    (r'^detail/(?P<toon_id>\d+)/$', 'toons.detail'),
    # Example:
    # (r'^wowzer/', include('wowzer.apps.foo.urls.foo')),
)
