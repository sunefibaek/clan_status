import requests
import os
import pandas as pd
import json
import streamlit as st
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


# Building the streamlit app #
st.markdown("""  
    ##Clan member status
""") 

clan_tag = st.text_input("Enter clan tag in the form #nnnnnnnn:")

if st.button('Convert to Excel'):    
    towrite = io.BytesIO()    
    df[columns].to_excel(towrite, index=False)    
    towrite.seek(0)    
    st.download_button(    
        label="Download Excel File",    
        data=towrite,    
        file_name='dataframe.xlsx',    
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'    
    ) 

if st.button('Refresh'):
    df_2 = call_api_for_tags(call_clan_api, clan_id)
    st.write(df_2)
else:
    st.write("Please enter the Clan ID and press 'Refresh' to see the data.")

st.markdown("""
    ## Source Code
    The code and documentation for this Streamlit app is available on GitHub: [GitHub Repository](https://github.com/sunefibaek/clan_status)
""")