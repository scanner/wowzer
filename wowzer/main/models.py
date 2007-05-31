#
# This is where we define the user profile which holds the customization and
# configuration data for various users as an extension of the user module.
#
# $Id$
#

# System imports
#
import pytz

# Django imports
#
from django.db import models

# django model imports
#
from django.contrib.auth.models import User

############################################################################
#
class Style(models.Model):
    """The style model defines several items that let a user pick the look and
    feel of their web experience. All a style is right now, really, is a
    reference to a css style sheet that will be used for the pages that
    this user visits."""
    name = models.CharField(maxlength = 128, unique = True, db_index = True,
                            blank = False)
    slug = models.SlugField(maxlength = 20, unique = True, db_index = True,
                            prepopulate_from = ("name", "creator",
                                                "created_at"))

    creator = models.ForeignKey(User, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    stylesheet = models.CharField(maxlength = 128, blank = False)
    screenshot = models.ImageField(upload_to = "img/styles/%s/screenshot",
                                   height_field = True, width_field = True)

    class Meta:
        row_level_permissions = True
        permissions = (("view", "Can see the style"),)

    #########################################################################
    #
    def __str__(self):
        return "Style %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/main/styles/%d" % self.id


############################################################################
#
class UserProfile(models.Model):
    TZ_CHOICES = tuple([(x,x) for x in pytz.common_timezones])

    # The supported kinds of markup a usr can choose from.  NOTE:
    # Basically we apply the markup when they POST an object that has a
    # field that is markupable (ie: any field named 'content'.
    # The value is the name of the module that contains the functions "to_html"
    # and such that will convert a body of text from markup to html.
    # THe name is appended to "wowzer." so "text.bbcode" refers to the module
    # "wowzer.text.bbcode"
    #
    MARKUP_CHOICES =  (('text.bbcode', 'BBCode'),
                       ('text.Ztextile', 'ZTextile'),
                       ('text.plain', 'Plain'))

    user = models.ForeignKey(User, unique = True, editable = False,
                             null = False)
    homepage = models.URLField(blank = True)
    style = models.ForeignKey(Style, blank = True, null = True)
    markup = models.CharField(maxlength=128, choices = MARKUP_CHOICES,
                              default = "text.bbcode")
    signature = models.TextField(maxlength = 1024, blank = True)
    signature_html = models.TextField(maxlength = 1024, blank = True,
                                      editable = False)

    # If blank defaults to the timezone of django site.
    #
    timezone = models.CharField(maxlength = 128, choices = TZ_CHOICES,
                                default = 'US/Eastern')
    avatar = models.ImageField(upload_to = "img/accounts/%d/avatars",
                               height_field = True, width_field = True,
                               blank = True, null = True)

#############################################################################
#
SHORTNAME_LENGTH = 24
def shorten_name(name):
    """
    A helper function to conditionally shorten a name to the
    acceptable length for a short name.
    """
    if len(name) > SHORTNAME_LENGTH:
        # If the short name is > 24 then take 10 characters at the
        # begining and 10 characters at the end and splice it
        # together with "..."
        #
        return name[:10] + "..." + name[-10:]
    return name

#############################################################################
#
class Breadcrumb(models.Model):
    """
    As a user navigates a site the browser can keep track of their
    previous urls. However, that may span sites, and is not something
    that we can easily incorporate in to our UI.

    Perhaps it can be done with javascript looking through a browser's
    history but that would not transport across browsers or
    sessions. It would also traverse sites.

    We want a way for people to know where they have been on THIS site
    recently. With some sort of upper bound on how many url's we will
    keep track of.

    We call these breadcrums and this model will be used to track
    them. The UI will display a certain number of them on every page.

    A user's profile page may display more and let the user set some
    conditions regarding them.

    A regular process will make sure to remove old ones from the database.

    XXX This should be limited by a parameter in the user profile.
    XXX for now we will limit it to 100 entries, of which only 5-10 will
    XXX probably be shown at once.
    """
    created = models.DateTimeField(auto_now_add = True, db_index = True)
    owner = models.ForeignKey(User, db_index = True, editable = False)
    url = models.CharField("URL", maxlength = 1024)
    name = models.CharField("Name", maxlength = 256)
    short_name = models.CharField("Short name", maxlength = SHORTNAME_LENGTH)
    class Meta:
        ordering = ('owner', '-created')

    #########################################################################
    #
    def __str__(self):
        return self.short_name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/main/breadcrumbs/%d/" % self.id

    #########################################################################
    #
    @classmethod
    def make(cls, request, name = None):
        """
        This class method is a convenience function that will create
        a new Breadcrumb from the given request.

        As a short bit of efficiency and to prevent refreshing a url
        from filling up your breadcrumb limit if the most recent
        breadcrum has the same url as the one we are making then we do
        not create one.
        """

        # If the requester is not logged in we do not create a breadcrumb.
        #
        if request.user.is_anonymous():
            return

        # First get the last url breadcrumb we made. If its url is the same as
        # the url in the request we were passed then we do not need to make
        # a new breadcrumb (the user went nowhere.. )
        #
        try:
            last_bc = cls.objects.filter(owner = request.user).\
                      order_by('-created')[0]
            if last_bc.url == request.path:
                # If the url of the last breadcrumb is the same as the url
                # of the request we were passed, then make no new breadcrumb.
                #
                return
        except IndexError:
            # Oh, they have no breadcrumbs on this session yet. This means
            # we are going to make one.
            #
            pass

        # Make a new breadcrumb from the request & shortname.
        #
        if name is None:
            name = request.path
        short_name = shorten_name(name)
        bc = cls(owner = request.user,
                 url = request.path,
                 name = name,
                 short_name = short_name)
        bc.save()

        # Now we see if they have more then 100 bread crumbs in this
        # session. If they do delete the excess.
        #
        sess_bc_list = \
                  cls.objects.filter(owner = request.user).order_by('created')
        num_bc = sess_bc_list.count()
        if num_bc > 100:
            for to_del in sess_bc_list[:100 - num_bc]:
                to_del.delete()
        return

    #########################################################################
    #
    @classmethod
    def rename_last(cls, request, name):
        """
        This class method will look up the last breadcrumb for this
        user. If its url matches the path of the given request then
        we will set the short name of the breadcrumb to the one provided.

        This is because sometimes we do not know what we want to name
        the breadcrumb until after it has been created, inside the
        view (this is because breadcrumbs are most commonly created
        via a decorator on view functions)
        """
        # First get the last url breadcrumb we made. If its url is the same as
        # the url in the request we were passed then we set the short name
        # of the breadcrumb to the one we were passed.
        #
        if not request.user.is_authenticated():
            # Anonymous users do not get breadcrumb support right now.
            return
        try:
            last_bc = cls.objects.filter(owner = request.user).\
                      order_by('-created')[0]
            if last_bc.url == request.path:
                short_name = shorten_name(name)

                if last_bc.short_name != short_name and \
                   last_bc.name != name:
                    last_bc.short_name = short_name
                    last_bc.name = name
                    last_bc.save()
        except IndexError:
            # Oh, they have no breadcrumbs on this session yet. Nothing
            # to rename.
            #
            pass
        return
