import json
from homeassistant.const import PERCENTAGE, UnitOfLength, CONF_PIN, CONF_PASSWORD, CONF_USERNAME


class Car_Information():
    def __init__(   self, value: str, 
                    device_class: str, 
                    display_name: str,
                    unit_of_measurement: str = None) -> None:
        self.value = value
        self.device_class = device_class
        self.unit_of_measurement = unit_of_measurement
        self.display_name = display_name
        
    def __str__(self) -> str:
        return f'Name: {self.display_name} | Value: {self.value}'

class Uconnect_location():
    def __init__(self, data) -> None:
        self.latitude = data['latitude']
        self.longitude = data['longitude']
    
    def get_data(self) -> dict:
        
        return_dict = {
            'longitude' : self.longitude,             
            'latitude': self.latitude, 
        }
        
        return return_dict
        
    def __str__(self) -> str:
        
        return_statement = self.get_data()
        
        for key in return_statement:
            return_statement[key] = str(return_statement[key])
        
        return json.dumps(return_statement, indent=4, sort_keys=True)

class Uconnect_Information():
    def __init__(self, data: str) -> None:
        
        battery_infos = data['evInfo']['battery']

        self.charging_level = Car_Information(
                                battery_infos['chargingLevel'],
                                'enum',
                                'Charging Level'
                                )
        self.charging_status = Car_Information(
                                battery_infos['chargingStatus'],
                                'enum',
                                'Charging Status'
                                )
        self.distance_to_empty = Car_Information(
                                battery_infos['distanceToEmpty']['value'],
                                'distance',
                                'Distance to empty',
                                UnitOfLength.KILOMETERS 
                                )
        self.plug_in_status = Car_Information(
                                battery_infos['plugInStatus'],
                                'distance',
                                'Plug in status'
                                )
        self.state_of_charge = Car_Information(
                                battery_infos['stateOfCharge'],
                                'battery',
                                'State of Charge',
                                PERCENTAGE
                                )
        self.total_range = Car_Information(
                                battery_infos['totalRange'],
                                'distance',
                                'Total Range',
                                UnitOfLength.KILOMETERS
                                )
    
    
    def get_data(self) -> dict:
        
        return_dict = {
            'chargingLevel' : self.charging_level,             
            'chargingStatus': self.charging_status, 
            #'distanceToEmpty_unit': self.distance_to_empty_unit,    
            'distanceToEmpty': self.distance_to_empty,   
            'plugInStatus' : self.plug_in_status,        
            'stateOfCharge' : self.state_of_charge,
            'totalRange' :  self.total_range
        }
        
        
        return return_dict
        
    def __str__(self) -> str:
        
        return_statement = self.get_data()
        
        for key in return_statement:
            return_statement[key] = str(return_statement[key])
        
        return json.dumps(return_statement, indent=4, sort_keys=True)