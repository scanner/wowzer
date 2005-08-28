# File: $Id$
#
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.apps.madhouse.views',
    (r'^$', 'madhouse.index'),
    (r'^detail/(?P<auction_id>\d+)/$', 'auction.detail'),
    (r'^history/(?P<item_id>\d+)/(?P<realm_id>\d+)/(?P<faction_id>\d+)/$',
     'history.for_realm_for_faction'),
    (r'^submit/', 'submit.submit'),
    # Example:
    # (r'^wowzer/', include('wowzer.apps.foo.urls.foo')),
)
