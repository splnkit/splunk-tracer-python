"""Connection class establishes HTTP connection with server.
    Utilized to send Proto Report Requests.
"""
import threading
import requests
import zlib


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
        with self._lock:
            try:
                data = report.serialize_to_string()
                if len(data) > 0:
                    gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
                    payload = gzip_compress.compress(data) + gzip_compress.flush()
                    headers = {"Content-Type": "application/json",
                               "Content-Encoding": 'gzip',
                               "Content-Length": str(len(payload)),
                               "Authorization": "Splunk %s" % auth}
                    r = requests.post(
                        self._collector_url,
                        headers=headers,
                        data=payload,
                        timeout=self._timeout_seconds)
                    resp = r.content
                    return resp
            except requests.exceptions.RequestException as err:
                raise err

    def close(self):
        """Close HTTP connection to the server."""
        self.ready = False
        pass
