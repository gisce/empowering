from datetime import datetime
import uuid
import times
from arrow.parser import DateTimeParser


# Monkey patch parse function for times library (newer)
parser = DateTimeParser()
times.parse = parser.parse_iso


def remove_none(struct, context=None):
    if not context:
        context = {}
    if 'xmlrpc' in context:
        return struct
    converted = struct.copy()
    for key, value in struct.items():
        if isinstance(value, dict):
            converted[key] = remove_none(value)
        else:
            if value is None or (isinstance(value, bool) and not value):
                del converted[key]
    return converted


def false_to_none(struct, context=None):
    if not context:
        context = {}
    if 'xmlrpc' in context:
        return struct
    converted = struct.copy()
    for key, value in struct.items():
        if isinstance(value, dict):
            converted[key] = false_to_none(value)
        else:
            if isinstance(value, bool) and not value:
                converted[key] = None
    return converted


def none_to_false(struct):
    if isinstance(struct, (list, tuple)):
        return [none_to_false(x) for x in struct]
    converted = struct.copy()
    for key, value in struct.items():
        if isinstance(value, dict):
            converted[key] = none_to_false(value)
        elif isinstance(value, (list, tuple)):
            converted[key] = none_to_false(value)
        else:
            if value is None:
                converted[key] = False
    return converted


def make_uuid(model, model_id):
    if isinstance(model, unicode):
        model = model.encode('utf-8')
    if isinstance(model_id, unicode):
        model_id = model_id.encode('utf-8')
    token = '%s,%s' % (model, model_id)
    return str(uuid.uuid5(uuid.NAMESPACE_OID, token))


def make_utc_timestamp(timestamp, timezone='Europe/Madrid'):
    if not timestamp:
        return None
    return times.to_universal(timestamp, timezone).isoformat('T') + 'Z'


def make_local_timestamp(timestamp, timezone='Europe/Madrid'):
    if not timestamp:
        return None
    if isinstance(timestamp, basestring):
        timestamp = times.parse(timestamp.replace('Z', ''))
    return times.to_local(timestamp, timezone).strftime('%Y-%m-%d %H:%M:%S')


def datestring_to_epoch(date_string):
    if not date_string:
        return None
    if not isinstance(date_string, datetime):
        dt = datetime.strptime(date_string, '%Y-%m-%d')
    else:
        dt = date_string
    return dt.strftime('%s')

def searchparams_to_querystring(search_params):
    operator_map = {
        '=': '==',
        '>=': '>=',
        '>': '>',
        '<': '<',
        '<=': '<=',
    }

    query = ''
    for param in search_params:
        if query:
            # is not the first
            query += ' and '

        field = param[0]
        operator = param[1]
        value = param[2]

        try:
            query_operator = operator_map[operator]
        except KeyError:
            raise Exception('Unsuported operand "%s"' % operand)

        if type(value) is str:
            # Add "" to the value
            query_value = '"%s"' % value
        else:
            query_value = '%s' % value

        query += '"%s"%s%s' % (field, query_operator, query_value)

    return query

