import sys
import re

import pygments

from pygments.lexers import get_lexer_by_name
from pygments.formatter import Formatter
from pygments.token import Token


ALL_WHITESPACE = re.compile(r'^\s+$')


# pasted from the docs
class NullFormatter(Formatter):
    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            outfile.write(value)


class MyFormatter(Formatter):
    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            if ttype is Token.Text and ALL_WHITESPACE.match(value):
                pass
            else:
                outfile.write('{}<{}>\n'.format(ttype, value))


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    #formatter = NullFormatter(linenos=False)
    formatter = MyFormatter()
    result = pygments.highlight(unformatted_code, lexer, formatter)

    print(result)
