# File: $Id$
#
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.apps.items.views',
    (r'^$', 'items.index'),
    (r'^search/$', 'items.search'),
    (r'^detail/(?P<item_id>\d+)/$', 'items.detail'),
    # Eventually we will have a way of submitting lootlink data to update our
    # items with a lot more detail.
    #
    # (r'^submit/', 'items.submit'),
)
