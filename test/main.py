from typing import Type
import json
import pathlib
from custom_components.uconnect_sensor.uconnect_api import Uconnect_API
from custom_components.uconnect_sensor.uconnect import Uconnect_Information, Uconnect_location
#from .uconnect_api import Uconnect_API


def main():
    
    p = pathlib.Path(__file__).parent / '_test_creds.json'
    
    print(p)
  
    # Opening JSON file
    f = open(p.resolve())
    data = json.load(f)
    
    
    
    api = Uconnect_API(data['username'], data['password'], data['pin'] )
    #data = api.fetch_data("svla")
    #data = api.fetch_data()
    
    #car_information = Uconnect_Information(data)
    #print(car_information)
    
    #data = api.post_data('DEEPREFRESH','ev')
    #print(data)
    
    data = api.fetch_data_with_payload('location/lastknown', 'location')
    location = Uconnect_location(data).get_data()
    #print(json.dumps(location, indent=4, sort_keys=True))
    
    print(json.dumps(data, indent=4, sort_keys=True))
if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()