#
# File: $Id$
#
'''Template tag library provided by the asforums app to make some things
easier and other things possible.
'''

from django import template

register = template.Library()

#############################################################################
#
viewable_by_user(parser, token):
    """The parser component of a template tag that will apply the 'viewable by a
    specific user' filter to query sets passed as arguments. 'user' is taken
    from the template context when it is being rendered."""

    try:
        tag_name, query_set_to_filter, method = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r requires exactly two " \
            "arguemnts" % token[0]
    return ViewableByUserNode(query_set_to_filter, method)

