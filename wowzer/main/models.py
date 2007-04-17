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
from django.contrib.contenttypes.models import ContentType

############################################################################
#
class TaggedItem(models.Model):
    """A tag on an item. This was originally cribbed from:
    http://www.djangoproject.com/documentation/models/generic_relations/"""
    tag = models.SlugField(db_index = True, unique = True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = models.GenericForeignKey()
    
    class Meta:
        ordering = ["tag"]
    
    def __str__(self):
        return self.tag

############################################################################
#
class UserTaggedItem(models.Model):
    """A tag on an item. This was originally cribbed from:
    http://www.djangoproject.com/documentation/models/generic_relations/

    The main difference is that a user tagged item belongs to and is
    specific to a user. Not everyone will have permission to tag
    anything, but anything that can be tagged they will have
    permission to make their own private tags against. """
    tag = models.SlugField(db_index = True)
    creator = models.ForeignKey(User, db_index = True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = models.GenericForeignKey()
    
    class Meta:
        ordering = ["tag"]
        unique_together = (("tag", "creator"),)
    
    def __str__(self):
        return self.tag
    
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
                   
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique = True)
    homepage = models.URLField(blank = True)
    style = models.ForeignKey(Style, blank = True, null = True)
    editing_markup = models.CharField(maxlength=128, choices = MARKUP_CHOICES,
                                      default = "text.bbcode")
    signature = models.TextField(maxlength = 1024, blank = True)
    signature_html = models.TextField(maxlength = 1024, blank = True)
    markup = models.CharField(maxlength=80, blank=True)
    
    # If blank defaults to the timezone of django site.
    #
    timezone = models.CharField(maxlength = 128, choices = TZ_CHOICES,
                                default = 'US/Eastern')
    avatar = models.ImageField(upload_to = "img/accounts/%d/avatars",
                               height_field = True, width_field = True,
                               blank = True)
