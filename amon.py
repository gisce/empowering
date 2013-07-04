CUPS_CACHE = {}

def get_cups_from_device(device_id):
    if device_id in CUPS_CACHE:
        return CUPS_CAHCE[device_id]
    else:
        

def profile_to_amon(profiles):
    """Return a list of AMON readinds.

    {
        "deviceId": "c1810810-0381-012d-25a8-0017f2cd3574",
        "meteringPointId": "c1759810-90f3-012e-0404-34159e211070",
        "readings": [
            {
                "type":  "electricityConsumption",
                "unit": "kWh",
                "period": "INSTANT",
            },
            {
                "type": "electricityKiloVoltAmpHours",
                "unit": "kVArh",
                "period": "INSTANT",
            }
        ],
        "measurements": [
            {
                "type": "electricityConsumption",
                "timestamp": "2010-07-02T11:39:09Z", # UTC
                "value": 7
            },
            {
                "type": "electricityKiloVoltAmpHours",
                "timestamp": "2010-07-02T11:44:09Z", # UTC
                "value": 6
            }
        ]
    }
    """
    res = []
    if not hasattr(profiles, '__iter__'):
        profiles = [profiles]
    for profile in profiles:
        
    