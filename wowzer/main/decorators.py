#
# $Id$
#

# wowzer imports
#
from wowzer.decorators import wrapped

# main model imports
#
from wowzer.main.models import Breadcrumb


############################################################################
#
def breadcrumb(name = None):
    """
    This provides a decorator that can easily be used on views to
    create a breadcrumb for the user visiting that view.
    """
    # We need to figure out how the decorator was called.
    # This is: @breadcrumb vs @breadcrumb() and @breadcrumb(short_name = foo)
    #
    if name != None and callable(name):
        # If name is a callable then the coder wrote @breadcrumb
        # and the name is actually the function being wrapped.
        #
        def wrapper(request, *args, **kwargs):
            Breadcrumb.make(request)
            return name(request, *args, **kwargs)
        return wrapper
    else:
        # name is None or not a callable. This means that the coder
        # wrote @breadcrumb() or @breadcrumb(name = name)
        #
        def view_decorator(func):
            def wrapper(request, *args, **kwargs):
                Breadcrumb.make(request, name = name)
                return func(request, *args, **kwargs)
            return wrapper
        return view_decorator

@wrapped
def nbreadcrumb(func, args, kwargs):
    Breadcrumb.make(args[0])
