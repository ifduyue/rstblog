# -*- coding: utf-8 -*-
"""
    rstblog.modules.pygments
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Adds support for pygments.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from rstblog.signals import before_file_processed, \
     before_build_finished

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers import PythonLexer, PythonConsoleLexer, CLexer, TextLexer, RstLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

html_formatter = None


class CodeBlock(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
        'linenostep': directives.positive_int,
        'emphasize-lines': directives.unchanged_required,
        'hl_lines': directives.unchanged_required,
        'noclasses': directives.unchanged,
    }
    lexers = dict(
        none = TextLexer(),
        python = PythonLexer(),
        pycon = PythonConsoleLexer(),
        pycon3 = PythonConsoleLexer(python3=True),
        rest = RstLexer(),
        c = CLexer(),
    )

    def run(self):
        code = u'\n'.join(self.content)
        lang = self.arguments[0].strip()
        linenos = 'linenos' in self.options
        linespec = self.options.get('emphasize-lines') or self.options.get('hl_lines') or ''
        linenostep = self.options.get('linenostep')
        noclasses = self.options.get('noclasses')
        if 'noclasses' in self.options:
            if noclasses.lower() in ('y', 'yes', '1', 'on', 'true', ''):
                noclasses = True
            elif noclasses.lower() in ('n', 'no', '0', 'off', 'false'):
                noclasses = False
        if linespec:
            try:
                nlines = len(self.content)
                hl_lines = [x+1 for x in self.parselinenos(linespec, nlines)]
            except ValueError, err:
                document = self.state.document
                return [document.reporter.warning(str(err), line=self.lineno)]
        else:
            hl_lines = []
        kwargs = {
            'hl_lines': hl_lines,
            'linenos': linenos,
            'language': lang,
        }
        if noclasses in (True, False):
            kwargs['noclasses'] = noclasses
        if linenostep:
            kwargs['linenostep'] = linenostep
        try:
            if lang in self.lexers:
                lexer = self.lexers[lang]
            elif lang == 'guess':
                lexer = guess_lexer(code)
            else:
                lexer = get_lexer_by_name(lang)
        except ValueError:
            lexer = TextLexer()
        formatter = html_formatter(**kwargs)
        formatted = highlight(code, lexer, formatter)
        return [nodes.raw('', formatted, format='html')]

    def parselinenos(self, spec, total):
        """Parse a line number spec (such as "1,2,4-6") and return a list of
        wanted line numbers.
        """
        items = list()
        parts = spec.split(',')
        for part in parts:
            try:
                begend = part.strip().split('-')
                if len(begend) > 2:
                    raise ValueError
                if len(begend) == 1:
                    items.append(int(begend[0])-1)
                else:
                    start = (begend[0] == '') and 0 or int(begend[0])-1
                    end = (begend[1] == '') and total or int(begend[1])
                    items.extend(xrange(start, end))
            except Exception:
                raise ValueError('invalid line number spec: %r' % spec)
        return items

def inject_stylesheet(context, **kwargs):
    context.add_stylesheet('_pygments.css')


def write_stylesheet(builder, **kwargs):
    with builder.open_static_file('_pygments.css', 'w') as f:
        f.write(html_formatter.get_style_defs())


def setup(builder):
    global html_formatter
    style = get_style_by_name(builder.config.root_get('modules.pygments.style'))
    noclasses = builder.config.root_get('modules.pygments.noclasses', False)
    class formatter_partial:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.get_style_defs = HtmlFormatter(**self.kwargs).get_style_defs
        def __call__(self, **kwargs):
            kw = self.kwargs.copy()
            kw.update(kwargs)
            return HtmlFormatter(**kw)
    html_formatter = formatter_partial(style=style, noclasses=noclasses)
    directives.register_directive('code-block', CodeBlock)
    directives.register_directive('sourcecode', CodeBlock)
    before_file_processed.connect(inject_stylesheet)
    before_build_finished.connect(write_stylesheet)
