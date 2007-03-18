"""
PyTextile is a Python port of Textile, Dean Allen's Humane Web Text Generator.
It supports all the features of version 2 and some more.
See: http://dealmeida.net/projects/textile/ for details.

Install textile.py in a python searchable path, copy this file to your
pyblosxom Pyblosxom/plugins directory, and you're ready to go.  Files with a
.txtl extension will be marked up as textile. 

If you want PyTextile to syntax-highlight Python snippets, you need the 
htmlizer module from twisted.python. If you don't have Twisted installed, you
can download htmlizer.py from http://dealmeida.net/code/htmlizer.py.txt.

To highlight Python code, use the "blockcode" signature, specifying the 
language as Python:

    bc[python].. from Pyblosxom import tools
    from textile import textile

    pass

Keywords in the code will receive <span> tags, which should be customized
using CSS. This is the CSS I use:

    .py-src-keyword {
        color: blue;
        font-weight: bold;
    }

    .py-src-triple {
        color: red;
    }

    .py-src-comment {
        color: green;
        font-style: italic;
    }

    .py-src-identifier {
        color: teal;
        font-weight: bold;
    }

    .py-src-string {
        color: purple;
    }

    .py-src-op {
        color: #333;
        font-weight: bold;
    }

PyTextile can optionally validate the generated XHTML, using either Mx.Tidy
(http://www.egenix.com/files/python/mxTidy.html) or uTidyLib
(http://utidylib.sourceforge.net/). Both depend on TidyLib. To enable the
validation, add the following to your config file:

    py['txtl_validate'] = 1

It's also a good thing to set your encoding and the desired output:

    py['txtl_encoding'] = 'latin-1'
    py['txtl_output']   = 'ascii'

You can configure this as your default preformatter for .txt files by
configuring it in your config file as follows::

    py['parser'] = 'textile'

or in your blosxom .txt file entries, place a '#parser textile' line after the
title of your blog::

    My Little Blog Entry
    #parser textile
    My main story...
"""

__version__ = '$Id$'
__author__ = 'Roberto De Almeida <roberto@dealmeida.net>'

import re
import string

import textile


def plot_sparkline(match):
    """Returns a sparkline image as a data: URI.
    
    The source data is a list of values between 0 and 100. Values greater
    than 50 are displayed in red, otherwise they are displayed in green.

    http://bitworking.org/news/Sparklines_in_data_URIs_in_Python
    """
    import Image, ImageDraw
    import cStringIO
    import urllib

    results0 = results = match.group('results')
    results = results.split(',')
    try:
        results = [float(i) for i in results]
    except ValueError:
        return ''

    span = min(results), max(results)

    im = Image.new("RGB", (len(results)*2, 15), 'white')
    draw = ImageDraw.Draw(im)
    for (r, i) in zip(results, range(0, len(results)*2, 2)):
        #color = (r > 50) and "red" or "green"
        #draw.line((i, im.size[1]-r/10-4, i, (im.size[1]-r/10)), fill=color)
        color = (r > 0) and "blue" or "red"
        draw.line((i, im.size[1]*(r-span[1])//(span[0]-span[1]), i, im.size[1]*(-span[1])//(span[0]-span[1])), fill=color)
    del draw

    f = cStringIO.StringIO()
    im.save(f, "PNG")
    data = urllib.quote(f.getvalue())
    tag = '<img class="sparkline" src="data:image/png,%s" alt="%s" />' % (data, results0)

    return tag


class SpecialTextiler(textile.Textiler):
    def __init__(self, text=''):
        textile.Textiler.__init__(self, text)

        self.signatures.append((r'^\014', self.ctrll))
        self.signatures.append((r'''^rot13                   # ROT13 signature
                                    %(battr)s                # ROT13 attributes
                                    (?P<dot>\.)              # .
                                    (?P<extend>\.)?          # Extended ROT13 denoted by a second dot
                                    \s                       # whitespace

                                    (?P<text>.*)             # text
                                 ''' % self.res, self.rot13))
        self.signatures.insert(0, (r'''^<python>(?P<text>.*)</python>$''', self.python))

    def ctrll(self):
        return '\014'

    def rot13(self, text, parameters=None, attributes=None, clear=None):
        """ROT13 function."""
        table = string.maketrans('nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM',
                                 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

        text = string.translate(text, table)

        return self.paragraph(text, parameters, attributes, clear)

    def python(self, text):
        parameters = '[python]'
        return self.bc(text, parameters)

    def qtags(self, text):
        """Foobar docstring.

        ---
        Otherwise it'll break pyTextile. Stupid me.
        """
        text = re.sub(r'\{\{(?P<results>.*?)\}\}', plot_sparkline, text)

        # Original qtags method.
        return textile.Textiler.qtags(self, text)

def to_html(text):
        parser = SpecialTextiler(text)
        return parser.process()

def name():
    return "textile"

def quote(text,url):
    return "bq. %s\n\n" %  text

