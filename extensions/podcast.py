#!/usr/bin/env python

# Tool for retrieving a podcast listing and dumping its contents to a
# directory. This directory can then be browsed by sippy as usual.

import xml.dom.minidom as minidom
import os, sys, time, urllib2

class Item(object):
    def __init__(self, title, date, url):
        self.title = title
        self.date = time.strptime(date[:-6], '%a, %d %b %Y %H:%M:%S')
        self.url = url

def get_items(url):
    def get_child(node, name):
        return filter(lambda x: x.localName == name, node.childNodes)[0]
    def get_data(node, name):
        return get_child(node, name).childNodes[0].data

    resp = urllib2.urlopen(url)
    xml = minidom.parse(resp)
    for item in xml.getElementsByTagName('item'):
        yield Item(get_data(item, 'title'),
                   get_data(item, 'pubDate'),
                   get_child(item, 'enclosure').attributes['url'].nodeValue)

def main():
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage: %s url directory' % sys.argv[0]
        return -1

    try:
        for i in get_items(sys.argv[1]):
            filename = '%(time)s - %(title)s.pls' % {
                'time':time.strftime('%Y-%m-%d', i.date),
                'title':i.title.replace('/', ''),
            }
            path = os.path.join(sys.argv[2], filename)
            if os.path.exists(path):
                continue
            with open(path, 'w') as f:
                f.write(i.url)
    except Exception as inst:
        print >>sys.stderr, 'Failed: %s' % str(inst)
        return -1

    return 0

if __name__ == '__main__':
    sys.exit(main())
