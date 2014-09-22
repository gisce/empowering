#!/bin/bash
curl --insecure -E /home/erp/src/conf/elgas.pem -H 'X-CompanyId: 8449512768' -X DELETE  https://api.empowering.cimne.com/v1/contracts
