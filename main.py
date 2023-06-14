from workspace.zhi2xml import from_url_to_xml, build_tex

urls = [
    # "https://zhuanlan.zhihu.com/p/592725113",
    # "https://zhuanlan.zhihu.com/p/594303459",
    # "https://zhuanlan.zhihu.com/p/596162640",
    # "https://zhuanlan.zhihu.com/p/597868376",
    # "https://zhuanlan.zhihu.com/p/58866876",
    # "https://zhuanlan.zhihu.com/p/61473751",
    # "https://zhuanlan.zhihu.com/p/59768829",
    # "https://zhuanlan.zhihu.com/p/331738362",
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
