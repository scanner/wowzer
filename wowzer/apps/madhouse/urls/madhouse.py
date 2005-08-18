from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.apps.madhouse.views',
    (r'^$', 'madhouse.index'),
    (r'^detail/(?P<auction_id>\d+)/$', 'auction.detail'),
    (r'^submit/', 'submit.submit'),
    (r'^poke_ud_queue/', 'submit.poke_ud_queue'),
    # Example:
    # (r'^wowzer/', include('wowzer.apps.foo.urls.foo')),
)
