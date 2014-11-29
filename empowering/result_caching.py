# -*- coding: utf-8 -*-

import time

AVALIABLE_ONLINE_TOOLS = ['ot101', 'ot201', 'ot103', 'ot503']

NO_RESULT_ERROR = 'No empowering result'
NO_STORED_ERROR = 'No stored value to compare with'
WRONG_VALUE_ERROR = 'Wrong value' 

class OTCaching(object):

    def __init__(self, empowering_service, empowering_resource,
                 mongo_connection, ot_code, log_error_collection,
                 period_key, value_key):
        self._empowering_resource = getattr(empowering_serivce,
                                            empowering_resource)
        self._result_collection = mongo_connection.get_collection(ot_code)
        self._log_error_collection = mongo_connection.get_collection(
                                                      log_error_collection)
        # Key used in results to specify the period
        self._period_key = period_key
        self._value_key = value_key
        self._ot_code = ot_code

    def pull_contract(self, cursor, uid, contract, period=None):
        """ Will ask for results of online tool for the specidied
        " contract for ALL periods if is not specidied in period param.
        " Pulled results will be stored in the mongo database
        "
        " If result already exist is replaced by the new one
        """
        results = self._empowering_resource().pull(contract=contract,
                                                   period=period)
        if '_items' not in results:
            # If _items not i results nothing to do, no results found
            return 0

        for result in results['_items']:
            result_period = result[self._period_key]
            if self._get(contract, result_period):
                # Delete cached result to replace it
                self._delete_cached(contract, result_period)
            self._store(result)

    def validate_contract(values, contract, period=None, log_errors=True):
        """ Validate the contract according to the values dict.
        " Values dict contain period as key and value as value.
        " Will create the error log in collection according to log_errors param
        "
        " values example:
        " {'201301': 42.2, '201302': 75.3}
        """
        cached_results = self._get(contract, period)
        for result in cached_results:
            cached_period = result[self._period_key]
            cached_value = result[self._value_key]
            error = None

            if cached_period not in values:
                # No stored value to compare with.
                # So we discart the empowering result
                error = NO_STORED_ERROR
                self._delete_cached(contract, cached_period)

            if cached_value != values[cached_period]:
                # Stored and empowering result missmatch
                # So we discart the empowering result
                error = WRONG_VALUE_ERROR
                self._delete_cached(contract, cached_period)
            else:
                pass #Everything OK :)

            if error and log_errors:
                self._insert_error(contract, cached_period, error)

            if cached_period not in values:
                # Pop from values to know if there are missing results
                values.pop(cached_period)

        for v_period, v_value in values:
            # There are still values to be checked
            error = NO_RESULT_ERROR
            self._insert_error(contract, v_period, error)

    def error_report(self, ot_code=None, contract=None, period=None,
                     validation_date='today'):
        """
        " @return an string containing a report of the errors happened
        """
        report = ''
        search_params = {}

        if validation_date == 'today':
            validation_date = time.strftime('%Y-%m-%d')

        if validation_date:
            search_params.update({'validation_date': validation_date})
        if ot_code:
            search_params.update({'ot_code': ot_code})
        if period:
            search_params.update({'period': period})
        if contract:
            search_params.update({'contract': contract})

        old_search = {'$ne': {'validation_date', validation_date}}
        old_errors = self._log_error_collection.find(old_search).count()
        if old_errors:
            report += 'WARNING: There are %d stored old errors.\n' % old_errors

        filter_msg += 'REPORT FILTER: %s ot - %s contract %s period %s date\n'
        filter_msg %= ot_code and ot_code or 'all' 
        filter_msg %= contract and contract or 'all'
        filter_msg %= period and period or 'all'
        filter_msg %= validation_date and validation_date or 'all'

        report += filter_msg

        if not ot_code:
            ot_codes = AVALIABLE_ONLINE_TOOLS
        else:
            ot_codes = [ot_code]

        for ot in ot_codes:
            report += '%s\n' % ot
            for error in (WRONG_VALUE_ERROR, NO_RESULT_ERROR, NO_STORED_ERROR):
                errors = search_params.copy()
                errors.update({'error': error})
                count = self._log_error_collection.find(errors).count()
                report += '\t%s: %d\n' % (error, count)

        return report

    def error_clear(self, ot_code=None, contract=None, period=None,
                    validation_date='today')
        """
        " Clear errors from database, si recomended to call this methond
        " just after error_report with the same parameters.
        """
        search_params = {}

        if validation_date == 'today':
            validation_date = time.strftime('%Y-%m-%d')

        if validation_date:
            search_params.update({'validation_date': validation_date})
        if ot_code:
            search_params.update({'ot_code': ot_code})
        if period:
            search_params.update({'period': period})
        if contract:
            search_params.update({'contract': contract})

        self._log_error_collection.remove(search_params)

 
    def _get(self, contract, period=None):
        query = {'contractId': contract}
        if period:
            query.update({self._period_key: period})

        return [x for x in self._result_collection.find(query)]

    def _store(self, result)
        self._result_collection.insert(result)

    def _delete_cached(self, contract, period=None):
        remove_query = {'contractId': contract}
        if period:
            remove_query.update({
                self._period_key: int(period) 
            })
    
        self._result_collection.remove(remove_query)

    def _insert_error(self, contract, period, error_message):
        error = {
            'ot_code': self._ot_code,
            'contract': contract,
            'period': period,
            'error': error_message,
            'validation_date': time.strftime('%Y-%m-%d')
        }
        self._log_error_collection(error)


class OT101Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(self, OT101).(empowering_service, 'ot101_results',
                            mongo_connection, 'ot101', 'empowering_error',
                            'month', 'consumption')

class OT103Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(self, OT101).(empowering_service, 'ot103_results',
                            mongo_connection, 'ot103', 'empowering_error',
                            'month', 'consumption')

class OT201Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(self, OT101).(empowering_service, 'ot201_results',
                            mongo_connection, 'ot201', 'empowering_error',
                            'month', 'actualConsumption')

class OT503Cahing(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(self, OT101).(empowering_service, 'ot503_results',
                            mongo_connection, 'ot503', 'empowering_error',
                            'time', 'consumption')


