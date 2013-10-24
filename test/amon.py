#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import sys
import urllib
import uuid
import json

import times
from ooop import OOOP

CUPS_CACHE = {}
DEVICE_MP_REL = {}
CUPS_UUIDS = {}
PARTNERS = []
UNITS = {'1': '', '1000': 'k'}

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


def make_uuid(model, model_id):
    token = '%s,%s' % (model, model_id)
    return str(uuid.uuid5(uuid.NAMESPACE_OID, token))


def make_post_data(json_list):
    post_data = {}
    for idx, item in enumerate(json_list):
        post_data['item%s' % idx] = json.dumps(item)
    return urllib.urlencode(post_data)


def get_device_serial(device_id):
    return device_id[5:].lstrip('0')


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
            cid = O.GiscedataLecturesComptador.get(cid[0])
            res = make_uuid('giscedata.cups.ps', cid.polissa.cups.name)
            CUPS_UUIDS[res] = cid.polissa.cups.id
        CUPS_CACHE[serial] = res
        return res
        

def make_utc_timestamp(timestamp):
    if not timestamp:
        return None
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
    if not isinstance(date_string, datetime):
        dt = datetime.strptime(date_string, '%Y-%m-%d')
    else:
        dt = date_string
    return dt.strftime('%s')


def profile_to_amon(profiles):
    """Return a list of AMON readinds.

    {
        "utilityId": "Utility Id",
        "deviceId": "c1810810-0381-012d-25a8-0017f2cd3574",
        "meteringPointId": "c1759810-90f3-012e-0404-34159e211070",
        "readings": [
            {
                "type_": "electricityConsumption",
                "unit": "kWh",
                "period": "INSTANT",
            },
            {
                "type_": "electricityKiloVoltAmpHours",
                "unit": "kVArh",
                "period": "INSTANT",
            }
        ],
        "measurements": [
            {
                "type_": "electricityConsumption",
                "timestamp": "2010-07-02T11:39:09Z", # UTC
                "value": 7
            },
            {
                "type_": "electricityKiloVoltAmpHours",
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
            print "No mp_uuid"
            continue
        device_uuid = make_uuid('giscedata.lectures.comptador', profile['name'])
        res.append({
            "companyId": 8449512768,
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
                    "value": float(profile['ai'])
                },
                {
                    "type": "electricityKiloVoltAmpHours",
                    "timestamp": make_utc_timestamp(profile['timestamp']),
                    "value": float(profile['r1'])
                }
        ]
        })
    return res

def device_to_amon(device_ids):
    """Convert a device to AMON.

    {
        "utilityId": "Utility Id",
        "externalId": required string UUID,
        "meteringPointId": required string UUID,
        "metadata": {
            "max": "Max number",
            "serial": "Device serial",
            "owner": "empresa/client"
        }, 
    }
    """
    res = []
    if not hasattr(device_ids, '__iter__'):
        device_ids = [device_ids]
    for dev_id in device_ids:
        dev = O.GiscedataLecturesComptador.get(dev_id)
        if dev.propietat == "empresa":
            dev.propietat = "company"
        res.append(remove_none({
            "utilityId": "1",
            "externalId": make_uuid('giscedata.lectures.comptador', dev_id),
            "meteringPointId": make_uuid('giscedata.cups.ps', dev.polissa.cups.name),
            "metadata": {
               "max": dev.giro,
               "serial": dev.name,
               "owner": dev.propietat, 
            }
        }))
    return res

def contract_to_amon(contract_ids, context=None):
    """Converts contracts to AMON.

    {
      "payerId":"payerID-123",
      "ownerId":"ownerID-123",
      "signerId":"signerID-123",
      "power":123,
      "dateStart":"2013-10-11T16:37:05Z",
      "dateEnd":null,
      "contractId":"contractID-123",
      "customer":{
        "customerId":"payerID-123",
        "address":{
          "city":"city-123",
          "cityCode":"cityCode-123",
          "countryCode":"ES",
          "country":"Spain",
          "street":"street-123",
          "postalCode":"postalCode-123"
        }
      },
      "meteringPointId":"c1759810-90f3-012e-0404-34159e211070",
      "devices":[
        {
          "dateStart":"2013-10-11T16:37:05Z",
          "dateEnd":null,
          "deviceId":"c1810810-0381-012d-25a8-0017f2cd3574"
        }
      ],
      "version":1,
      "activityCode":"activityCode",
      "tariffId":"tariffID-123",
      "companyId":1234567890
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
        PARTNERS.append(modcon.pagador.id)
        PARTNERS.append(modcon.titular.id)
        contract = {
            'companyId': 8449512768,
            'ownerId': make_uuid('res.partner', modcon.titular.id),
            'payerId': make_uuid('res.partner', modcon.pagador.id),
            'dateStart': make_utc_timestamp(modcon.data_inici),
            'dateEnd': make_utc_timestamp(modcon.data_final),
            'contractId': polissa.name,
            'tariffId': modcon.tarifa.name,
            'power': int(modcon.potencia * 1000),
            'version': int(modcon.name),
            'activityCode': modcon.cnae and modcon.cnae.name or None,
            'meteringPointId': make_uuid('giscedata.cups.ps', modcon.cups.name),
            'customer': {
                'customerId': make_uuid('res.partner', modcon.titular.id),
                'address': {
                    'city': polissa.cups.id_municipi.name,
                    'cityCode': polissa.cups.id_municipi.ine,
                    'countryCode': polissa.cups.id_provincia.country_id.code,
                    'street': get_street_name(polissa.cups),
                    'postalCode': polissa.cups.dp
                }
            }
        }
        devices = []
        for comptador in polissa.comptadors:
            devices.append({
                'dateStart': make_utc_timestamp(comptador.data_alta),
                'dateEnd': make_utc_timestamp(comptador.data_baixa),
                'deviceId': make_uuid('giscedata.lectures.comptador',
                                      comptador.id)
            })
        contract['devices'] = devices
        res.append(remove_none(contract, context))
    return res

def partners_to_amon(partner_ids, context=None):
    """Convert a partner to JSON Format.

    {
      "utilityId": "Utility id",
      "externalId": "sample string 1",
      "firstName": "sample string 3",
      "firstSurname": "sample string 4",
      "secondSurname": "sample string 5",
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
        if not partner.vat:
            partner.vat = '40000'
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
            if not partner.address:
                addr = False
            else:
                addr = partner.address[0]
        data = {
            'utilityId': '1',
            'externalId': make_uuid('res.partner', partner.id),
            'firstName': first_name,
            'firstSurname': first_surname
        }
        if addr:
            data['address'] = {
                'street': addr.street,
                'postalCode': addr.zip,
                'city': addr.municipi and addr.municipi.name or None,
                'cityCode': addr.municipi and addr.municipi.ine or None,
                'province': addr.state_id and addr.state_id.name or None,
                'provinceCode': addr.state_id and addr.state_id.code or None,
                'country': addr.country_id and addr.country_id.name or None,
                'countryCode': addr.country_id and addr.country_id.code or None,
                'parcelNumber': None
            }
        res.append(remove_none(data, context))
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
    from empowering import Empowering
    em = Empowering(8449512768)
    if sys.argv[2] == 'push_amon_measures':
        profiles_ids = O.TgProfile.search([], 0, limit)
        profiles = O.TgProfile.read(profiles_ids)
        profiles_to_push = profile_to_amon(profiles)
        print em.amon_measures().create(profiles_to_push)
    elif sys.argv[2] == 'push_contracts':
        contracts_ids = O.GiscedataPolissa.search([], 0, limit)
        contracts_to_push = contract_to_amon(contracts_ids)
        print em.contracts().create(contracts_to_push)
    elif sys.argv[2] == 'get_contracts':
        print em.contracts().get()
    elif sys.argv[2] == 'get_contract':
        print em.contract(sys.argv[3]).get()
