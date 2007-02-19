#
# Small script to initialize asforums with some data
#
from django.contrib.auth.models import User
from wowzer.asforums.models import Forum

try:
    u = User.objects.get(username='scanner')
except User.DoesNotExist:
    u = User(username="scanner", is_staff = True, is_active = True)
    u.save()

for name in ('test1', 'test2', 'test3', 'test4'):
    try:
        f = Forum.objects.get(name=name)
    except Forum.DoesNotExist:
        f = Forum(name=name, slug = name, creator = u)
        f.save()
        print "Created forum '%s'" % str(f)


