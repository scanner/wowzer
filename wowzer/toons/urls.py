from django.conf.urls.defaults import *
from wowzer.toons.models import *
info_dict = {
    'queryset'    : Toon.objects.all(),
}

urlpatterns = patterns(
    'django.views.generic',  # The module name prefix.
    #
    # Generic list & detail
    #
    (r'^toon/$',
     'list_detail.object_list', dict(info_dict, paginate_by=30)),
    (r'^toon/(?P<object_id>\d+)/$',
     'list_detail.object_detail', info_dict),
)
