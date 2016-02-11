from empowering.service import EmpoweringResource
from empowering.utils import searchparams_to_querystring


class OTStatus(EmpoweringResource):
    path = 'module_task_reports'

    def pull(self, ot=None):
        search_params = []

        if ot:
            if type(ot) is not str:
                ot = str(ot).lower()
            param = ('module', '=', ot)
            search_params.append(param)

        query = searchparams_to_querystring(search_params)
        return self.multiget(where=query)
