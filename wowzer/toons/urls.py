from django.conf.urls.defaults import *
from wowzer.toons.models import *
info_dict = {
    'queryset'    : Toon.objects.all(),
}

urlpatterns = patterns(
    'wowzer.toons.views',

    (r'^$', 'index'),

    (r'^toons/$', 'toon_list'),
    (r'^toons/(?P<toon_id>\d+)/$', 'toon_detail'),
)
