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
        self._empowering_resource = getattr(empowering_service,
                                            empowering_resource)
        self._result_collection = getattr(mongo_connection, ot_code)
        self._log_error_collection = getattr(mongo_connection,
                                             log_error_collection)
        # Key used in results to specify the period
        self._period_key = period_key
        self._value_key = value_key
        self._ot_code = ot_code

    def pull_contract(self, contract, period=None):
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

    def validate_contract(self, values, contract, period=None, log_errors=True):
        """ Validate the contract according to the values dict.
        " Values dict contain period as key and value as value.
        " Will create the error log in collection according to log_errors param
        "
        " values example:
        " {'201301': 42.2, '201302': 75.3}
        """
        cached_results = self._get(contract, period)
        for result in cached_results:
            cached_period = str(int(result[self._period_key]))
            cached_value = result[self._value_key]
            error = None
            error_details = {}

            if cached_period not in values:
                # No stored value to compare with.
                # So we discart the empowering result
                error = NO_STORED_ERROR
            elif not self._is_valid(cached_value, values[cached_period]):
                # Stored and empowering result missmatch
                # So we discart the empowering result
                error = WRONG_VALUE_ERROR
                error_details.update({
                    'expected': values[cached_period],
                    'cached': cached_value
                })
            else:
                pass #Everything OK :)

            if error:
                self._delete_cached(contract, cached_period)
                if log_errors:
                    self._insert_error(contract, cached_period, error,
                                       error_details)

            if cached_period in values:
                # Pop from values to know if there are missing results
                values.pop(cached_period)

        for v_period, v_value in values.iteritems():
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
        if period:
            search_params.update({'period': period})
        if contract:
            search_params.update({'contract': contract})

        old_search = {'validation_date': {'$ne': validation_date}}
        old_errors = self._log_error_collection.find(old_search).count()
        if old_errors:
            report += 'WARNING: There are %d stored old errors.\n' % old_errors

        filter_msg = 'REPORT FILTER: %s ot - %s contract %s period %s date\n'
        filter_msg %= (
            ot_code and ot_code or 'all',
            contract and contract or 'all',
            period and period or 'all',
            validation_date and validation_date or 'all'
        )
        report += filter_msg

        if not ot_code:
            ot_codes = AVALIABLE_ONLINE_TOOLS
        else:
            ot_codes = [ot_code]

        for ot in ot_codes:
            report += '%s\n' % ot
            for error in (WRONG_VALUE_ERROR, NO_RESULT_ERROR, NO_STORED_ERROR):
                errors = search_params.copy()
                errors.update({'error': error, 'ot_code': ot})
                count = self._log_error_collection.find(errors).count()
                report += '\t%s: %d\n' % (error, count)

        return report

    def error_clear(self, ot_code=None, contract=None, period=None,
                    validation_date='today'):
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
            query.update({self._period_key: int(period)})

        return [x for x in self._result_collection.find(query)]

    def _store(self, result):
        self._result_collection.insert(result)

    def _delete_cached(self, contract, period=None):
        remove_query = {'contractId': contract}
        if period:
            remove_query.update({
                self._period_key: int(period)
            })

        self._result_collection.remove(remove_query)

    def _is_valid(self, cached, reference):
        """ Return True if cached value is valid according to the
        " value reference, false otherwise
        """
        return abs(reference - cached) < 2

    def _insert_error(self, contract, period, error_message,
                      error_details=None):
        error = {
            'ot_code': self._ot_code,
            'contract': contract,
            'period': period,
            'error': error_message,
            'validation_date': time.strftime('%Y-%m-%d')
        }
        if error_details:
            error.update(error_details)
        if not self._log_error_collection.find(error).count():
            # Avoid insert errors twice
            self._log_error_collection.insert(error)


class OT101Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(OT101Caching, self).__init__(empowering_service, 'ot101_results',
                                  mongo_connection, 'ot101', 'empowering_error',
                                  'month', 'consumption')

class OT103Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(OT103Caching, self).__init__(empowering_service, 'ot103_results',
                            mongo_connection, 'ot103', 'empowering_error',
                            'month', 'consumption')

class OT201Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(OT201Caching, self).__init__(empowering_service, 'ot201_results',
                            mongo_connection, 'ot201', 'empowering_error',
                            'month', 'actualConsumption')

class OT503Caching(OTCaching):
    def __init__(self, empowering_service, mongo_connection):
        super(OT503Caching, self).__init__(empowering_service, 'ot503_results',
                            mongo_connection, 'ot503', 'empowering_error',
                            'time', 'consumption')

    def _get_period_sum(self, contract, period):
        period_start = int(period + '01')
        period_end = int(period + '31')

        aggregate = [
            {
                "$match": {
                    "contractId": contract,
                    "time": {
                        "$gte": period_start,
                        "$lte": period_end
                    }
                }
            },
            {
                "$group": {
                    "_id": "$contractId",
                    "total": {
                        "$sum": "$consumption"
                    }
                }
            }
        ]

        result = self._result_collection.aggregate(aggregate)
        if 'result' in result and 'total' in result['result'][0]:
            return result['result'][0]['total']
        else:
            return None

    def _delete_month_period(self, contract, period):
        """
        " Delete all cached in the given period
        """
        period_start = int(period + '01')
        period_end = int(period + '31')
        remove = {
            "contractId": contract,
            "time": {
                "$gte": period_start,
                "$lte": period_end
            }
        }
        self._result_collection.remove(remove)

    def _delete_all_periods_except(self, contract, period_list):
        """
        " Delete al results for the contract not in the period_list
        """
        keep_ids = []
        for period in period_list:
            period_start = int(period + '01')
            period_end = int(period + '31')
            query = {
                "contractId": contract,
                "time": {
                    "$gte": period_start,
                    "$lte": period_end
                }
            }
            ids = [x["_id"] for x in self._result_collection.find(query, {"_id": 1})]
            keep_ids.extend(ids)

        remove = {
            "contractId": contract,
            "_id": { '$nin': keep_ids }
        }

        # Identify them
        invalids_cursor = self._result_collection.find(remove,
                                                       {self._period_key: 1})
        to_delete = [x[self._period_key] for x in invalids_cursor]
        # Delete them

        self._result_collection.remove(remove)
        # Notify deleted
        return to_delete

    def validate_contract(self, values, contract, period=None, log_errors=True):
        """ Validate the contract according to the values dict.
        " Values dict contain period as key and value as value.
        " Will create the error log in collection according to log_errors param
        "
        " values example:
        " {'201301': 42.2, '201302': 75.3}
        "
        " OT503 specific
        " This ot uses daily measures will check if the sum of the dailys
        " is equal to the stored monthly. If the sum of the dailys is equal
        " to the month the dailys are considered valid, deleted otherwise
        """

        if period:
            # Discard other values
            values = {period: values[period]}

        # Different algorism with super validate_contract
        # here we will delete al periods not in valid_periods
        valid_periods = []
        for v_period, v_value in values.iteritems():
            error = None
            error_details = {}
            cached_value = self._get_period_sum(contract, v_period)
            if cached_value == None:
                error = NO_RESULT_ERROR
            elif not self._is_valid(cached_value, v_value):
                # Stored and empowering result missmatch
                error = WRONG_VALUE_ERROR
                error_details.update({
                    'expected': v_value,
                    'cached': cached_value
                })
                self._delete_month_period(contract, v_period)
            else:
                # Result is OK
                # All periods not in this list will be deleted
                valid_periods.append(v_period)

            if error and log_errors:
                self._insert_error(contract, v_period, error,
                                   error_details)

        if period and period not in valid_periods:
            # Only checking one period and is invalid
            self._delete_month_period(contract, period)
        elif not period:
            # We are checking all contract data
            # must delete all not checked results
            deleteds = self._delete_all_periods_except(contract, valid_periods)
            error = NO_STORED_ERROR
            for deleted in deleteds:
                self._insert_error(contract, deleted, error)
        else:
            # Period specified and is valid -> OK nothing to do
            pass

