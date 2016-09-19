#-*- coding: utf-8 -*-

import urllib.request
from bs4 import BeautifulSoup
import re
import json
import os
import pdfkit

class Chapter:

    def __init__(self, link):
        self.link = link
        link_components = urllib.parse.urlparse(link)
        relativepath = link_components.path
        self.name = relativepath.replace('/', '')
        self.path = os.getcwd() + relativepath
        self.__createdownloadfolder()
        self.__getimglinks()
        self.pdf = self.create_comic()

    def __createdownloadfolder(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def __getimglinks(self):
        req = urllib.request.Request(self.link)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0')
        page = urllib.request.urlopen(req)
        html = page.read().decode(encoding='UTF-8')
        soup = BeautifulSoup(str(html), 'html.parser')
        script, = soup.find_all("script", text=re.compile("rm_h.init"))
        script = str(script)
        linksinhtml, = re.findall(r'\[\[.*\]\]', script)
        linksinjson = str(linksinhtml).replace("'", '"')
        links = json.loads(linksinjson)
        self.meta = [{
                    'url': "{http}{auto}{number}".format(http=link[1], auto=link[0], number=link[2]),
                    'width': link[3],
                    'height': link[4]
                } for link in links]
        return self.meta

    def download(self):
        for link in self.meta:
            *_, filename = link['url'].split('/')
            urllib.request.urlretrieve(link['url'], "{path}/{filename}".format(path=self.path, filename=filename))

    def create_comic(self):
        html = """<html>
                    <body>
                        {pages}
                    </body>
                </html>"""
        # links = os.listdir(path)
        pages = ""
        for link in self.meta:
            page = '<img src="{path}"></img>'.format(path=link['url'])
            pages += page

        with open('{path}/{filename}.html'.format(path=self.path, filename=self.name), 'w', encoding='utf-8') as file:
            file.write(html.format(pages=pages))

        pdfkit.from_file('{path}/{filename}.html'.format(path=self.path, filename=self.name), '{path}/{filename}.pdf'.format(path=self.path, filename=self.name), options={'page-size': 'Letter'})
        return '{path}/{filename}.pdf'.format(path=self.path, filename=self.name)

    def getPDF(self):
        return self.pdf

    def __del(self):
        files = os.listdir(self.path)
        for file in files:
            os.remove("{path}/{filename}".format(path=self.path, filename=file))
        os.rmdir(self.path)