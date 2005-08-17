from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.apps.madhouse.views',
    (r'^$', 'madhouse.index'),
    (r'^detail/(?P<auction_id>\d+)/$', 'auction.detail'),
    #(r'^submit/')
    # Example:
    # (r'^wowzer/', include('wowzer.apps.foo.urls.foo')),
)
