from empowering.service import EmpoweringResource
from empowering.utils import searchparams_to_querystring

import calendar

class OTResult(EmpoweringResource):
    def pull(self, period=None, contract=None):
        search_params = []

        if contract:
            if type(contract) is not str:
                contract = str(contract)
            param = ('contractId', '=', contract)
            search_params.append(param)

        if period:
            if type(period) is not int:
                period = int(period)
            param = ('month', '=', period)
            search_params.append(param)

        query = searchparams_to_querystring(search_params)
        return self.multiget(where=query)

class OT101Results(OTResult):
    path = 'OT101Results'


class OT103Results(OTResult):
    path = 'OT103Results'


class OT106Results(OTResult):
    path = 'OT106Results'


class OT201Results(OTResult):
    path = 'OT201Results'


class OT204Results(OTResult):
    path = 'OT204Results'


class OT503Results(OTResult):
    path = 'OT503Results'

    def pull(self, period=None, contract=None):
        # Thanks empowering for keeping the acorded API :D </ironic>

        last_day = 31
        search_params = []
        if contract:
            if type(contract) is not str:
                contract = str(contract)
            param = ('contractId', '=', contract)
            search_params.append(param)
        if period:
            if type(period) is not str:
                # For API coherence period should be int but
                # is not useful here
                period = str(period)

            year = period[:4]
            month = period[-2:]
            last_day = calendar.monthrange(int(year), int(month))[1]

            start_period = '%s%s%s' % (year, month, '01')
            end_period = '%s%s%s' % (year, month, last_day)

            params = [
                ('day', '>=', int(start_period)),
                ('day', '<=', int(end_period)),
            ]
            search_params.extend(params)

        query = searchparams_to_querystring(search_params)
        return self.multiget(where=query, sort='[("day", 1)]',
                             max_results=last_day)


class OT900Results(OTResult):
    path = 'OT900Results'


class BT111Results(OTResult):
    path = 'BT111Results'
