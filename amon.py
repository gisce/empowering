#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import sys
import uuid

import times
from ooop import OOOP

CUPS_CACHE = {}
DEVICE_MP_REL = {}
CUPS_UUIDS = {}
UNITS = {'1': '', '1000': 'k'}

def get_device_serial(device_id):
    return device_id[3:].lstrip('0')

def get_cups_from_device(device_id):
    # Remove brand prefix and right zeros
    serial = get_device_serial(device_id)
    if serial in CUPS_CACHE:
        return CUPS_CACHE[serial]
    else:
        # Search de meter
        cid = O.GiscedataLecturesComptador.search([('name', '=', serial)])
        if not cid:
            res = False
        else:
            print cid
            cid = O.GiscedataLecturesComptador.get(cid[0])
            res = str(uuid.uuid5(uuid.NAMESPACE_OID, cid.polissa.cups.name))
        CUPS_CACHE[serial] = res
        CUPS_UUIDS[res] = cid.polissa.cups.id
        return res
        

def make_utc_timestamp(timestamp):
    return times.to_universal(timestamp, 'Europe/Madrid').isoformat('T') + 'Z'

def get_street_name(cups):
    street = []
    street_name = u''
    if cups.cpo or cups.cpa:
        street = u'CPO %s CPA %s' % (cups.cpo, cups.cpa)
    else:
        if cups.tv:
            street.append(cups.tv.name)
        if cups.nv:
            street.append(cups.nv)
        street_name += u' '.join(street)
        street = [street_name]
        for f_name, f in [(u'número', 'pnp'), (u'escalera', 'es'),
                          (u'planta', 'pt'), (u'puerta', 'pu')]:
            val = getattr(cups, f)
            if val:
                street.append(u'%s %s' % (f_name, val))
    street_name = ', '.join(street)
    return street_name

def datestring_to_epoch(date_string):
    if not date_string:
        return None
    return datetime.strptime(date_string, '%Y-%m-%d').strftime('%s')

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
        device_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, profile['name']))
        DEVICE_MP_REL[device_uuid] = mp_uuid
        res.append({
            "deviceId": device_uuid,
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

def cups_to_amount(mp_uuids, context=None):
    """Convert CUPS to Amon.

    {
        "meteringPointId": uuid,
        "metadata": {
            "cupsnumber": "ES0987543210987654ZF",
            "address": {
                "street": "Calle y número",
                "postalCode": "CodigoPostal",
                "city": "Nombre ciudad",
                "cityCode": "Código INE ciudad",
                "province": "Nombre provincia",
                "provinceCode": "Código INE provincia",
                "country": "España",
                "countryCode": "ES. Codigo según ISO 3166",
                "parcelNumber": "Referencia catastral"
            }
        }
    }
    """
    res = []
    cups_obj = O.GiscedataCupsPs
    if not hasattr(mp_uuids, '__iter__'):
        mp_uuids = [mp_uuids]
    for mp_uuid in mp_uuids:
        cups = cups_obj.get(CUPS_UUIDS[mp_uuid])
        res.append(false_to_none({
            "meteringPointId": mp_uuid,
            "metadata": {
                'cupsnumber': cups.name,
                'address': {
                    'street': get_street_name(cups),
                    'postalCode': cups.dp,
                    'city': cups.id_municipi.name,
                    'cityCode': cups.id_municipi.ine,
                    'province': cups.id_municipi.state.name,
                    'provinceCode': cups.id_municipi.state.code,
                    'country': cups.id_municipi.state.country_id.name,
                    'countryCode': cups.id_municipi.state.country_id.code,
                    'parcelNumber': cups.ref_catastral
                }
            },
        }, context))

def device_to_amon(device_uuids):
    """Convert a device to AMON.

    {
        "deviceId": required string UUID,
        "meteringPointId": required string UUID,
        "metadata": {
            # Think what we could put inside this
        }, 
    }
    """
    res = []
    if not hasattr(device_uuids, '__iter__'):
        device_uuids = [device_uuids]
    for dev_uuid in device_uuids:
        res.append(false_to_none({
            "deviceId": dev_uuid,
            "meteringPointId": DEVICE_MP_REL[dev_uuid],
            "metadata": {
            }
        }))
    return res

def contract_to_amon(contract_ids, context=None):
    """Converts contracts to AMON.

    {
        "id": "uuid",
        "owenerId": "uuid",
        "payerId": "uuid",
        "version": "2",
        "start": 1332806400,
        "end": 1362009600,
        "tariffId": "2.0A",
        "power": 3300,
        "activityCode": "CNAE",
        "meteringPointId": "c1759810-90f3-012e-0404-34159e211070",
    }
    """
    if not context:
        context = {}
    res = []
    pol = O.GiscedataPolissa
    modcon_obj = O.GiscedataPolissaModcontractual
    if not hasattr(contract_ids, '__iter__'):
        contract_ids = [contract_ids]
    for contract_id in contract_ids:
        polissa = pol.get(contract_id)
        if 'modcon_id' in context:
            modcon = modcon_obj.get(context['modcon_id'])
        else:
            modcon = polissa.modcontractual_activa
        res.append(false_to_none({
            'id': str(uuid.uuid5(uuid.NAMESPACE_OID, polissa.name)),
            'customerId': str(uuid.uuid5(uuid.NAMESPACE_OID, modcon.pagador.id)),
            'start': datestring_to_epoch(times.to_universal(modcon.data_inici, 'Europe/Madrid')),
            'end': datestring_to_epoch(times.to_universal(modcon.data_final, 'Europe/Madrid')),
            'tariffId': modcon.tarifa.name,
            'power': int(modcon.potencia * 1000),
            'version': modcon.name,
            'activityCode': modcon.cnae.name,
            'meteringPointId': str(uuid.uuid5(uuid.NAMESPACE_OID, modcon.cups.name)),
        }, context))
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
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 80
    profiles = O.TgProfile.search([], 0, limit)
    profiles = O.TgProfile.read(profiles)
    print profile_to_amon(profiles)
    print device_to_amon(DEVICE_MP_REL.keys())
    
    
