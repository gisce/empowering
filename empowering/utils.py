import uuid
import times


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