from django.conf.urls.defaults import *
from wowzer.toons.models import *
info_dict = {
    'queryset'    : Toon.objects.all(),
}

urlpatterns = patterns(
    '',  # The module name prefix.
    #
    # Generic list & detail
    #
    (r'^toon/$',
     'django.views.generic.list_detail.object_list', dict(info_dict, paginate_by=40)),
    (r'^toon/(?P<object_id>\d+)/$', 'wowzer.toons.views.detail'),
)
