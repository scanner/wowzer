#
# File: $Id$
#
'''Template tag library provided by the asforums app to make some things
easier and other things possible.
'''

from django import template
from django.template import resolve_variable

register = template.Library()

#############################################################################
#
@register.tag(name="viewable_by_user")
def viewable_by_user(parser, token):
    """The parser component of a template tag that will apply the 'viewable
    by a specific user' filter to query sets passed as arguments. 'user' is
    taken from the template context when it is being rendered."""

    try:
        tag_name, query_set_to_filter, method = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r requires exactly two " \
            "arguemnts" % token[0]
    return ViewableByUserNode(query_set_to_filter, method)

class ViewableByUserNode(template.Node):
    """Template node to render some query set, and then invoke the named
    method on that query set.
    """
    def __init__(self, query_set, method_name):
        self.query_set = query_set
        self.method_name = method_name

    def render(self, context):
        try:
            qs = resolve_variable(self.query_set, context)
            qs = qs.viewable(request.user)
            if hasattr(qs,self.method_name):
                # If this is a method then invoke it as a function.
                #
                if isinstance(getattr(qs, self.method_name), MethodType):
                    return getattr(qs, self.method_name)()
                else:
                    return getattr(qs, self.method_name)()
        except:
            # render() should never raise any exception. If something goes
            # wrong we need to log it somewhere else, not chuck it up the
            # call stack.
            #
            return ""

##############################################################################
#
def has_perm_chain(parser, token):
    """This custom tag deal with per object permissions and the permission
    chain required for the asforum system. For things like 'post' and 'read'
    permissions on a discussion, the user must have the permissions from all
    containing objects as well. ie: in order to post to a discussion they must
    have post permission on the discussion and post permission on the forum
    and post permission on the forum collection.

    This helper will use the permission inheritance map from the models file
    to check to see if a user has the permissions necessary for this
    object.

    This will also support an 'or' syntax so you can do things like 'if user
    has edit permission on this post or moderate permission on this forum they
    can edit this post.

    Checks permission on the given user. Checks row-level permissions if an
    object is given.

    Perm name should be in the format [app_label].[perm codename].
    """
    bits = token.contents.split()
    del bits[0]
    if not bits:
        raise TemplateSyntaxError, \
              "'if' statement requires at least one argument"
    # bits now looks something like this: ['a', 'b', 'or', 'not', 'b', 'c',
    # 'or', 'c.d', 'e.f']
    #
    # See if we have any 'and' or 'or' statements. THey can only use one or
    # the other in a single tag.
    #
    bitstr = ' '.join(bits)
    boolpairs = bitstr.split(' and ')
    boolvars = []
    if len(boolpairs) == 1:
        link_type = HasPermChainNode.LinkTypes.or_
        boolpairs = bitstr.split(' or ')
    else:
        link_type = HasPermChainNode.LinkTypes.and_
        if ' or ' in bitstr:
            raise TemplateSyntaxError, "'if' tags can't mix 'and' and 'or'"
    
    # Make sure each 'boolpairs' set is one two or three terms. If it is three
    # terms the first must be 'not'. If it is two terms the first is a
    # permission and the second is an object instance. If it is one term it is
    # a permission (for all objects of that class)
    #
    for boolpair in boolpairs:
        if ' ' in boolpair:
            elts = boolpair.split()
            if elts == 3:
                if elts[0] != 'not':
                    raise TemplateSyntaxError, "Expected 'not' in if statement"
                else:
                    pass
                
    
    

    
class HasPermChainNode(Node):
    def __init__(self, bool_exprs, nodelist_true, nodelist_false, link_type):
        self.bool_exprs = bool_exprs
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.link_type = link_type

    def __repr__(self):
        return "<If node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        if self.link_type == IfNode.LinkTypes.or_:
            for ifnot, bool_expr in self.bool_exprs:
                try:
                    value = bool_expr.resolve(context, True)
                except VariableDoesNotExist:
                    value = None
                if (value and not ifnot) or (ifnot and not value):
                    return self.nodelist_true.render(context)
            return self.nodelist_false.render(context)
        else:
            for ifnot, bool_expr in self.bool_exprs:
                try:
                    value = bool_expr.resolve(context, True)
                except VariableDoesNotExist:
                    value = None
                if not ((value and not ifnot) or (ifnot and not value)):
                    return self.nodelist_false.render(context)
            return self.nodelist_true.render(context)

    class LinkTypes:
        and_ = 0,
        or_ = 1
