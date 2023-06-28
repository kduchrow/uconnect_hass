from typing import Type
import json
from uconnect_api import Uconnect_API
#from .uconnect_api import Uconnect_API


class Uconnect_Information():
    def __init__(self, data: str) -> None:
        
        battery_infos = data['evInfo']['battery']
        self.charging_level             = battery_infos['chargingLevel']
        self.charging_status            = battery_infos['chargingStatus']
        #self.distance_to_empty_unit     = battery_infos['distanceToEmpty']['unit']
        self.distance_to_empty_value    = battery_infos['distanceToEmpty']['value']
        self.plug_in_status             = battery_infos['plugInStatus']
        self.state_of_charge            = battery_infos['stateOfCharge']
        self.total_range                = battery_infos['totalRange']
    
    
    def get_data(self) -> dict:
        
        return_dict = {
            'chargingLevel' : self.charging_level,             
            'chargingStatus':self.charging_status, 
  #          'distanceToEmpty_unit': self.distance_to_empty_unit,    
            'distanceToEmpty_value': self.distance_to_empty_value ,   
            'plugInStatus' : self.plug_in_status    ,        
            'stateOfCharge' : self.state_of_charge ,
            'totalRange' :  self.total_range
        }
        
        
        return return_dict
        
    def __str__(self) -> str:
        
        return json.dumps(self.get_data(), indent=4, sort_keys=True)
            
                


def main():
    api = Uconnect_API()
    data = api.fetch_data()
    
    car_information = Uconnect_Information(data).get_data()
    print(car_information)

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()