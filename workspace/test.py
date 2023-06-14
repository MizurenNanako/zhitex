from zhi2xml import from_url_to_xml

url = '''https://zhuanlan.zhihu.com/p/365457613'''
# url = '''https://zhuanlan.zhihu.com/p/593236864'''

doc_xml, meta = from_url_to_xml(url)

from re import sub as _sub

doc_tex = doc_xml.replace('<p>', '\\text{').replace('</p>', '\\}') \
    .replace('<blockquote>', '\n\\begin{quote}\n').replace('</blockquote>', '\n\\end{quote}\n}') \
    .replace('<xtex>', '\n$$\n').replace('</xtex>', '\n$$\n')

with open('../'+'_'.join(meta) + '.tex', 'w') as f:
    f.write(doc_tex)