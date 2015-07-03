from marshmallow import Schema, fields


class Integer(fields.Integer):
    def __init__(self, default=None, **kwargs):
        super(Integer, self).__init__(default=default, **kwargs)


class CustomerAddress(Schema):
    buildingId = fields.UUID()
    city = fields.String()
    cityCode = fields.String()
    countryCode = fields.String()
    street = fields.String()
    postalCode = fields.String()


class CustomerProfileEducationLevel(Schema):
    edu_prim = Integer()
    edu_sec = Integer()
    edu_uni = Integer()
    edu_noStudies = Integer()


class CustomerProfile(Schema):
    totalPersonNumber = Integer()
    minorsPersonsNumber = Integer()
    workingAgePersonsNumber = Integer()
    retiredAgePersonsNumber = Integer()
    malePersonsNumber = Integer()
    femalePersonsNumber = Integer()
    educationLevel = fields.Nested(CustomerProfileEducationLevel)


class Customer(Schema):
    customerId = fields.UUID()
    address = fields.Nested(CustomerAddress)
    profile = fields.Nested(CustomerProfile)


class Device(Schema):
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    deviceId = fields.UUID()


class Contract(Schema):
    contractId = fields.String()
    ownerId = fields.UUID()
    payerId = fields.UUID()
    signerId = fields.UUID()
    power = Integer()
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    weatherStationId = fields.String()
    activeUser = fields.Bool()
    activeUserDate = fields.Bool()
    experimentalGroupUser = fields.Bool()
    experimentalGroupUserTest = fields.Bool()
    customer = fields.Nested(Customer)
    tariffId = fields.String()
    version = Integer()
    activityCode = fields.String()
    meteringPointId = fields.UUID()
    devices = fields.List(fields.Nested(Device))


class Reading(Schema):
    type = fields.Select(['electricityConsumption'])
    unit = fields.Select(['kWh', 'Wh'])
    period = fields.Select(['INSTANT', 'CUMULATIVE', 'PULSE'])


class Measurement(Schema):
    type = fields.Select(['electricityConsumption'])
    timestamp = fields.DateTime(format='iso')
    value = fields.Float()


class AmonMeasure(Schema):
    deviceId = fields.UUID()
    meteringPointId = fields.UUID()
    readings = fields.List(fields.Nested(Reading))
    measurements = fields.List(fields.Nested(Measurement))
