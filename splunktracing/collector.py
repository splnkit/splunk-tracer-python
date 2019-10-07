import json
import copy


class ReportRequest(object):
    def __init__(self, reporter, spans):
        self.reporter = reporter
        self.spans = spans

    def serialize_to_string(self):
        report_objs = []
        for span in self.spans:
            span_dict = {
                "trace_id": span.span_context.trace_id,
                "span_id": span.span_context.span_id,
                "parent_span_id": span.span_context.parent_id,
                "operation_name": span.operation_name,
                "tags": span.tags,
                "baggage": span.span_context.baggage
            }
            span_dict.update(self.reporter.tags)
            for log in span.logs:
                log_event = {
                    "time": log["timestamp"],
                    "sourcetype": "splunktracing:log",
                    "event": {"fields": log , "timestamp": log["timestamp"]}
                }
                log_event["event"].update(span_dict)
                report_objs.append(log_event)
            span_dict["timestamp"] = span.start_timestamp
            span_dict["duration"] = span.duration_micros
            span_event = {
                "time": span.start_timestamp,
                "sourcetype": "splunktracing:span",
                "event": span_dict
            }
            report_objs.append(span_event)
        return "\n".join([json.dumps(obj) for obj in report_objs])


class Span(object):
    def __init__(self, span_context, operation_name, start_timestamp, duration_micros, tags={}, logs=[]):
        self.span_context = span_context
        self.operation_name = operation_name
        self.start_timestamp = start_timestamp
        self.duration_micros = duration_micros
        self.tags = tags
        self.logs = logs


class Reporter(object):
    def __init__(self, reporter_id, tags):
        self.reporter_id = reporter_id
        self.tags = tags


class SpanContext(object):
    def __init__(self, trace_id, span_id, parent_id, baggage={}):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.baggage = baggage

class Timestamp(object):
    def __init__(self, seconds, nanos):
        self.seconds = seconds
        self.nanos = nanos
