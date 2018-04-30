"""
Validation support
"""

import base64, hashlib, io
import hxl

SEVERITY_LEVELS = {
    'info': 1,
    'warning': 2,
    'error': 3
}

def make_rule_hash(rule):
    """Make a good-enough hash for a rule."""
    s = "\r".join([str(rule.severity), str(rule.description), str(rule.tag_pattern)])
    return base64.urlsafe_b64encode(hashlib.md5(s.encode('utf-8')).digest())[:8].decode('ascii')

def do_validate(source, schema_url=None, schema_content=None, severity_level=None):
    """Validate a source, and return a list of errors."""
    min_severity = SEVERITY_LEVELS.get(severity_level, -1)
    errors = {}
    def callback(error):
        if SEVERITY_LEVELS.get(error.rule.severity, 0) >= min_severity:
            rule_hash = make_rule_hash(error.rule)
            if errors.get(rule_hash) is None:
                errors[rule_hash] = []
            errors[rule_hash].append(error)

    # baseline schema
    schema = hxl.schema(schema_url, callback)

    # extra, inline schema
    if schema_content:
        extra_schema = hxl.schema(hxl.data(io.BytesIO(schema_content.encode('utf-8'))))
        for rule in extra_schema.rules:
            schema.rules.append(rule)
    
    result = schema.validate(source)
    return errors

# end
