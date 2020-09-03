import asyncio
import time

import pdfkit

test_url = 'http://10.0.32.28:7001/memberAnalysis/groups'


def get(get_name):
    # url = get_name
    # 文件路径
    # to_file = 'out.pdf'

    options = {
        'javascript-delay': '5000'
    }
    pdfkit.from_umrl(get_name, 'out.pdf', options=options)
    print('已生成pdf文件')


get(test_url)
