import os
import sys
import uuid

import times
from ooop import OOOP

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
            res = str(uuid.uuid5(uuid.NAMESPACE_OID, cid.polissa.cups.name))
        CUPS_CACHE[device_id] = res
        return res

def make_utc_timestamp(timestamp):
    return times.to_universal(timestamp, 'Europe/Madrid').isoformat('T') + 'Z'

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
        mp_uuid = get_cups_from_device(profile['name'])
        if not mp_uuid:
            continue
        res.append({
            "deviceId": str(uuid.uuid5(uuid.NAMESPACE_OID, profile['name'])),
            "meteringPointId": mp_uuid,
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

def partner_data(partner_ids, context=None):
    """Convert a partner to JSON Format.

    {
      "id": "sample string 1",
      "fiscalId": "sample string 2",
      "firstName": "sample string 3",
      "firstSurname": "sample string 4",
      "secondSurname": "sample string 5",
      "email": "sample string 6",
      "address": {
        "street": "sample string 1",
        "postalCode": "sample string 2",
        "city": "sample string 3",
        "cityCode": "sample string 4",
        "province": "sample string 5",
        "provinceCode": "sample string 6",
        "country": "sample string 7",
        "countryCode": "sample string 8",
        "parcelNumber": "sample string 9"
      }
    }
    """
    if not hasattr(partner_ids, '__iter__'):
        partner_ids = [partner_ids]
    addr_obj = O.ResPartnerAddress
    if not context:
        context = {}
    res = []
    for partner_id in partner_ids:
        partner = O.ResPartner.get(partner_id)
        vat = len(partner.vat) == 9 and partner.vat or partner.vat[2:]
        if (vat[0] not in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                           'J', 'U', 'V', 'N', 'P', 'Q', 'R', 'S', 'W')
                and ',' in partner.name):
            first_name = partner.name.split(',')[-1].strip()
            first_surname = ' '.join([
                x.strip() for x in partner.name.split(',')[:-1]
            ])
        else:
            first_name = partner.name
            first_surname = ''
        if 'address_id' in context:
            addr = addr_obj.get(context['address_id'])
        else:
            addr = partner.address[0]
        print addr.read()
        res.append(false_to_none({
            'id': partner.id,
            'fiscalId': vat,
            'firstName': first_name,
            'firstSurname': first_surname,
            'email': addr.email,
            'address': {
                'street': addr.nv,
                'postalCode': addr.zip,
                'city': addr.id_municipi.name,
                'cityCode': addr.id_municipi.ine,
                'province': addr.state_id.name,
                'provinceCode': addr.state_id.code,
                'country': addr.country_id.name,
                'countryCode': addr.country_id.code,
                'parcelNumber': addr.pnp
            }
        }, context))
    return res

if __name__ == '__main__':
    ooop_config = {}
    for key, value in os.environ.items():
        if key.startswith('OOOP_'):
            key = key.split('_')[1].lower()
            if key == 'port':
                value = int(value)
            ooop_config[key] = value
    print "Using OOOP CONFIG: %s" % ooop_config

    O = OOOP(**ooop_config)
    if sys.argv[1] == 'test':
        #pids = O.ResPartner.search([], 0, 80)
        #print partner_data(pids)
        profiles = O.TgProfile.search([], 0, 80)
        profiles = O.TgProfile.read(profiles)
        print profile_to_amon(profiles)
    
    
