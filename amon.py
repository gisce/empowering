import uuid
import times

CUPS_CACHE = {}
UNITS = {'1': '', '1000': 'k'}

def get_cups_from_device(device_id):
    # Remove brand prefix and right zeros
    device_id = device_id[3:].lstrip('0')
    if device_id in CUPS_CACHE:
        return CUPS_CACHE[device_id]
    else:
        # Search de meter
        cid = O.GiscedataLecturesComptador.search([('name', '=', device_id)])
        if not cid:
            res = False
        else:
            cid = O.GiscedataLecturesComptador.get(cid[0])
            res = uuid.uuid5(uuid.NAMESPACE_OID, cid.polissa_id.cups.name)
        CUPS_CACHE[device_id] = res
        return res

def make_utc_timestamp(timestamp):
    return times.to_universal(timestamp, 'Europe/Madrid').isoformat('T') + 'Z'

def profile_to_amon(profiles):
    """Return a list of AMON readinds.

    {
        "deviceId": "c1810810-0381-012d-25a8-0017f2cd3574",
        "meteringPointId": "c1759810-90f3-012e-0404-34159e211070",
        "readings": [
            {
                "type": "electricityConsumption",
                "unit": "kWh",
                "period": "INSTANT",
            },
            {
                "type": "electricityKiloVoltAmpHours",
                "unit": "kVArh",
                "period": "INSTANT",
            }
        ],
        "measurements": [
            {
                "type": "electricityConsumption",
                "timestamp": "2010-07-02T11:39:09Z", # UTC
                "value": 7
            },
            {
                "type": "electricityKiloVoltAmpHours",
                "timestamp": "2010-07-02T11:44:09Z", # UTC
                "value": 6
            }
        ]
    }
    """
    res = []
    if not hasattr(profiles, '__iter__'):
        profiles = [profiles]
    for profile in profiles:
        res.append({
            "deviceId": uuid.uuid5(uuid.NAMESPACE_OID, profile['name']),
            "meteringPointId": get_cups_from_device(profile['name'])
            "readings": [
                {
                    "type":  "electricityConsumption",
                    "unit": "%sWh" % UNITS[profile['magn']],
                    "period": "INSTANT",
                },
                {
                    "type": "electricityKiloVoltAmpHours",
                    "unit": "%sVArh" % UNITS[profile['magn']],
                    "period": "INSTANT",
                }
            ],
            "measurements": [
                {
                    "type": "electricityConsumption",
                    "timestamp": make_utc_timestamp(profile['timestamp']),
                    "value": profile['ai']
                },
                {
                    "type": "electricityKiloVoltAmpHours",
                    "timestamp": make_utc_timestamp(profile['timestamp']),
                    "value": profile['r1']
                }
        ]
        })
    return res
    