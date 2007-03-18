"""
basic quoting/editing/rendering of text
"""
__revision__ = "$Rev: 227 $" 
__date__ = "$Date$" 



from django.conf.urls.defaults import patterns
urlpatterns = patterns('zilbo.common.text.views',
    (r'^$', 'preview'),
    (r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<hash>.+)/quote/$', 'quote'),
    (r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<hash>.+)/get/$', 'get'),
)
