# File: $Id$
#
from django.conf.urls.defaults import *
from wowzer.items.models import *

info_dict = {
    'queryset'    : WDBItem.objects.all(),
}

urlpatterns = patterns(
    'django.views.generic',  # The module name prefix.
    #
    # Generic list & detail
    #
    (r'^wdbitem/$',
     'list_detail.object_list', dict(info_dict, paginate_by=30)),
    (r'^wdbitem/(?P<object_id>\d+)/$',
     'list_detail.object_detail', info_dict),

##     'wowzer.apps.items.views',
##     (r'^$', 'items.index'),
##     (r'^search/$', 'items.search'),
##     (r'^detail/(?P<item_id>\d+)/$', 'items.detail'),
##     # Eventually we will have a way of submitting lootlink data to update our
##     # items with a lot more detail.
##     #
##     # (r'^submit/', 'items.submit'),
)
