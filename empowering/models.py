from marshmallow import Serializer, fields


class CustomerAddress(Serializer):
    city = fields.String()
    cityCode = fields.String()
    countryCode = fields.String()
    street = fields.String()
    postalCode = fields.String()


class Customer(Serializer):
    customerId = fields.UUID()
    address = fields.Nested(CustomerAddress)


class Device(Serializer):
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    deviceId = fields.UUID()


class Contract(Serializer):
    companyId = fields.Integer()
    ownerId = fields.UUID()
    payerId = fields.UUID()
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    contractId = fields.String()
    tariffId = fields.String()
    power = fields.Integer()
    version = fields.Integer()
    activityCode = fields.String()
    meteringPointId = fields.UUID()
    customer = fields.Nested(Customer)
    devices = fields.List(fields.Nested(Device))


class Reading(Serializer):
    type = fields.Selection(['electricityConsumption'])
    unit = fields.Selection(['kWh', 'Wh'])
    period = fields.Selection(['INSTANT', 'CUMULATIVE', 'PULSE'])


class Measurement(Serializer):
    type = fields.Selection(['electricityConsumption'])
    timestamp = fields.DateTime(format='iso')
    value = fields.Float()


class AmonMeasure(Serializer):
    companyId = fields.Integer()
    deviceId = fields.UUID()
    meteringPointId = fields.UUID()
    readings = fields.List(fields.Nested(Reading))
    measurements = fields.List(fields.Nested(Measurement))
