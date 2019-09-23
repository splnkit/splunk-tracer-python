"""Demonstrates a Trace distributed across multiple machines.

A SpanContext's text representation is stored in the headers of an HTTP request.

Runs two threads, starts a Trace in the client and passes the SpanContext to the server.
"""

import argparse
import errno
import socket
import sys
import threading

try:
    # For Python 3.0 and later
    from urllib.request import (
        Request,
        urlopen,
    )
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    # Fall back to Python 2
    from urllib2 import (
        Request,
        urlopen,
    )
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import opentracing
import opentracing.ext.tags
import splunktracing


class RemoteHandler(BaseHTTPRequestHandler):
    """This handler receives the request from the client.
    """

    def do_GET(self):
        server_span = before_answering_request(self, opentracing.tracer)
        with opentracing.tracer.scope_manager.activate(server_span, True):
            server_span.log_event('request received', self.path)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Hello World!".encode("utf-8"))

            server_span.log_event('prepared response', self.path)


def before_sending_request(request):
    """Context manager creates Span and encodes the span's SpanContext into request.
    """
    span = opentracing.tracer.start_span('Sending request')
    span.set_tag('server.http.url', request.get_full_url())
    try:
        # Python 2
        host = request.get_host()
    except:
        # Python 3
        host = request.host

    if host:
        span.set_tag(opentracing.ext.tags.PEER_HOST_IPV4, host)

    carrier_dict = {}
    span.tracer.inject(span.context, opentracing.Format.HTTP_HEADERS, carrier_dict)
    for k, v in carrier_dict.items():
        request.add_header(k, v)
    return span


def before_answering_request(handler, tracer):
    """Context manager creates a Span, using SpanContext encoded in handler if possible.
    """
    operation = 'handle_request:' + handler.path
    carrier_dict = {}
    for k, v in handler.headers.items():
        carrier_dict[k] = v
    extracted_context = tracer.extract(opentracing.Format.HTTP_HEADERS, carrier_dict)

    span = None
    if extracted_context:
        span = tracer.start_span(
            operation_name=operation,
            child_of=extracted_context)
    else:
        print('ERROR: Context missing, starting new trace')
        global _exit_code
        _exit_code = errno.ENOMSG
        span = tracer.start_span(operation_name=operation)
        headers = ', '.join({k + '=' + v for k, v in handler.headers.items()})
        span.log_event('extract_failed', headers)
        print('Could not extract context from http headers: ' + headers)

    host, port = handler.client_address
    if host:
        span.set_tag(opentracing.ext.tags.PEER_HOST_IPV4, host)
    if port:
        span.set_tag(opentracing.ext.tags.PEER_PORT, str(port))

    return span


def pick_unused_port():
    """ Since we don't reserve the port, there's a chance it'll get grabed, but that's unlikely.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def splunk_tracer_from_args():
    """Initializes splunk tracer from the commandline args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Your Splunk HEC token.',
                        default='{your_access_token}')
    parser.add_argument('--host', help='The Splunk HEC host to contact.',
                        default='127.0.0.1')
    parser.add_argument('--port', help='The Splunk HEC port.',
                        type=int, default=8088)
    parser.add_argument('--no_tls', help='Disable TLS for reporting',
                        dest="no_tls", action='store_true')
    parser.add_argument('--component_name', help='The Splunk component name',
                        default='TrivialExample')
    args = parser.parse_args()

    if args.no_tls:
        collector_encryption = 'none'
    else:
        collector_encryption = 'tls'

    return lightstep.Tracer(
        component_name=args.component_name,
        access_token=args.token,
        collector_host=args.host,
        collector_port=args.port,
        collector_encryption=collector_encryption,
    )


if __name__ == '__main__':
    with splunk_tracer_from_args() as tracer:
        opentracing.tracer = tracer
        global _exit_code
        _exit_code = 0

        # Create a web server and define the handler to manage the incoming request
        port_number = pick_unused_port()
        server = HTTPServer(('', port_number), RemoteHandler)

        try:
            # Run the server in a separate thread.
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()
            print('Started httpserver on port ', port_number)

            # Prepare request in the client
            url = 'http://localhost:{}'.format(port_number)
            request = Request(url)
            client_span = before_sending_request(request)
            with opentracing.tracer.scope_manager.activate(client_span, True):
                client_span.log_event('sending request', url)

                # Send request to server
                response = urlopen(request)

                response_body = response.read()
                client_span.log_event('server returned', {
                    "code": response.code,
                    "body": response_body,
                })

            print('Server returned ' + str(response.code) + ': ' + str(response_body))

            sys.exit(_exit_code)

        finally:
            server.shutdown()
