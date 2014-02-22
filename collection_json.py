from __future__ import absolute_import, unicode_literals
import json


__all__ = ['Collection']
__version__ = '0.0.1dev'


class BaseObject(object):

    def __eq__(self, other):
        """Return True if both instances are equivalent."""
        return (type(self) == type(other) and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        """Return True if both instances are not equivalent."""
        return (type(self) != type(other) or
                self.__dict__ != other.__dict__)


class Collection(BaseObject):
    @staticmethod
    def from_json(data):
        """Return a Collection instance.

        Raises `ValueError` when no valid document is provided.

        """
        try:
            data = json.loads(data)
            kwargs = data.get('collection')
            if not kwargs:
                raise ValueError
        except ValueError:
            raise ValueError('Not a valid Collection+JSON document.')

        collection = Collection(**kwargs)
        return collection

    def __init__(self, version='1.0', href=None, links=None, items=None,
                 queries=None, template=None, error=None):
        self.version = version
        self.href = href

        if isinstance(error, dict):
            error = Error(**error)
        self.error = error

        if isinstance(template, dict):
            template = Template(**template)
        self.template = template

        if items is None:
            items = []
        self.items = Array(Item, 'items', items)

        if links is None:
            links = []
        self.links = Array(Link, 'links', links)

        if queries is None:
            queries = []
        self.queries = Array(Query, 'queries', queries)

    def to_dict(self):
        output = {
            'collection': {
                'version': self.version,
                'href': self.href,
            }
        }
        if self.links:
            output['collection'].update(self.links.to_dict())
        if self.items:
            output['collection'].update(self.items.to_dict())
        if self.queries:
            output['collection'].update(self.queries.to_dict())
        if self.template:
            output['collection'].update(self.template.to_dict())
        if self.error:
            output['collection'].update(self.error.to_dict())
        return output


class Error(BaseObject):

    def __init__(self, code=None, message=None, title=None):
        self.code = code
        self.message = message
        self.title = title

    def to_dict(self):
        """Return a dictionary representing the Error instance."""
        output = {
            'error': {
            }
        }
        if self.code:
            output['error']['code'] = self.code
        if self.message:
            output['error']['message'] = self.message
        if self.title:
            output['error']['title'] = self.title
        return output


class Template(BaseObject):
    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = Array(Data, 'data', data)

    def to_dict(self):
        return {
            'template': self.data.to_dict()
        }


class Array(BaseObject, list):
    def __init__(self, item_class, collection_name, items):
        self.item_class = item_class
        self.collection_name = collection_name
        super(Array, self).__init__(self._build_items(items))

    def _build_items(self, items):
        result = []
        for item in items:
            if isinstance(item, self.item_class):
                result.append(item)
            elif isinstance(item, dict):
                result.append(self.item_class(**item))
            else:
                raise ValueError("Invalid value for %s: %r" % (
                    self.item_class.__name__, item))
        return result

    def __eq__(self, other):
        """Return True if both instances are equivalent."""
        return (super(Array, self).__eq__(other) and
                list.__eq__(self, other))

    def __ne__(self, other):
        """Return True if both instances are not equivalent."""
        return (super(Array, self).__ne__(other) or
                list.__ne__(self, other))

    def to_dict(self):
        return {
            self.collection_name: [item.to_dict() for item in self]
        }


class Item(BaseObject):
    def __init__(self, href=None, data=None, links=None):
        self.href = href
        if data is None:
            data = []
        self.data = Array(Data, 'data', data)
        if links is None:
            links = []
        self.links = Array(Link, 'links', links)

    def __repr__(self):
        return '<Item>'

    def to_dict(self):
        output = {}
        if self.href:
            output['href'] = self.href
        if self.data:
            output.update(self.data.to_dict())
        if self.links:
            output.update(self.links.to_dict())
        return output


class Data(BaseObject):
    def __init__(self, name, value=None, prompt=None):
        self.name = name
        self.value = value
        self.prompt = prompt

    def __repr__(self):
        return "<Data: %s>" % self.name

    def to_dict(self):
        output = {
            'name': self.name
        }
        if self.value is not None:
            output['value'] = self.value
        if self.prompt is not None:
            output['prompt'] = self.prompt
        return output


class Query(BaseObject):
    def __init__(self, href, rel, name=None, prompt=None, data=None):
        self.href = href
        self.rel = rel
        self.name = name
        self.prompt = prompt
        if data is None:
            data = []
        self.data = Array(Data, 'data', data)

    def __repr__(self):
        data = "rel='%s'" % self.rel
        if self.name:
            data += " name='%s'" % self.name
        return "<Query: %s>" % data

    def to_dict(self):
        output = {
            'href': self.href,
            'rel': self.rel,
        }
        if self.name is not None:
            output['name'] = self.name
        if self.prompt is not None:
            output['prompt'] = self.prompt
        if len(self.data):
            output.update(self.data.to_dict())
        return output


class Link(BaseObject):
    def __init__(self, href, rel, name=None, render=None, prompt=None):
        self.href = href
        self.rel = rel
        self.name = name
        self.render = render
        self.prompt = prompt

    def __repr__(self):
        data = "rel='%s'" % self.rel
        if self.name:
            data += " name='%s'" % self.name
        if self.render:
            data += " render='%s'" % self.render
        return "<Link: %s>" % data

    def to_dict(self):
        output = {
            'href': self.href,
            'rel': self.rel,
        }
        if self.name is not None:
            output['name'] = self.name
        if self.render is not None:
            output['render'] = self.render
        if self.prompt is not None:
            output['prompt'] = self.prompt
        return output