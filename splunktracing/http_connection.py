"""Connection class establishes HTTP connection with server.
    Utilized to send Proto Report Requests.
"""
import threading
import requests
# import zlib
# from StringIO import StringIO
# import gzip

class _HTTPConnection(object):
    """Instances of _Connection are used to establish a connection to the
    server via HTTP protocol.
    """
    def __init__(self, collector_url, timeout_seconds):
        self._collector_url = collector_url
        self._lock = threading.Lock()
        self.ready = True
        self._timeout_seconds = timeout_seconds

    def open(self):
        """Establish HTTP connection to the server."""
        pass

    # May throw an Exception on failure.
    def report(self, *args, **kwargs):
        """Report to the server."""
        auth = args[0]
        report = args[1]
        print self._collector_url
        with self._lock:
            try:
                headers = {# "Content-Type": "application/text",
#                           "Content-Encoding": 'gzip',
#                           "Accept": "application/json",
                           "Authorization": "Splunk %s" % auth}
                # s = StringIO()
                # g = gzip.GzipFile(fileobj=s, mode='w')
                # g.write(report.serialize_to_string())
                # g.close()
                r = requests.post(
                    self._collector_url,
                    headers=headers,
                    data=report.serialize_to_string(),  # zlib.compress(report.serialize_to_string()),
                    timeout=self._timeout_seconds,
                    verify=False)
                print report.serialize_to_string()
                resp = r.content
                return resp
            except requests.exceptions.RequestException as err:
                raise err

    def close(self):
        """Close HTTP connection to the server."""
        self.ready = False
        pass
