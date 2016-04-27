import datetime
from inspect import getframeinfo, stack
import os
import pprint
from django.http import HttpResponse
from django.utils.html import escape


class FrontendLogger(object):
    entities = []
    request = None

    def __init__(self, request=None):
        self.entities = []
        self.request = request

    def log(self, entity):
        caller = getframeinfo(stack()[1][0])
        self.entities.append((datetime.datetime.now().time(), caller.filename, caller.lineno, entity))

    def html(self):
        if not self.request:
            raise NotImplementedError('You have to setup request in constructor or response')
        html = u'<html><head><title>Debug: %s</title></head>' % self.request.get_full_path()
        html += u'<body><table>'
        for e in self.entities:
            html += u'<tr><td>%(time)s</td>' \
                    u'<td>%(file)s</td>' \
                    u'<td>%(line)s</td>' \
                    u'<td><pre>%(entity)s</pre></td>' \
                    u'</tr>\n' % {'time': e[0],
                                  'file': e[1],
                                  'line': e[2],
                                  'entity': escape(pprint.pformat(e[3]).decode('utf-8'))
                                  }
        html += u'</table></html>'
        return html

    def response(self, request=None):
        if request:
            self.request = request
        return HttpResponse(self.html())


class RequestLogger(FrontendLogger):
    entities_per_request_id = {}

    def __init__(self):
        self.request = None
        self.entities_per_request_id = {}

    def _set_entities(self, x):
        self.entities_per_request_id[os.environ.get('REQUEST_LOG_ID')] = x

    def _get_entities(self):
        REQUEST_LOG_ID = os.environ.get('REQUEST_LOG_ID')
        try:
            return self.entities_per_request_id[REQUEST_LOG_ID]
        except KeyError:
            self._set_entities([])
            return self.entities_per_request_id[REQUEST_LOG_ID]

    def response(self, *args, **kwargs):
        resp = super(RequestLogger, self).response(*args, **kwargs)
        REQUEST_LOG_ID = os.environ.get('REQUEST_LOG_ID')
        del self.entities_per_request_id[REQUEST_LOG_ID]
        self.request = None
        return resp

    entities = property(_get_entities, _set_entities)


logger = RequestLogger()
