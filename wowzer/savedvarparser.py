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
            while True:
                self.lstrip()
                if len(self.input) == 0:
                    break
                varname = self._p_re(_varname)
                self.lstrip()
                self._p_simple_string("=")
                self.lstrip()
                
                # After the '=' we can have a '{' for a dictionary declaration
                # or a string, or an integer, or a float.
                #
                self.result[varname] = self._p_expression()
        except:
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
            raise SyntaxError

        return data
        
    #######################################################################
    #
    def _p_string(self):
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
    def _p_integer(self):
        return int(self._p_re(_integer))

    #######################################################################
    #
    def _p_float(self):
        return float(self._p_re(_float))

    #######################################################################
    #
    def _p_dictionary(self):
        """A dictionary is:

        dictionary : LBRACE keyvalues RBRACE
                   | LBRACE RBRACE
                   | LBRACE (LBRACE keyvalues RBRACE,)* RBRACE
        """
        self._p_simple_string('{')
        self.lstrip()

        # Now, either we have an empty dictionary, or we have a keyed
        # dictionary, or we have an implied key dictionary.
        #
        # If the next character is '}' then we have an empty dictionary.
        #
        # If the next character is '[' then we have a keyed dictionary.
        #
        # If the next character is anything else, then we have an implied key
        # dictionary.
        #
        if self.input[0] == '[':
            # keyed dictionary.
            #
            result = self._p_keyvalues()
        elif self.input[0] == '}':
            self.input = self.input[1:]
            # Empty dictionary.
            #
            return {}
        else:
            # An implied key dictionary. We will have a series of comma
            # separate values. The keys are implied integers starting at 1.
            #
            result = self._p_impliedkeyvalues()

        self.lstrip()
        self._p_simple_string('}')
        self.lstrip()
        return result

    ###########################################################################
    #
    def _p_impliedkeyvalues(self):
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
                break
            self.lstrip()
            if self.input.startswith('}'):
                break
        return result

    ###########################################################################
    #
    def _p_keyvalues(self):
        '''keyvalues : keyvalue
                     | keyvalue COMMA
                     | keyvalue COMMA keyvalues'''
        result = {}

        while True:
            (key, value) = self._p_keyvalue()
            result[key] = value

            # If the next character is NOT a comma then we have parsed
            # all the key/values that we can. Return our result
            #
            if self._p_simple_string(',', silent = True) is None:
                break
            # Otherwise we have a comma. After the white space the
            # next character MUST be a '[' or a '}'.
            #
            self.lstrip()
            if self.input.startswith('}'):
                break
            if not self.input.startswith('['):
                raise NoMatch
        return result
            
    #######################################################################
    #
    def _p_keyvalue(self):
        '''keyvalue : LBRACK scalar RBRACK ASSIGN value'''
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
