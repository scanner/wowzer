#
# File: $Id$
#
"""
"""

# System imports.
#
import pytz
import types

# Django imports
#
from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Models
#
from django.contrib.auth.models import User
from wowzer.main.models import UserProfile, Breadcrumb

register = template.Library()

#############################################################################
#
# This code was gotten from: http://code.djangoproject.com/wiki/PaginatorTag
#
@register.inclusion_tag("paginator.html", takes_context=True)
def paginator(context, adjacent_pages=2):
    """Adds pagination context variables for first, adjacent and next page
    links in addition to those already populated by the object_list generic
    view."""
    page_numbers = \
                 [n for n in \
                  range(context["page"] - adjacent_pages, context["page"] + \
                        adjacent_pages + 1) \
                  if n > 0 and n <= context["pages"]]
    return {
        "hits": context["hits"],
##         "order_by" : context["order_by"],
        "results_per_page": context["results_per_page"],
        "page": context["page"],
        "pages": context["pages"],
        "page_numbers": page_numbers,
        "next": context["next"],
        "previous": context["previous"],
        "has_next": context["has_next"],
        "has_previous": context["has_previous"],
        "show_first": 1 not in page_numbers,
        "show_last": context["pages"] not in page_numbers,
    }

#
#############################################################################

#############################################################################
#
# This code was gotten from: http://code.djangoproject.com/wiki/ColumnizeTag
#
@register.tag('columnize')
def columnize(parser, token):
    '''Put stuff into columns. Can also define class tags for rows and cells

    Usage: {% columnize num_cols [row_class[,row_class2...]|''
           [cell_class[,cell_class2]]] %}

    num_cols:   the number of columns to format.
    row_class:  can use a comma (no spaces, please) separated list that
                cycles (utilizing the cycle code) can also put in '' for
                nothing, if you want no row_class, but want a cell_class.
    cell_class: same format as row_class, but the cells only loop within a
                row. Every row resets the cell counter.

    Typical usage:

    <table border="0" cellspacing="5" cellpadding="5">
    {% for o in some_list %}
       {% columnize 3 %}
          <a href="{{ o.get_absolute_url }}">{{ o.name }}</a>
       {% endcolumnize %}
    {% endfor %}
    </table>
    '''
    nodelist = parser.parse(('endcolumnize',))
    parser.delete_first_token()

    #Get the number of columns, default 1
    columns = 1
    row_class = ''
    cell_class = ''
    args = token.contents.split(None, 3)
    num_args = len(args)
    if num_args >= 2:
        #{% columnize columns %}
        if args[1].isdigit():
            columns = int(args[1])
        else:
            raise template.TemplateSyntaxError('The number of columns must ' \
                                               'be a number. "%s" is not a ' \
                                               'number.') % args[2]
    if num_args >= 3:
        #{% columnize columns row_class %}
        if "," in args[2]:
            #{% columnize columns row1,row2,row3 %}
            row_class = [v for v in args[2].split(",") if v]  # split and kill
                                                              # blanks
        else:
            row_class = [args[2]]
            if row_class == "''":
                # Allow the designer to pass an empty string (two quotes) to
                # skip the row_class and only have a cell_class
                row_class = []
    if num_args == 4:
        #{% columnize columns row_class cell_class %}
        if "," in args[3]:
            #{% columnize row_class cell1,cell2,cell3 %}
            cell_class = [v for v in args[3].split(",") if v] # split and kill
                                                              # blanks
        else:
            cell_class = [args[3]]
            if cell_class == "''":
                # This shouldn't be necessary, but might as well test for it
                cell_class = []

    return ColumnizeNode(nodelist, columns, row_class, cell_class)

class ColumnizeNode(template.Node):
    def __init__(self, nodelist, columns = 1, row_class = '', cell_class = ''):
        self.nodelist = nodelist
        self.columns = int(columns)
        self.counter = 0
        self.rowcounter = -1
        self.cellcounter = -1
        self.row_class_len = len(row_class)
        self.row_class = row_class
        self.cell_class_len = len(cell_class)
        self.cell_class = cell_class

    def render(self, context):
        output = ''
        self.counter += 1
        if (self.counter > self.columns):
            self.counter = 1
            self.cellcounter = -1

        if (self.counter == 1):
            output = '<tr'
            if self.row_class:
                self.rowcounter += 1
                output += ' class="%s">' % self.row_class[self.rowcounter % self.row_class_len]
            else:
                output += '>'

        output += '<td'
        if self.cell_class:
            self.cellcounter += 1
            output += ' class="%s">' % self.cell_class[self.cellcounter % self.cell_class_len]
        else:
            output += '>'

        output += self.nodelist.render(context) + '</td>'

        if (self.counter == self.columns):
            output += '</tr>'

        return output
#
#############################################################################

#############################################################################
#
@register.inclusion_tag("main/helpers/icon.html")
def icon(icon_name, icon_title=""):
    """The defines a django inclusion tag called 'icon'

    This will insert the standard html defined for one of our icons
    with the path of icon is supposed to be (the latter part will
    later on become a configurable item letting us switch to different
    icon sets (although then we need to know the user.)
    """

    # I wish it had the context of the original request
    #

    return { 'MEDIA_URL' : settings.MEDIA_URL,
             'icon_dir'  : 'img/silk-icons/',
             'icon_name' : icon_name,
             'icon_title': icon_title }


#############################################################################
#
@register.filter()
def user_tz(value, user):
    """Expects a datetime as the value. Expects a User object as the arg.
    Looks up the 'timezone' value in the user's profile, and converts
    the given datetime in to one in the user's timezone.

    NOTE: This assumes that you have the 'pytz' module
    (pytz.sourceforge.net) and that the user profile has a field
    called 'timezone' that is a character string and that the timezone
    thus specified is a valid timezone supported by pytz.
    """
    tz = settings.TIME_ZONE
    if isinstance(user, User):
        try:
            tz = user.get_profile().timezone
        except ObjectDoesNotExist:
            pass
    try:
        result = value.astimezone(pytz.timezone(tz))
    except ValueError:
        # Hm.. the datetime was stored 'naieve' ie: without timezone info.
        # we assume the timezone in 'settings' for all naieve objects.
        #
        result = value.replace(tzinfo=pytz.timezone(settings.TIME_ZONE)).astimezone(pytz.timezone(tz))
    return result

#############################################################################
#
@register.filter()
def tz_std_date(value, user):
    """This is a simplification of the kinds of time stamps we
    frequently use in our app framework. The given datetime, expressed
    in the user's profile's time zone in a standard format (that is
    defined using the django standard settings.DATETIME_FORMAT.

    XXX Later on we may add the ability for a user to specify their own date
    XXX time format to use.
    """
    from django.utils.dateformat import DateFormat
    df = DateFormat(user_tz(value, user))
    return df.format(settings.DATETIME_FORMAT)

#############################################################################
#
@register.filter()
def tz_std_date_ago(value, user):
    """This is a further simplification of the kinds of time stamps we
    frequently use in our app framework. It is just like tz_std_date, except
    we return the datetime string with ' (<timesince> ago)'
    """
    from django.utils.timesince import timesince
    return "%s (%s ago)" % (tz_std_date(value, user), timesince(value))

#############################################################################
#
@register.tag("breadcrumbs")
def do_breadcrumbs(parser, token):
    """
    A tag that will stick the list of breadcrumbs to render on a page
    in the context of that page.
    """
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single " \
              "argument" % token.contents[0]
    return Breadcrumbs(var_name)

#############################################################################
#
class Breadcrumbs(template.Node):
    """
    The node class for our new tag that lets you define a variable in the
    template that contains a list of the last <n> breadcrumbs for this session
    """
    ########################################################################
    #
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        """
        Use the request.user object in the context to get the
        breadcrumbs for this user. Insert the past <n> breadcrumbs
        as the specified variable name in our context.

        """
        if context['request'].user.is_authenticated():
            context[self.var_name] = Breadcrumb.objects.filter(owner = context['request'].user)[:10:-1]
        else:
            context[self.var_name] = []
        return ""
