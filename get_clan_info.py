import requests
import os
import pandas as pd
import json

clan_tag = "#V80U2J88"

def call_clan_api(tag):
    processed_tag = tag.replace("#", "%23")

    bearer_token = os.environ.get("COC_API_TOKEN")

    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    url = f"https://api.clashofclans.com/v1/clans/{processed_tag}/members"
    response = requests.get(url, headers=headers)

    df = pd.json_normalize(response.json()['items'])
    df_2 = df.drop(columns=[col for col in df.columns if col not in ['tag', 'name', 'role', 'townHallLevel']])

    return df_2
 
def call_api_for_tags(call_clan_api, tag):    
    df_2 = call_clan_api(tag)  
    api_data = []  
  
    for tag in df_2['tag']:    
        processed_tag = tag.replace("#", "%23")    
  
        url = f"https://api.clashofclans.com/v1/players/{processed_tag}"    
        bearer_token = os.environ.get("COC_API_TOKEN")    
            
        headers = {    
            "Authorization": f"Bearer {bearer_token}"    
        }            
  
        response = requests.get(url, headers=headers)    
        data = response.json()  
  
        war_preference = data.get('warPreference', None)  
        town_hall_weapon_level = data.get('townHallWeaponLevel', None)  
  
        api_data.append({'warPreference': war_preference, 'townHallWeaponLevel': town_hall_weapon_level})  
  
    df_api = pd.DataFrame(api_data)  
  
    df_2 = pd.concat([df_2, df_api], axis=1)  
  
    return df_2  

print(call_api_for_tags(call_clan_api, clan_tag))