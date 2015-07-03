from marshmallow import Schema, fields


class Integer(fields.Integer):
    def __init__(self, default=None, **kwargs):
        super(Integer, self).__init__(default=default, **kwargs)


class CustomerAddress(Schema):
    buildingId = fields.UUID()
    country = fields.String()
    countryCode = fields.String()
    province = fields.String()
    provinceCode = fields.String()
    city = fields.String()
    cityCode = fields.String()
    street = fields.String()
    postalCode = fields.String()
    parcelNumber = fields.String()


class CustomerBuildingData(Schema):
    buildingConstructionYear = fields.Integer()
    dwellingArea = fields.Integer()
    buildingVolume = fields.Integer()
    buildingType = fields.Select(['Single_house', 'Apartment'])
    dwellingPositionInBuilding = fields.Select(['first_floor', 'middle_floor', 'last_floor', 'other'])
    dwellingOrientation = fields.Select(['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW'])
    buildingWindowsType = fields.Select(['single_panel', 'double_panel', 'triple_panel', 'low_emittance', 'other'])
    buildingWindowsFrame = fields.Select(['PVC', 'wood', 'aluminium', 'steel', 'other'])
    buildingHeatingSource = fields.Select(['electricity', 'gas', 'gasoil', 'district_heating', 'biomass', 'other'])
    buildingHeatingSourceDhw = fields.Select(['electricity', 'gas', 'gasoil', 'district_heating', 'biomass', 'other'])
    buildingSolarSystem = fields.Select(['PV', 'solar_thermal_heating', 'solar_thermal_DHW', 'other', 'not_installed'])


class CustomerProfileEducationLevel(Schema):
    edu_prim = fields.Integer()
    edu_sec = fields.Integer()
    edu_uni = fields.Integer()
    edu_noStudies = fields.Integer()


class CustomerProfile(Schema):
    totalPersonNumber = fields.Integer()
    minorsPersonsNumber = fields.Integer()
    workingAgePersonsNumber = fields.Integer()
    retiredAgePersonsNumber = fields.Integer()
    malePersonsNumber = fields.Integer()
    femalePersonsNumber = fields.Integer()
    educationLevel = fields.Nested(CustomerProfileEducationLevel)

class CustomerCustomisedGroupingCriteria(Schema):
    pass


class CustomerCustomisedServiceParameters(Schema):
    OT101 = fields.String()
    OT103 = fields.String()
    OT105 = fields.String()
    OT106 = fields.String()
    OT109 = fields.String()
    OT201 = fields.String()
    OT204 = fields.String()
    OT401 = fields.String()
    OT502 = fields.String()
    OT503 = fields.String()
    OT603 = fields.String()
    OT603g = fields.String()
    OT701 = fields.String()
    OT703 = fields.String()


class Customer(Schema):
    customerId = fields.UUID()
    address = fields.Nested(CustomerAddress)
    buildingData = fields.Nested(CustomerBuildingData)
    profile = fields.Nested(CustomerProfile)
    customisedGroupingCriteria = fields.Nested(CustomerCustomisedGroupingCriteria)
    customisedServiceParameters = fields.Nested(CustomerCustomisedServiceParameters)


class Device(Schema):
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    deviceId = fields.UUID()


class Contract(Schema):
    payerId = fields.UUID()
    ownerId = fields.UUID()
    signerId = fields.UUID()
    power = Integer()
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    contractId = fields.String()
    tariffId = fields.String()
    version = fields.Integer()
    activityCode = fields.String()
    meteringPointId = fields.UUID()
    weatherStationId = fields.UUID()
    experimentalGroupUser = fields.Boolean()
    experimentalGroupUserTest = fields.Boolean()
    activeUser = fields.Boolean()
    activeUserDate = fields.DateTime(format='iso')
    customer = fields.Nested(Customer)
    devices = fields.List(fields.Nested(Device))


class Reading(Schema):
    type = fields.Select(['electricityConsumption', 'electricityKiloVoltAmpHours', 'heatConsumption', 'gasConsumption',
                          'estimatedElectricityConsumption', 'estimatedElectricityKiloVoltAmpHours',
                          'estimatedHeatConsumption', 'estimatedGasConsumption'])
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
