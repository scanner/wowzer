# File: $Id$
#
"""This module contains the code to parse the variable declarations in a
SavedVariables.lua file."""

import sys
import re
import string
#import lex
#import yacc
import os
import os.path

#############################################################################
#
# Regular expression constants and other constants used to match
# certain structures.
#
_comment = re.compile(r'--.*$', re.MULTILINE)
_varname = re.compile(r'[A-Za-z]\w*')
_integer = re.compile(r'(-|\+)?\d+')
_digit = re.compile(r'-|\+|\d')
_float = re.compile(r'(-|\+)?(\d+)?\.(\d+)?')
_ws = re.compile(r'\s*')
_quoted_string = re.compile(r'"((?:\\"|[^"])*)"(?!")')
_lbrace = re.compile(r'{')
_rbrace = re.compile(r'}')
_lbrack = re.compile(r'\[')
_rbrack = re.compile(r'\]')
_assign = re.compile(r'=')
_comma = re.compile(r',')
_nil = re.compile(r'nil')

ASSIGNMENT = 0
EXPRESSION = 1


#######################################################################
#
class NoMatch(Exception):
    def __init__(self, value = "no match"):
        self.value = value
    def __str__(self):
        return "NoMatch: %s" % self.value

class SVP(object):
    #######################################################################
    #
    def __init__(self, lua_input):
        self.result = {}
        self.tokens = lua_input.split()
        
        try:

            pass
        except StopIteration:
            return


    #######################################################################
    #
    def _p_boolean(self):
        if self._p_simple_string('true', silent = True):
            return True
        
        if self._p_simple_string('false'):
            return False
        
    #######################################################################
    #
    def _p_nil(self):
        if self._p_simple_string('nil'):
            return None

    #######################################################################
    #
    def _p_string(self):
        if self.tokens[0][0] != '"':
            raise NoMatch(value = "'%s' is not the first token in a string" \
                          % self.tokens[0])
        # The first character IS a '"'. We now need to assemble our full string
        # by popping off tokens and appending them to a single string until we
        # get a token that ends with '"' and does NOT end with '\"'
        #

        # Chop off the beginning quote
        #
        self.tokens[0] = self.tokens[0][1:]
        running = True
        result = ""

        while running:
            if self.tokens[0][-1] == '"' and self.tokens[0][-2:] != r'\"':
                self.tokens[0] = self.tokens[0][:-1]
                running = False

            result += self.tokens[0] + " "
            self.tokens.pop(0)

        return result[:-1]
            
    #######################################################################
    #
    def _p_re(self, regexp, silent = False, swallow = True, group = 0,
              syntax_error = None):
        match = regexp.match(self.tokens[0])
        if match is None:
            if silent:
                return None
            else:
                if syntax_error:
                    raise NoMatch(value = syntax_error)
                else:
                    raise NoMatch(value = "No match for r.e. '%s'" % \
                                  regexp.pattern)
        if swallow:
            self.pop(0)
        return match.group(group)
        
    #######################################################################
    #
    def _p_simple_string(self, string, silent = False, swallow = True,
                         case_matters = False, syntax_error = None):

        matched = False
        if case_matters:
            if self.tokens[0] == string:
                matched = True
        else:
            if self.tokens[0].lower() == string.lower():
                matched = True

        if matched and swallow:
            self.tokens.pop(0)

        if matched:
            return string

        if silent:
            return None

        if syntax_error:
            raise NoMatch(value = syntax_error)
        else:
            raise NoMatch(value = "No match for simple string '%s'" % \
                          string)

    #######################################################################
    #
    def __getitem__(self, key):
        return self.result[key]

    #######################################################################
    #
    def get(self, key, default = None):
        return self.result.get(key, default)

    #######################################################################
    #
    def __setitem__(self, key, value):
        self.result[key] = value
        
    #######################################################################
    #
    def __delitem__(self, key):
        del self.result[key]

    #######################################################################
    #
    def __iter__(self):
        return self.result.__iter__()

    #######################################################################
    #
    def iteritems(self):
        return self.result.iteritems()

    #######################################################################
    #
    def iterkeys(self):
        return self.result.iterkeys()

    #######################################################################
    #
    def itervalues(self):
        return self.result.itervalues()

    #######################################################################
    #
    def has_key(self, key):
        return self.result.has_key(key)

    #######################################################################
    #
    def __contains__(self, item):
        return self.result.__contains__(item)

    #######################################################################
    #
    def keys(self):
        return self.result.keys()



    
class SavedVarParser(object):
    """A simplistic parser for turning lua variable structures frequently see
    in World of Warcraft SavedVariables lua files in to python structures
    (lists, dictionaries, strings, integers, floats, etc.)
    """
    #######################################################################
    #
    def __init__(self, lua_structure, input_stream = None):
        self.input = lua_structure
        #self.cur_pos = 0
        self.input_stream = input_stream
        self.line_no = 1
        self.result = {}
        return

    #######################################################################
    #
    def __getitem__(self, key):
        return self.result[key]

    #######################################################################
    #
    def get(self, key, default = None):
        return self.result.get(key, default)

    #######################################################################
    #
    def __setitem__(self, key, value):
        self.result[key] = value
        
    #######################################################################
    #
    def __delitem__(self, key):
        del self.result[key]

    #######################################################################
    #
    def __iter__(self):
        return self.result.__iter__()

    #######################################################################
    #
    def iteritems(self):
        return self.result.iteritems()

    #######################################################################
    #
    def iterkeys(self):
        return self.result.iterkeys()

    #######################################################################
    #
    def itervalues(self):
        return self.result.itervalues()

    #######################################################################
    #
    def has_key(self, key):
        return self.result.has_key(key)

    #######################################################################
    #
    def __contains__(self, item):
        return self.result.__contains__(item)

    #######################################################################
    #
    def keys(self):
        return self.result.keys()

    #######################################################################
    #
    def parse(self):
        """Parse the input from an ascii representation of a lua variable
        structure in to a python dictionary. The dictionary will have a key for
        each variable declaration in the input. The value will be the value
        that was assigned to that variable in the lua input.
        """

        self.result = {}
        
        # Basically loop until we have no more input to swallow and parse.
        #
        try:
            while len(self.input) > 0:
                self.lstrip()
                varname = self._p_re(_varname)
                print "Got varname: %s" % varname
                self.lstrip()
                self._p_simple_string("=")
                self.lstrip()
                
                # After the '=' we can have a '{' for a dictionary declaration
                # or a string, or an integer, or a float.
                #
                self.result[varname] = self._p_expression()
        except:
            print "Exception at line %d" % self.line_no
            raise
            
        return self.result
        
    #######################################################################
    #
    def lstrip(self):
        """
        Strip the beginning of the input of any white space or comments.
        """
        self.input = self.input.lstrip()
        self._p_re(_comment, silent = True, swallow = True)
        self.input = self.input.lstrip()
        return
    
    #######################################################################
    #
    def _p_expression(self):
        """An expression is a dictionary, or a string, or an integer, or a
        float. 
        """
#        print "Entered _p_expression: line #: %d '%s'" % (self.line_no, self.input[:10])
        data = None
        found = False

        if self.input[0] == '{':
            data = self._p_dictionary()
        elif self.input[0] == '"':
            data = self._p_string()
        elif _digit.match(self.input[0]):
            try:
                data = self._p_float()
            except NoMatch:
                data = self._p_integer()
        elif self.input[:3].lower() == 'nil':
            data = self._p_nil()
        elif self.input[0].lower() in ('t', 'f'):
            data = self._p_boolean()
        else:
#            print "SyntaxError, unparseable expression: '%s'" % self.input[:10]
            raise SyntaxError

##         for func in (self._p_dictionary, self._p_string, self._p_float,
##                      self._p_integer, self._p_nil, self._p_boolean):
##             try:
##                 data = func()
##                 found = True
##                 break
##             except NoMatch:
##                 pass

##         if not found:
##             raise SyntaxError
        return data
        
    #######################################################################
    #
    def _p_string(self):
#        print "Entered _p_string: line #: %d '%s'" % (self.line_no, self.input[:10])

        return self._p_re(_quoted_string, group = 1)

    #######################################################################
    #
    def _p_boolean(self):
        if self._p_simple_string('true', silent = True):
            return True
        
        if self._p_simple_string('false'):
            return False
        
    #######################################################################
    #
    def _p_nil(self):
        if self._p_simple_string('nil'):
            return None

    #######################################################################
    #
##     def _p_ws(self):
##         """A special parser for white space. If we get a match
##         it will count all the occurrences of '\n' in the string we match.
##         """
## #        print "Entered _p_ws: line #: %d '%s'" % (self.line_no, self.input[:10])
##         match = self._p_re(_ws)
##         if match is not None and len(match) > 0:
##             self.line_no += match.count('\n')
            
    #######################################################################
    #
    def _p_integer(self):
#        print "Entered _p_int: line #: %d '%s'" % (self.line_no, self.input[:10])
        return int(self._p_re(_integer))

    #######################################################################
    #
    def _p_float(self):
#        print "Entered _p_float: line #: %d '%s'" % (self.line_no, self.input[:10])
        return float(self._p_re(_float))

    #######################################################################
    #
    def _p_dictionary(self):
        """A dictionary is:

        dictionary : LBRACE keyvalues RBRACE
                   | LBRACE RBRACE
                   | LBRACE (LBRACE keyvalues RBRACE,)* RBRACE
        """
#        print "Entered _p_dictionary: line #: %d '%s'" % (self.line_no, self.input[:10])
        self._p_simple_string('{')
        self.lstrip()

        # the next character should be a '[' which indicates a key value
        # pair, or '{' which indicates that we have an implied key
        # if it is not any of these, we should find a '}' indicating an
        # empty dictionary.
        #
        if self.input[0] not in ('[', '{'):
            self._p_simple_string('}')
#            print "Leaving _p_dictionary (empty dictionary)"
            return {}

        # See if we have an implied key/value pair.
        #
        if self.input.startswith('{'):
            result = self._p_impliedkeyvalues()
        else:
            # Otherwise we MUST have a bracket and at least one set of
            # keyvalues. 
            #
            result = self._p_keyvalues()
        self._p_simple_string('}')
        self.lstrip()
#        print "Leaving _p_dictionary"
        return result

    ###########################################################################
    #
    def _p_impliedkeyvalues(self):
#        print "Entered _p_impliedkeyvalues: line #: %d '%s'" % (self.line_no, self.input[:10])
        result = {}

        index = 0
        while True:
            index += 1  # implied key/values start with a key of 1.
            result[index] = self._p_expression()
            self.lstrip()
            # If the next character is NOT a comma then we have parsed
            # all the key/values that we can. Return our result
            #
            if self._p_simple_string(',', silent = True) is None:
#                print "   Next character is NOT a comma"
                break
#            print "    FOUND COMMA"
            # Otherwise we have a comma. After the white space the
            # next character MUST be a '[' or a '}'.
            #
            self.lstrip()
#            print "Input starts with: %s" % self.input[:20]
            if self.input.startswith('}'):
                break
            if not self.input.startswith('{'):
                raise NoMatch
#        print "Leaving _p_impliedkeyvalues"
        return result

    ###########################################################################
    #
    def _p_keyvalues(self):
        '''keyvalues : keyvalue
                     | keyvalue COMMA
                     | keyvalue COMMA keyvalues'''
#        print "Entered _p_keyvalues: line #: %d '%s'" % (self.line_no, self.input[:10])
        result = {}

        while True:
            (key, value) = self._p_keyvalue()
            result[key] = value

            # If the next character is NOT a comma then we have parsed
            # all the key/values that we can. Return our result
            #
            if self._p_simple_string(',', silent = True) is None:
#                print "   Next character is NOT a comma"
                break
#            print "    FOUND COMMA"
            # Otherwise we have a comma. After the white space the
            # next character MUST be a '[' or a '}'.
            #
            self.lstrip()
            if self.input.startswith('}'):
                break
            if not self.input.startswith('['):
                raise NoMatch
#        print "Leaving _p_keyvalues"
        return result
            
    #######################################################################
    #
    def _p_keyvalue(self):
        '''keyvalue : LBRACK scalar RBRACK ASSIGN value'''
#        print "Entered _p_keyvalue: line #: %d '%s'" % (self.line_no, self.input[:10])
        self._p_simple_string('[')
#        self.lstrip()

        # The key can be either a string or an integer. If it begins with a '"'
        # then it must be a string. (in a real language this could also be a
        # variable.
        #
        if self.input.startswith('"'):
            key = self._p_string()
        else:
            key = self._p_integer()
##         self.lstrip()
##         self._p_simple_string(']')
##         self.lstrip()
##         self._p_simple_string('=')
##         self.lstrip()
        # XXX Hack. We are parsing regular lua saved variables. We know that
        # XXX the next 4 characters are ALWAYS '] = '
        #
        self.input = self.input[4:]
        value = self._p_expression()
        self.lstrip()
#        print "Leaving _p_keyvalue (key: %s)" % str(key)
        return (key, value)
    
    #######################################################################
    #
    def _p_re(self, regexp, silent = False, swallow = True, group = 0,
              syntax_error = None):
        """This will attempt to match (ie: at the beginning of the string)
        the given regular expression with our current input string. If it
        matches it will return what matched. If 'silent' is False, and it did
        NOT match, then it will raise the NoMatch exception. If 'swallow' is
        True, then it will chop off the matched characters from the beginning
        of our input string.

        If 'group' is specified (an integer!) it will be passed to the match
        object's group() method letting the caller pick what part of the
        match they wish returned to them. Of course the r.e. used must have
        appropiate matching group's specified.

        NOTE: If the match fails then we do NOT swallow any input even if
              swallow = True
        """
        #match = regexp.match(self.input)
        match = regexp.match(self.input)
        if match is None:
            if silent:
                return None
            else:
                if syntax_error:
                    raise NoMatch(value = syntax_error)
                else:
                    raise NoMatch(value = "No match for r.e. '%s'" % \
                                  regexp.pattern)
        if swallow:
            # self.cur_pos += match.end()
            self.input = self.input[match.end():]
        return match.group(group)

    #######################################################################
    #
    def _p_simple_string(self, string, silent = False, swallow = True,
                        case_matters = False, syntax_error = None):
        """Like p_re(), this is used to parse a bit of input. However it just
        a well defined string so there is no waste time invoking a regular
        expression.

        If 'case_matters' is True then the string comparsion is exact (case
        sensitive.) Otherwise the match is case insensitive.

        If 'case_matters' is False the returned string is forced to lower case.

        If we do not match, then input is not swallowed even if swallow = True.
        """
        if not self.input.startswith(string):
            if silent:
                return None
            else:
                raise NoMatch(value = "No match for simple string. Expected: '%s', found: '%s'" % (string, self.input[:20]))
        self.input = self.input[len(string):]
        return string

##         str_len = len(string)
##         if len(self.input) < str_len:
##             match = None
##         else:
##             if case_matters:
##                 if self.input[:str_len] == string:
##                     match = string
##                 else:
##                     match = None
##             else:
##                 if self.input[str_len].lower() == string.lower():
##                     match = string.lower()
##                 else:
##                     match = None
                
##         if match is None:
##             if silent:
##                 return None
##             else:
##                 if syntax_error:
##                     raise NoMatch(value = syntax_error)
##                 else:
##                     raise NoMatch(value = "No match for simple string '%s'" % \
##                                   string)
##         if swallow:
##             #self.cur_pos += len(string)
##             self.input = self.input[str_len:]
##         return match

    #
    # Done token parsing routines.
    #
    #######################################################################
    #######################################################################
            
#############################################################################
#
# Our class for parsing lua files that only have variable declarations from
# constants.
#
# Way slow.
## class ParseSavedVariables:
##     """This class uses the PLY lexx/yacc tools to define a gramar that will
##     read in a SavedVariables.lua file and return a dictionary that has defined
##     as keys the variable declarations from the SavedVariables.lua. Lua hashes
##     are turned in to python dictionaries. We have support for strings, ints,
##     floats, and booleans.
##     """
##     tokens = (
##         'STRING', 'INTEGER', 'FLOAT', 'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
##         'ASSIGN', 'COMMA', 'BOOLEAN', 'NAME', 'BIGNUM'
##         )

##     # Actual token definitions as regular expressions
##     #
##     t_STRING = r'\"([^\\\n]|(\\\n)|(\\.))*?\"'
##     t_NAME   = r'[a-zA-Z][a-zA-Z0-9_]*'
##     t_ASSIGN = r'='
##     t_INTEGER = r'[0-9]+'
##     t_FLOAT  = r'[0-9]+\.[0-9]+'
##     t_BIGNUM = r'[0-9]+(\.[0-9]+)?e\+[0-9]+'
##     t_LBRACE = r'{'
##     t_RBRACE = r'}'
##     t_LBRACK = r'\['
##     t_RBRACK = r'\]'
##     t_COMMA  = r','
##     t_BOOLEAN = r'([Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee])'


##     # We ignore white space
##     #
##     t_ignore = ' \t'

##     # We count newlines so we can report parsing errors
##     #
##     def t_newline(self, t):
##         r'[\r\n]+'
##         t.lineno += t.value.count("\n")
##         t.lineno += t.value.count("\r")

##     def t_error(self, t):
##         print "Illegal character '%s' at line: %d" % (t.value[0], t.lineno)
##         t.skip(1)

##     ##
##     ## And so ends the lexer
##     ##
##     #########################################################################
##     #########################################################################
##     ##
##     ## And so begins the parser
##     ##
##     def p_declarations(self, p):
##         '''declarations : declaration
##                         | declaration declarations'''
##         return

##     # Here is where variables are declared. We only want to really store
##     # declarations of variables that we actually care about so if the NAME is
##     # not one that we care about we just skip it. Otherwise, we assign a key in
##     # our variables dictionary to be the value we have parsed out for this
##     # declaration.
##     #
##     def p_declaration(self, p):
##         '''declaration : NAME ASSIGN value'''
##         self.variables[p[1]] = p[3]
##         return

##     def p_value(self, p):
##         '''value : dictionary
##                  | scalar'''
##         p[0] = p[1]
##         return

##     def p_scalar(self, p):
##         '''scalar : string
##                   | integer
##                   | float
##                   | bignum
##                   | boolean'''
##         p[0] = p[1]
##         return

##     def p_string(self, p):
##         '''string : STRING'''
##         p[0] = p[1][1:-1]
##         return

##     def p_integer(self, p):
##         '''integer : INTEGER'''
##         p[0] = int(p[1])
##         return

##     def p_float(self, p):
##         '''float : FLOAT'''
##         p[0] = float(p[1])
##         return

##     # Going to force the scientific notation bigums in to ints because that is
##     # the only way they are used in the SavedVariables.lua file
##     #
##     def p_bignum(self, p):
##         '''bignum : BIGNUM'''
##         p[0] = int(float(p[1]))
##         return

##     def p_boolean(self, p):
##         '''boolean : BOOLEAN'''
##         if string.lower(p[1]) == "true":
##             p[0] = True
##         else:
##             p[0] = False
##         return
    
##     def p_dictionary(self, p):
##         '''dictionary : LBRACE keyvalues RBRACE
##                       | LBRACE RBRACE
##         '''
##         if len(p) == 4:
##             p[0] = dict(p[2])
##         elif len(p) == 3:
##             p[0] = {}
##         return

##     def p_keyvalues(self, p):
##         '''keyvalues : keyvalue
##                      | keyvalue COMMA
##                      | keyvalue COMMA keyvalues'''
##         if len(p) == 2 or len(p) == 3:
##             p[0] = [ p[1] ]
##         elif len(p) == 4:
##             p[3].append(p[1])
##             p[0] = p[3]
##         return

##     def p_keyvalue(self, p):
##         '''keyvalue : LBRACK scalar RBRACK ASSIGN value'''
##         p[0] = ( p[2], p[5] )
##         return

##     def p_error(self, p):
##         while True:
##             tok = yacc.token()
##             if not tok or tok.type == 'RBRACE':
##                 break
##         yacc.restart()

##     ##
##     ## And so ends the parser declaration
##     ##
##     ########################################################################

##     ########################################################################
##     #
##     def __init__(self, output_dir = None):
##         """This will initialize our lexer and parser and define the dictionary
##         used to hold the results of our parsing.
##         """

##         # We dump our parser table in to the media top directory of the wowzer
##         # app.. we can reverse engineer where that is from where this file is.
##         #
##         if output_dir is None:
##             output_dir = os.normpath(\
##                 os.path.join(os.path.dirname(__file__) , "..", "..", "media"))
##             sys.stderr.write("SavedParser - parse tables will be in: %s " % \
##                              output_dir)
##             sys.stderr.flush()

##         self.variables = {}
##         self.lexer = lex.lex(module = self)
##         self.parser = yacc.yacc(module = self, outputdir = output_dir,
##                                 tabmodule="savedvarparser")
##         # self.parser = yacc.yacc(module = self, write_tables = 0)

##         return

##     ######################################################################
##     #
##     def process(self, data):
##         """We are handed a string which contains the entire lua script we wish
##         to parse. When this is done self.variables will be a dictionary which
##         will have a key for every variable defined in the data we have parsed.

##         One big assumption here to save time is that we are parsing a file that
##         only has in it the data we care about!
##         """
##         self.lexer.input(data)
##         self.parser.parse()
