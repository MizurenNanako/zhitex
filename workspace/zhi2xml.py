from json import loads as jloads
from re import sub as _sub
from typing import Dict, Tuple

from bs4 import BeautifulSoup as bsoup
from bs4 import ResultSet as rset
from bs4 import Tag as tag
from requests import get as rq_get


def from_url_to_xml(url: str) -> Tuple[str, Tuple[str, str, str]]:
    doc_main = bsoup(rq_get(url).content.replace(b'^', b'&amp;hat;'),
                     "html.parser") \
        .find('body', {'class': 'WhiteBg-body PostIndex-body'}) \
        .find('div', {'id': 'root'}) \
        .find('div', {'class': 'App'}) \
        .main \
        .find('div', {'class': 'Post-content'}) \
        .extract()
    doc_meta_json = jloads(doc_main.attrs['data-zop'])

    doc_article: tag = doc_main.article \
        .find('div', {'class': 'Post-RichTextContainer'}) \
        .div.div.div.extract()
    doc_article.name = 'article'
    doc_article.attrs = {}
    for node in doc_article.find_all(lambda tag: tag.has_attr('id')):
        node: tag
        node.insert(0, bsoup(
            f"<label>{node['id'].removeprefix('#')}</label>", 'html.parser')
        )
        del node['id']
    for node in doc_article.find_all('style'):
        node.decompose()
    for node in doc_article.find_all('figure'):
        node.attrs = {}
        imgsrc: str = node.noscript.img['src']
        node.insert(0, bsoup(
            f"<graphics>{imgsrc.split('/')[-1]}</graphics>", 'html.parser')
        )
        node.insert(0, bsoup(f"<imgurl>{imgsrc}</imgurl>", 'html.parser'))
        node.noscript.decompose()
        node.img.decompose()
    for node in doc_article.find_all(lambda tag:
                                     tag.name == 'a' and
                                     tag.has_attr('href')):
        node.name = 'href'
        node.attrs = {'ref': node['href'].removeprefix('#')}

# tex math determination

    for node in doc_article.find_all('span', {'class': 'ztext-math'}):
        node: tag
        node.name = 'xtex'
        node.string = node.string.removeprefix('\\[') \
            .removesuffix('\\]') \
            .replace('{align}', '{aligned}') \
            .replace('&hat;', '^')
        node.attrs = {}
        if node.string.find('\\\\') != -1 or \
           node.string.find('sum') != -1 or \
           node.string.find('prod') != -1 or \
           node.string.find('int') != -1 or \
                len(node.parent.contents) == 2:
            node.name = 'xtex-disp'
        else:
            node.name = 'xtex-inline'
            node.string = node.string.replace('\\frac', '\\dfrac')

# attr eliminate

    for node in doc_article.find_all(lambda tag:
                                     tag.has_attr('data-pid') or
                                     tag.name in
                                     [
                                         'p',
                                         'ol',
                                         'ul',
                                         'h2',
                                         'h3',
                                         'li',
                                         'sup',
                                         'span',
                                         'figrue',
                                     ]):
        node.attrs = {}

    return str(doc_article), (doc_meta_json['authorName'],
                              doc_meta_json['title'],
                              str(doc_meta_json['itemId']))


def _build_doc_tex(doc_xml, meta) -> str:
    doc_tex = doc_xml

    # Deal with Chinese misformat

    doc_tex = _sub(
        r'(</xtex-disp>(?:\s*<b>)?)\s*(?:,|:|\.|，|。|？|！|：)', '\g<1>', doc_tex)

    doc_tex = _sub('''<href ref="(.*?)">(.*?)</href>''',
                   '\\\href{\g<1>}{\g<2>}',
                   doc_tex) \
        .replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>') \
        .replace('#', '\\#').replace('\\\\', '\\\\\n') \
        .replace('&hat;', '\\char94') \
        .replace('<p>', ' ').replace('</p>', '\n\n') \
        .replace('<span>', ' ').replace('</span>', ' ') \
        .replace('<label>', '\\label{').replace('</label>', '}') \
        .replace('<xtex-inline>', '\\(').replace('</xtex-inline>', '\\)') \
        .replace('<xtex-disp>', '\n\\[\\begin{aligned}\n').replace('</xtex-disp>', '\n\\end{aligned}\\]\n') \
        .replace('<blockquote>', '\n\n\\begin{quote}\n').replace('</blockquote>', '\n\\end{quote}\n\n') \
        .replace('<figure>', '\n\n\\begin{figure}\n').replace('</figure>', '\\end{figure}\n\n') \
        .replace('<imgurl>', '%\\immediate\\write18{wget ').replace('</imgurl>', '}\n') \
        .replace('<graphics>', '%\\includegraphics{').replace('</graphics>', '}\n') \
        .replace('<b>', '\\textbf{').replace('</b>', '}') \
        .replace('<i>', '\\textit{').replace('</i>', '}') \
        .replace('<h2>', '\\section{').replace('</h2>', '}\n') \
        .replace('<h3>', '\\textbf{').replace('</h3>', '}\n\n') \
        .replace('<hr/>', '\n\n\n').replace('<br/>', '\n\n') \
        .replace('<ol>', '\n\\begin{enumerate}\n').replace('</ol>', '\\end{enumerate}\n') \
        .replace('<ul>', '\n\\begin{itemize}\n').replace('</ul>', '\\end{itemize}\n') \
        .replace('<li>', '\\item ').replace('</li>', '\n') \
        .replace('<sup>', '\\textsuperscript{').replace('</sup>', '}') \
        .replace('<article>', '\\begin{document}\n' + '\\begin{center}\n\t\\LARGE\\bfseries ' + meta[0] + ' \\quad ' + meta[1] + '\n\\end{center}\n\n').replace('</article>', '\n\\end{document}')

    return doc_tex


def build_tex(doc_xml, meta) -> str:
    prelude = \
        '''\\RequirePackage{silence}
\\WarningFilter{latexfont}{Size substitutions with differences}
\\WarningFilter{latexfont}{Font shape `U/rsfs}
\\documentclass[dvipsnames, svgnames, 12pt]{article}
\\PassOptionsToPackage{quiet}{fontspec}
\\usepackage[UTF8]{ctex}

\\usepackage{indentfirst}
\\setlength\\parindent{2.45em}

\\usepackage{fontspec}
\\setmainfont{Noto Serif CJK SC}

\\usepackage{tikz}
\\usetikzlibrary{calc}
\\usepackage{eso-pic}
\\AddToShipoutPictureBG{%
\\begin{tikzpicture}[overlay,remember picture]
\\draw[line width=0.6pt]
    ($ (current page.north west) + (0.6cm,-0.6cm) $)
    rectangle
    ($ (current page.south east) + (-0.6cm,0.6cm) $);
\\end{tikzpicture}}

\\usepackage{xcolor}
\\definecolor{c1}{HTML}{2752C9}
\\definecolor{c2}{RGB}{190,20,83}

\\usepackage[a4paper, top=28mm, bottom=28mm, left=15mm, right=15mm]{geometry}

\\usepackage{hyperref}
\\hypersetup{colorlinks,linktoc = section,linkcolor = c1,citecolor = c1}

\\usepackage{amsmath, amssymb, amsthm, amsfonts, amsrefs, mathrsfs, unicode-math, physics}

\\usepackage{cases}
\\usepackage{tabularray, float, appendix, lipsum}
\\usepackage{subfigure, graphicx, wrapfig}
\\usepackage{caption, subcaption}

\\usepackage{fancyhdr}
\\fancypagestyle{plain}{\\pagestyle{fancy}}
\\pagestyle{fancy}
''' + '\\lhead{\kaishu ' + meta[0] + '}\n\\rhead{\kaishu {' + meta[1] + '}}\n' + '''
\\cfoot{\\raisebox{-2em}{\\Large\\textbf{\\thepage}}}
\\setlength{\headheight}{13.6pt}
\\addtolength{\\topmargin}{-1.6pt}

\\usepackage{titlesec, titletoc}
\\titleformat{\\section}{\\Large\\heiti}{\\textbf{\\Large\\arabic{section}}}{1em}{}[]

\\allowdisplaybreaks[4]'''

    return prelude + _build_doc_tex(doc_xml, meta)
