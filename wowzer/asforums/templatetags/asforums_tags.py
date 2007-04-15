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
            pass
        return ""

##############################################################################
#
@register.tag(name = 'fancy_if')
def fancy_if(parser, token):
    """A fancy if tag. It has two notable features:

    1) you can combine and, or, and not statements nested as much as you like.
    2) you can test object like {% if %} AND you can test row level permissions
       in the same expression.

    NOTE: To simplify my sanity, I use a simple prefix expression.

    So, for example, to test if a discussion is not locked or the user
    has moderate permission on the forum the discussion is in:

    {% fancy_if or not discussion.locked 'asforums.has_moderate' discussion.forum %} ... {% else %} {% end_fancy_if %}

    The syntax is:

    {% fancy_if expr %}

    An expr may be:
    
       ( expr )
       or expr ...   (a list of one or more expr's or'd together)
       and expr ...  (a list of one or more expr's or'd together)
       not expr
       'permission code name' <variable>|None
       eq <variable>|'string' <variable>|'string'
       <variable>

    If you wish to nest or & and you use '(' ')' to express the
    sub-expression. These characters MUST be separated by white space, ie:

    Good: ( and foo bar biz bat )
    Bad:  (and foo bar biz bat)

    NOTE: Permissions are expressed by being surrounded by matching
    double or single quotes. ie: 'asforums.forum_moderate' or
    'asforums.disc_read'.

    NOTE: The permission expression MUST be two tokens. A permission
    and a variable reference. If you wish to do class level permission
    checking using the value 'None' (with no quotes!) as the variable
    reference.
    """

#    print "entered fancy_if!"
    bits = token.contents.split()
    tag = bits.pop(0)
    if not bits:
        raise template.TemplateSyntaxError, \
            "'fancy_if' statement requires at least one argument"
    expr = parse_fi_expressions(bits, parser)
    
    nodelist_true = parser.parse(('else', 'end_' + tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('end_' + tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return FancyIfNode(expr, nodelist_true, nodelist_false)

##############################################################################
#
class FancyIfNode(template.Node):
    """The template Node object that represents our 'fancy if'.
    """
    def __init__(self, expr, nodelist_true, nodelist_false):
        self.expr = expr
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<FancyIf: %s >" % repr(self.expr)

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
        if self.expr.eval(context):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

        
##############################################################################
#
def parse_fi_expressions(tokens, parser):
    """Given a list of tokens that comprised the 'fancy_if' statement
    parse them in to a list of node trees that represents the expressions to
    be evaluated.
    """
#    print "entered pfie, tokens: %s" % str(tokens)
    try:
        token = tokens.pop(0)
        if token == "(":
#            print "Got a '%s' parsing sub-expression" % token
            res = parse_fi_expressions(tokens, parser)
            if tokens.pop(0) != ")":
                raise template.TemplateSyntaxError, "Missing matching ')'"
            return res
        elif token  == "not":
#            print "Got a '%s' parsing sub-expression" % token
            if len(tokens) < 1:
                raise TemplateSyntaxError, "'%s' must come with an expres" \
                    "sion to operate on." % token
            return FiNot(parse_fi_expressions(tokens, parser))
        elif token in ("and", "or"):
#            print "Got a '%s' parsing sub-expression" % token
            if len(tokens) < 1:
                raise TemplateSyntaxError, "'%s' must come with a list of " \
                    "expressions to operate on." % token
            res = []
            while len(tokens) > 0:
                if tokens[0] == ")":
                    break
                res.append(parse_fi_expressions(tokens, parser))
            if token == "and":
                return FiAnd(res)
            return FiOr(res)

        elif token[0] == token[-1] and token[0] in ('"', "'"):
#            print "Got a '%s' parsing sub-expression" % token
            return FiPerm(token[1:-1],
                          parser.compile_filter(tokens.pop(0)))
        elif token == "eq":
#            print "Got a '%s' parsing sub-expression" % token
            return FiEquals(parser.compile_filter(tokens.pop(0)),
                            parser.compile_filter(tokens.pop(0)))

        # Otherwise it is just a variable reference.
        #
#        print "Got a '%s' assuming FiVar" % token
        return FiVar(parser.compile_filter(token))
    except IndexError:
        raise template.TemplateSyntaxError, "Mis-matched terms and " \
              "operators. Ran out of tokens whilst parsing arguments."
    
##############################################################################
#
# Here we have a simple set of classes to define our parsed expression
# syntax in a format that is easy to eval when we have a context we need
# to render. We define a sub-class for each type of operation. They must
# have an eval() method which returns True or False, and a __repr__ method
# that gives us a simple string representation.
#
class FiExpr(object):
    """The root object for the expression tree in our fancy-if node.
    """
    def __repr__(self):
        raise NotImplementedError
        
    def eval(self, context):
        raise NotImplementedError

class FiNot(FiExpr):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "(not: %s )" % repr(self.expr)

    def eval(self, context):
        return not self.expr.eval(context)

class FiAnd(FiExpr):
    def __init__(self, expr_list):
        self.expr_list = expr_list

    def __repr__(self):
        return "(and:" + " ".join([repr(x) for x in self.expr_list]) + " )"

    def eval(self, context):
        for elt in self.expr_list:
            if not elt.eval(context):
                return False
        return True

class FiOr(FiExpr):
    def __init__(self, expr_list):
        self.expr_list = expr_list

    def __repr__(self):
        return "(or:" + " ".join([repr(x) for x in self.expr_list]) + " )"

    def eval(self, context):
        for elt in self.expr_list:
            if elt.eval(context):
                return True
        return False

class FiEquals(FiExpr):
    def __init__(self, obj_var1, obj_var2):
        self.obj_var1 = obj_var1
        self.obj_var2 = obj_var2

    def __repr__(self):
        return "( eq %s %s )" % (self.obj_var1, self.obj_var2)

    def eval(self, context):
        try:
            obj1 = self.obj_var1.resolve(context)
        except template.VariableDoesNotExist:
            obj1 = None
        try:
            obj2 = self.obj_var2.resolve(context)
        except template.VariableDoesNotExist:
            obj2 = None
        return obj1 == obj2

class FiPerm(FiExpr):
    def __init__(self, perm, obj_var):
        self.perm = perm
        self.obj_var = obj_var

    def __repr__(self):
        return "(has perm '%s' on %s )" % (self.perm,
                                           self.obj_var.var)

    def eval(self, context):
        if self.obj_var == None:
            obj = None
        else:
            try:
                obj = self.obj_var.resolve(context)
            except template.VariableDoesNotExist:
                obj = None
        try:
            user = template.resolve_variable("user", context)
        except template.VariableDoesNotExist:
            return settings.TEMPLATE_STRING_IF_INVALID

        return user.has_perm(self.perm, object=obj)

class FiVar(FiExpr):
    def __init__(self, obj_var):
        self.obj_var = obj_var

    def __repr__(self):
        return self.obj_var.var

    def eval(self, context):
        try:
            obj = self.obj_var.resolve(context)
        except template.VariableDoesNotExist:
            obj = None
        if obj:
            return True
        return False
