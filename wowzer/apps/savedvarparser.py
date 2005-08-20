# File: $Id$
#
"""This module contains the code to parse the variable declarations in a
SavedVariables.lua file."""

import string
import lex
import yacc
import os
import os.path

#############################################################################
#
# Our class for parsing lua files that only have variable declarations from
# constants.
#
# Way slow.
class ParseSavedVariables:
    """This class uses the PLY lexx/yacc tools to define a gramar that will
    read in a SavedVariables.lua file and return a dictionary that has defined
    as keys the variable declarations from the SavedVariables.lua. Lua hashes
    are turned in to python dictionaries. We have support for strings, ints,
    floats, and booleans.
    """
    tokens = (
        'STRING', 'INTEGER', 'FLOAT', 'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
        'ASSIGN', 'COMMA', 'BOOLEAN', 'NAME', 'BIGNUM'
        )

    # Actual token definitions as regular expressions
    #
    t_STRING = r'\"([^\\\n]|(\\\n)|(\\.))*?\"'
    t_NAME   = r'[a-zA-Z][a-zA-Z0-9_]*'
    t_ASSIGN = r'='
    t_INTEGER = r'[0-9]+'
    t_FLOAT  = r'[0-9]+\.[0-9]+'
    t_BIGNUM = r'[0-9]+(\.[0-9]+)?e\+[0-9]+'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACK = r'\['
    t_RBRACK = r'\]'
    t_COMMA  = r','
    t_BOOLEAN = r'([Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee])'


    # We ignore white space
    #
    t_ignore = ' \t'

    # We count newlines so we can report parsing errors
    #
    def t_newline(self, t):
        r'\n+'
        t.lineno += t.value.count("\n")

    def t_error(self, t):
        print "Illegal character '%s' at line: %d" % (t.value[0], t.lineno)
        t.skip(1)

    ##
    ## And so ends the lexer
    ##
    #########################################################################
    #########################################################################
    ##
    ## And so begins the parser
    ##
    def p_declarations(self, p):
        '''declarations : declaration
                        | declaration declarations'''
        return

    # Here is where variables are declared. We only want to really store
    # declarations of variables that we actually care about so if the NAME is
    # not one that we care about we just skip it. Otherwise, we assign a key in
    # our variables dictionary to be the value we have parsed out for this
    # declaration.
    #
    def p_declaration(self, p):
        '''declaration : NAME ASSIGN value'''
        self.variables[p[1]] = p[3]
        return

    def p_value(self, p):
        '''value : dictionary
                 | scalar'''
        p[0] = p[1]
        return

    def p_scalar(self, p):
        '''scalar : string
                  | integer
                  | float
                  | bignum
                  | boolean'''
        p[0] = p[1]
        return

    def p_string(self, p):
        '''string : STRING'''
        p[0] = p[1][1:-1]
        return

    def p_integer(self, p):
        '''integer : INTEGER'''
        p[0] = int(p[1])
        return

    def p_float(self, p):
        '''float : FLOAT'''
        p[0] = float(p[1])
        return

    # Going to force the scientific notation bigums in to ints because that is
    # the only way they are used in the SavedVariables.lua file
    #
    def p_bignum(self, p):
        '''bignum : BIGNUM'''
        p[0] = int(float(p[1]))
        return

    def p_boolean(self, p):
        '''boolean : BOOLEAN'''
        if string.lower(p[1]) == "true":
            p[0] = True
        else:
            p[0] = False
        return
    
    def p_dictionary(self, p):
        '''dictionary : LBRACE keyvalues RBRACE
                      | LBRACE RBRACE
        '''
        if len(p) == 4:
            p[0] = dict(p[2])
        elif len(p) == 3:
            p[0] = {}
        return

    def p_keyvalues(self, p):
        '''keyvalues : keyvalue
                     | keyvalue COMMA
                     | keyvalue COMMA keyvalues'''
        if len(p) == 2 or len(p) == 3:
            p[0] = [ p[1] ]
        elif len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        return

    def p_keyvalue(self, p):
        '''keyvalue : LBRACK scalar RBRACK ASSIGN value'''
        p[0] = ( p[2], p[5] )
        return

    def p_error(self, p):
        while True:
            tok = yacc.token()
            if not tok or tok.type == 'RBRACE':
                break
        yacc.restart()

    ##
    ## And so ends the parser declaration
    ##
    ########################################################################

    ########################################################################
    #
    def __init__(self, output_dir = None):
        """This will initialize our lexer and parser and define the dictionary
        used to hold the results of our parsing.
        """

        # We dump our parser table in to the media top directory of the wowzer
        # app.. we can reverse engineer where that is from where this file is.
        #
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__) , "..", "..",
                                      "media")
            sys.stderr.write("SavedParser - parse tables will be in: %s " % \
                             output_dir)
            sys.stderr.flush()

        self.variables = {}
        self.lexer = lex.lex(module = self)
        self.parser = yacc.yacc(module = self, outputdir = output_dir)
        # self.parser = yacc.yacc(module = self, write_tables = 0)

        return

    ######################################################################
    #
    def process(self, data):
        """We are handed a string which contains the entire lua script we wish
        to parse. When this is done self.variables will be a dictionary which
        will have a key for every variable defined in the data we have parsed.

        One big assumption here to save time is that we are parsing a file that
        only has in it the data we care about!
        """
        self.lexer.input(data)
        self.parser.parse()
