import socket
import sys

from . import util
from . import version as tracer_version

from splunktracing.collector import ReportRequest, Span, Reporter, SpanContext, Timestamp
from splunktracing.converter import Converter


class HttpConverter(Converter):


    def create_runtime(self, component_name, tags, guid):
        if component_name is None:
            component_name = sys.argv[0]

        host_name = socket.gethostname()
        ip_address = util.local_ip()
        python_version = '.'.join(map(str, sys.version_info[0:3]))

        if tags is None:
            tags = {}
        tracer_tags = tags.copy()

        tracer_tags.update({
            'tracer_platform': 'python',
            'tracer_platform_version': python_version,
            'tracer_version': tracer_version.SPLUNK_PYTHON_TRACER_VERSION,
            'component_name': component_name,
            'guid': util._id_to_hex(guid),
            'device': host_name,
            'ip_address': ip_address
        })

        # Convert tracer_tags to a list of KeyValue pairs.
        runtime_attrs = tracer_tags

        return Reporter(reporter_id=guid, tags=runtime_attrs)

    def create_span_record(self, span, guid):
        if span.parent_id:
            pid = util._id_to_hex(int(span.parent_id))
        else:
            pid = span.parent_id
        span_context = SpanContext(trace_id=util._id_to_hex(int(span.context.trace_id)),
                                   span_id=util._id_to_hex(int(span.context.span_id)),
                                   parent_id=pid)
        seconds, nanos = util._time_to_seconds_nanos(span.start_time)
        span_record = Span(span_context=span_context,
                           operation_name=util._coerce_str(span.operation_name),
                           start_timestamp="%d.%d" % (seconds, nanos),
                           duration_micros=int(util._time_to_micros(span.duration)))
        return span_record

    def append_attribute(self, span_record, key, value):
        span_record.tags[key] = value

    def append_join_id(self, span_record, key, value):
        self.append_attribute(span_record, key, value)

    def append_log(self, span_record, log):
        if log.key_values is not None and len(log.key_values) > 0:
            log_dict = {"timestamp": log.timestamp}
            log_dict.update(log.key_values)
            span_record.logs.append(log_dict)

    def create_report(self, runtime, span_records):
        return ReportRequest(reporter=runtime, spans=span_records)

    def combine_span_records(self, report_request, span_records):
        report_request.spans.extend(span_records)
        return report_request.spans

    def num_span_records(self, report_request):
        return len(report_request.spans)

    def get_span_records(self, report_request):
        return report_request.spans

    def get_span_name(self, span_record):
        return span_record.get("operation_name", None)
