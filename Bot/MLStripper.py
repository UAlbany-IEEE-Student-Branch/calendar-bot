from abc import ABC
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser, ABC):
    """A child class of HTMLParser that serves to take in uncompiled HTML code and remove it, returning the relevant
     information"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
