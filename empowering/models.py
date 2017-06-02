from marshmallow import Schema, fields
from marshmallow.validate import OneOf


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
    buildingType = fields.Str(validate=OneOf(['Single_house', 'Apartment']))
    dwellingPositionInBuilding = fields.Str(validate=OneOf(['first_floor',
                                                            'middle_floor',
                                                            'last_floor',
                                                            'other']))
    dwellingOrientation = fields.Str(validate=OneOf(['S', 'SE', 'E', 'NE',
                                                     'N', 'NW', 'W', 'SW']))
    buildingWindowsType = fields.Str(validate=OneOf(['single_panel',
                                                     'double_panel',
                                                     'triple_panel',
                                                     'low_emittance',
                                                     'other']))
    buildingWindowsFrame = fields.Str(validate=OneOf(['PVC',
                                                      'wood',
                                                      'aluminium',
                                                      'steel',
                                                      'other']))
    buildingHeatingSource = fields.Str(validate=OneOf(['electricity', 'gas',
                                                       'gasoil',
                                                       'district_heating',
                                                       'biomass',
                                                       'other']))
    buildingHeatingSourceDhw = fields.Str(validate=OneOf(['electricity',
                                                          'gas', 'gasoil',
                                                          'district_heating',
                                                          'biomass', 'other']))
    buildingSolarSystem = fields.Str(validate=OneOf(['PV',
                                                     'solar_thermal_heating',
                                                     'solar_thermal_DHW',
                                                     'other',
                                                     'not_installed']))


class CustomerProfileEducationLevel(Schema):
    edu_prim = fields.Integer()
    edu_sec = fields.Integer()
    edu_uni = fields.Integer()
    edu_noStudies = fields.Integer()


class CustomerProfile(Schema):
    totalPersonsNumber = fields.Integer()
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
    dateStart = fields.DateTime(format='iso')
    dateEnd = fields.DateTime(format='iso')
    contractId = fields.String()
    tariffId = fields.String()
    power = fields.Integer()
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
    type = fields.Str(validate=OneOf(['electricityConsumption',
                                      'electricityKiloVoltAmpHours',
                                      'heatConsumption',
                                      'gasConsumption',
                                      'estimatedElectricityConsumption',
                                      'estimatedElectricityKiloVoltAmpHours',
                                      'estimatedHeatConsumption',
                                      'estimatedGasConsumption']))
    unit = fields.Str(validate=OneOf(['kWh', 'Wh']))
    period = fields.Str(validate=OneOf(['INSTANT', 'CUMULATIVE', 'PULSE']))


class Measurement(Schema):
    type = fields.Str(validate=OneOf(['electricityConsumption']))
    timestamp = fields.DateTime(format='iso')
    value = fields.Float()


class AmonMeasure(Schema):
    deviceId = fields.UUID()
    meteringPointId = fields.UUID()
    readings = fields.List(fields.Nested(Reading))
    measurements = fields.List(fields.Nested(Measurement))


class ResidentialTimeofuseMeasurement(Schema):
    type = fields.Str(validate=OneOf(['electricityConsumption']))
    timestamp = fields.DateTime(format='iso')
    p1 = fields.Float()
    p2 = fields.Float()
    p3 = fields.Float()


class ResidentialTimeofuseAmonMeasure(Schema):
    deviceId = fields.UUID()
    meteringPointId = fields.UUID()
    readings = fields.List(fields.Nested(Reading))
    measurements = fields.List(fields.Nested(ResidentialTimeofuseMeasurement))

