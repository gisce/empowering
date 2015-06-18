# Empowering python library

## Example

```python
from empowering import Empowering

emp = Empowering(company_id, username, password, key_file, cert_file)

# Create a new contract
emp.contracts().create({
  "payerId": "payerID-123",
  "ownerId": "ownerID-123",
  "signerId": "signerID-123",
  "power": 123,
  "dateStart": "2013-10-11T16:37:05Z",
  "dateEnd": None,
  "contractId": "contractID-123",
  "customer":{
    "customerId": "payerID-123",
    "address": {
      "city": "city-123",
      "cityCode": "cityCode-123",
      "countryCode": "ES",
      "country": "Spain",
      "street": "street-123",
      "postalCode": "postalCode-123"
    }
  },
  "meteringPointId": "c1759810-90f3-012e-0404-34159e211070",
  "devices": [
    {
      "dateStart": "2013-10-11T16:37:05Z",
      "dateEnd": None,
      "deviceId": "c1810810-0381-012d-25a8-0017f2cd3574"
    }
  ],
  "version": 1,
  "activityCode": "activityCode",
  "tariffId": "tariffID-123",
})

# Update a contract

emp.contract("contractID-123").update({
    "power": 687,
})

```
