"""Simple example showing several generations of spans in a trace.
"""
import argparse
import sys
import time
import traceback

import opentracing
import splunktracing.tracer

def sleep_dot():
    """Short sleep and writes a dot to the STDOUT.
    """
    time.sleep(0.05)
    sys.stdout.write('.')
    sys.stdout.flush()


def add_spans():
    """Calls the opentracing API, doesn't use any LightStep-specific code.
    """
    with opentracing.tracer.start_active_span('trivial/initial_request') as parent_scope:
        parent_scope.span.set_tag('url', 'localhost')
        sleep_dot()
        parent_scope.span.log_event('All good here!', payload={'N': 42, 'pi': 3.14, 'abc': 'xyz'})
        parent_scope.span.log_kv({'foo': 'bar', 'int': 42, 'float': 4.2, 'bool': True, 'obj': {'blargh': 'hmm', 'whee': 4324}})
        parent_scope.span.set_tag('span_type', 'parent')
        parent_scope.span.set_tag('int_tag', 5)
        parent_scope.span.set_tag('unicode_val', u'non-ascii: \u200b')
        parent_scope.span.set_tag('bool_tag', True)
        parent_scope.span.set_baggage_item('checked', 'baggage')
        sleep_dot()

        # This is how you would represent starting work locally.
        with opentracing.tracer.start_active_span('trivial/child_request') as child_scope:
            child_scope.span.set_tag('span_type', 'child')
            # Pretend there was an error
            child_scope.span.set_tag('error', True)
            child_scope.span.log_event('Uh Oh!', payload={'stacktrace': traceback.extract_stack()})
            sleep_dot()

            # Play with the propagation APIs... this is not IPC and thus not
            # where they're intended to be used.
            text_carrier = {}
            opentracing.tracer.inject(child_scope.span.context, opentracing.Format.TEXT_MAP, text_carrier)

            span_context = opentracing.tracer.extract(opentracing.Format.TEXT_MAP, text_carrier)
            with opentracing.tracer.start_active_span(
                'trivial/remote_span',
                child_of=span_context) as remote_scope:
                    remote_scope.span.log_event('Remote!')
                    remote_scope.span.set_tag('span_type', 'remote')
                    sleep_dot()

def splunk_tracer_from_args():
    """Initializes splunk tracer from the commandline args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Your Splunk HEC token.',
                        default='{your_hec_token}')
    parser.add_argument('--host', help='The Splunk HEC endpoint to contact.',
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

    return splunktracing.Tracer(
            component_name=args.component_name,
            access_token=args.token,
            collector_host=args.host,
            collector_port=args.port,
            verbosity=1,
            collector_encryption=collector_encryption)


if __name__ == '__main__':
    print('Hello ')

    # Use LightStep's opentracing implementation
    with splunk_tracer_from_args() as tracer:
        opentracing.tracer = tracer
        add_spans()

    print(' World!')
