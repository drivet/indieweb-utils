import opengraph
from micawber.providers import bootstrap_noembed


class PreviewGenerator(object):
    def __init__(self):
        self.providers = None

    def initialize(self):
        self.providers = []
        self.providers.append(bootstrap_noembed())

    def preview(self, url):
        if not self.providers:
            self.initialize()
        for p in self.providers:
            result = p.extract(url)
            if result[1]:
                items = result[1].items()
                return list(items)[0][1]

        result = opengraph.OpenGraph(url=url)
        if result:
            return result
        return None
