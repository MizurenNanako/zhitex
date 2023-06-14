# Usage

Have a peek at the example `main.py`:

```py
from workspace.zhi2xml import from_url_to_xml, build_tex

urls = [
    # "list the urls which"
    # "you want to download"
    # "here ... for example:"
    "https://zhuanlan.zhihu.com/p/331738362",
    "https://zhuanlan.zhihu.com/p/359082678",
]

for url in urls:
    doc_xml, meta = from_url_to_xml(url)
    basename = '_'.join(meta).replace('/', '_').replace(' ', '_')
    print(basename)
    with open(file= 'xml/' + basename + '.xml', mode= 'w') as f:
        f.write(doc_xml)
    with open(file= 'tex/' + basename + '.tex', mode= 'w') as f:
        f.write(build_tex(doc_xml, meta))

```

Now run the `main.py` script and check generated `.tex` files in `tex/` directory, they are almost ready to compile.

> PS: If any picture occurred in the original posts, corresponding `\figure{}` block and `\includegraphic{}` block will be generated but commented. Download all these pictures according to the comment then uncomment these blocks to revive figures.
> PPS: html `<table>` hasn't been supported yet.
