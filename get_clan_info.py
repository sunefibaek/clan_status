import requests
import os
import pandas as pd
import json
import streamlit as st
import datetime
#clan_tag = "#V80U2J88"

def get_clan_name(tag):
    processed_tag = tag.replace("#", "%23")

    # bearer_token = os.environ.get("COC_API_TOKEN")
    bearer_token = st.secrets["COC_API_TOKEN"]

    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    url = f"https://api.clashofclans.com/v1/clans/{processed_tag}"
    response = requests.get(url, headers=headers)

    clan_name = response.json().get('name', None)
      # Replace spaces with underscores
    return clan_name

def get_clan_members(tag):
    processed_tag = tag.replace("#", "%23")

    # bearer_token = os.environ.get("COC_API_TOKEN")
    bearer_token = st.secrets["COC_API_TOKEN"]

    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    url = f"https://api.clashofclans.com/v1/clans/{processed_tag}/members"
    response = requests.get(url, headers=headers)

    clan_members_df = pd.json_normalize(response.json()['items'])
    clan_members_df = clan_members_df.drop(columns=[col for col in clan_members_df.columns if col not in ['tag', 'name', 'role', 'townHallLevel']])

    return clan_members_df
 
def clan_member_status(get_clan_members, tag):
    clan_member_status_df = get_clan_members(tag)
    api_data = []

    for tag in clan_member_status_df['tag']:
        processed_tag = tag.replace("#", "%23")

        url = f"https://api.clashofclans.com/v1/players/{processed_tag}"
        
        # bearer_token = os.environ.get("COC_API_TOKEN")
        bearer_token = st.secrets["COC_API_TOKEN"]

        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        war_preference = data.get('warPreference', None)
        town_hall_weapon_level = data.get('townHallWeaponLevel', None)

        api_data.append({'warPreference': war_preference, 'townHallWeaponLevel': town_hall_weapon_level})

    member_status_df = pd.DataFrame(api_data)

    clan_members_df = pd.concat([clan_member_status_df, member_status_df], axis=1)

    return clan_members_df

# Building the streamlit app #
st.markdown("""
    ## Clan member status
""")

clan_tag = st.text_input("Enter clan tag in the form #nnnnnnnn:")

if st.button('Update'):
    clan_members_df = clan_member_status(get_clan_members, clan_tag)
    st.write(clan_members_df)
else:
    st.write("Please enter the Clan ID and press 'Refresh' to see the data.")

if st.button('Download as .xlsx'):
    towrite = io.BytesIO()
    clan_member_status(get_clan_members, clan_tag).to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button(
        label="Download Excel File",
        data=towrite,
        file_name = "member_status_" + get_clan_name(clan_tag).replace(" ", "_") + "_" + datetime.datetime.now().strftime("%d_%m_%Y_%I_%M_%S") + ".xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

st.markdown("""
    The code and documentation for this Streamlit app is available on GitHub: [GitHub Repository](https://github.com/sunefibaek/clan_status)
""")