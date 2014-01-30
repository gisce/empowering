from marshmallow import Serializer, fields


class CustomerAddress(Serializer):
    buildingId = fields.UUID()
    city = fields.String()
    cityCode = fields.String()
    countryCode = fields.String()
    street = fields.String()
    postalCode = fields.String()


class CustomerProfileEducationLevel(Serializer):
    edu_prim = fields.Integer()
    edu_sec = fields.Integer()
    edu_uni = fields.Integer()
    edu_noStudies = fields.Integer()


class CustomerProfile(Serializer):
    totalPersonNumber = fields.Integer()
    minorsPersonsNumber = fields.Integer()
    workingAgePersonsNumber = fields.Integer()
    retiredAgePersonsNumber = fields.Integer()
    malePersonsNumber = fields.Integer()
    femalePersonsNumber = fields.Integer()
    educationLevel = fields.Nested(CustomerProfileEducationLevel)


class Customer(Serializer):
    customerId = fields.UUID()
    address = fields.Nested(CustomerAddress)
    profile = fields.Nested(CustomerProfile)


class Device(Serializer):
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    deviceId = fields.UUID()


class Contract(Serializer):
    payerId = fields.UUID()
    ownerId = fields.UUID()
    signerId = fields.UUID()
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
    type = fields.Select(['electricityConsumption'])
    unit = fields.Select(['kWh', 'Wh'])
    period = fields.Select(['INSTANT', 'CUMULATIVE', 'PULSE'])


class Measurement(Serializer):
    type = fields.Select(['electricityConsumption'])
    timestamp = fields.DateTime(format='iso')
    value = fields.Float()


class AmonMeasure(Serializer):
    deviceId = fields.UUID()
    meteringPointId = fields.UUID()
    readings = fields.List(fields.Nested(Reading))
    measurements = fields.List(fields.Nested(Measurement))
