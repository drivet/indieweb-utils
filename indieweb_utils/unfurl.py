import opengraph
from micawber.providers import bootstrap_noembed
from PIL import Image
import requests
from io import BytesIO
import mf2py
import mf2util


def elide(s, maxchars):
    if len(s) <= maxchars:
        return s
    else:
        return s[:maxchars-3] + '...'


def fetch_image_dimensions(result):
    if 'image' not in result or \
       ('image:width' in result and 'image:height' in result):
        return

    response = requests.get(result['image'])
    img = Image.open(BytesIO(response.content))
    result['image:width'] = img.width
    result['image:height'] = img.height


def fetch_mf2_result(url):
    parsed = mf2py.Parser(url=url).to_dict()
    if not parsed:
        return None

    entry = mf2util.interpret_entry(parsed, url, want_json=True)
    post_type = mf2util.post_type_discovery(parsed)
    print('ddd ' + mf2util.get_plain_text(entry.get('name')))
    print('fff ' + mf2util.get_plain)
    result = {}
    result['mf2'] = True
    result['type'] = 'mf2:' + post_type
    if 'name' in entry:
        result['title'] = entry['name']

    if 'summary' in entry:
        result['description'] = elide(entry['summary'], 500)
    elif 'content' in entry:
        result['description'] = elide(entry['content-plain'], 500)

    if 'url' in entry:
        result['url'] = entry['url']

    if 'author' in entry:
        result['author'] = entry['author']

    if 'featured' in entry:
        result['image'] = entry['featured']
    elif 'photo' in entry:
        result['image'] = entry['photo']

    fetch_image_dimensions(result)

    return result


def fetch_og_result(url):
    result = opengraph.OpenGraph(url=url)
    if result:
        fetch_image_dimensions(result)
        return result
    return None


class PreviewGenerator(object):
    def __init__(self):
        self.providers = None

    def initialize(self):
        self.providers = []
        self.providers.append(bootstrap_noembed())

    def fetch_oembed_result(self, url):
        if not self.providers:
            self.initialize()

        for p in self.providers:
            result = p.extract(url)
            if result[1]:
                items = result[1].items()
                return list(items)[0][1]

    def preview(self, url):
        result = self.fetch_oembed_result(url)
        if result:
            return result

        mf2_result = fetch_mf2_result(url)
        if mf2_result and 'image:width' in mf2_result and \
           int(mf2_result['image:width']) > 300:
            # mf2 has a large image, don't bother with og
            return mf2_result

        # mf2 has small or no photo, try og
        og_result = fetch_og_result(url)
        if mf2_result is None or ('image:width' in og_result and
                                  int(og_result['image:width']) > 300):
            # og has larger photo (or there's no mf2), prefer og
            return og_result

        print('gggggg ' + str(mf2_result))
        return mf2_result
