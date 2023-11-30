import asyncio  # Standard library imports
import datetime
import io
import os

import coc  # Third-party imports
import pandas as pd
import streamlit as st

async def get_coc_client():
    coc_client = coc.Client()
    try:
        #await coc_client.login(os.getenv('COC_API_EMAIL'), os.getenv('COC_API_PASSWORD'))
        await coc_client.login(st.secrets['COC_API_EMAIL'], st.secrets["COC_API_PASSWORD"])
    except coc.InvalidCredentials as error:
        exit(error)
    return coc_client

async def get_clan_members_war_status(tag):
    coc_client = await get_coc_client()
    try:
        clan = await coc_client.get_clan(tag)
        clan_name = clan.name
        members = clan.members
        data = []
        for member in members:
            player = await coc_client.get_player(member.tag)
            data.append({
                'player': player.name,
                'role': member.role,
                'warStatus': player.war_opted_in,
                'warStars': player.war_stars,
                'townHallLevel': player.town_hall,
                'townHallWeaponLevel': player.town_hall_weapon
            })
        members_war_status = pd.DataFrame(data)
        players_ready_for_war = members_war_status[members_war_status['warStatus'] == True].shape[0]
        return members_war_status, players_ready_for_war, clan_name
    finally:
        await coc_client.close()

async def get_clan_name(tag):
    coc_client = await get_coc_client()
    try:
        clan = await coc_client.get_clan(tag)
        return clan.name
    finally:
        await coc_client.close()

# Building the streamlit app #
"""
## Clan member war status

This app shows the war status of all members in a clan. 
"""

clan_tag = st.text_input("Clan tag:")

if 'fetch_pressed' not in st.session_state:
    st.session_state.fetch_pressed = False

if st.button('Go fetch!'):
    st.session_state.fetch_pressed = True
    st.session_state.members_war_status, st.session_state.ready_for_war, st.session_state.clan_name = asyncio.run(get_clan_members_war_status(clan_tag))
    st.write("There are currently " + str(st.session_state.ready_for_war) + " players ready for war in " + str(st.session_state.clan_name) + ".")
    st.write(st.session_state.members_war_status)
    st.divider()

if st.session_state.fetch_pressed:
    if st.button('Generate Excel File'):
        towrite = io.BytesIO()
        st.session_state.members_war_status.to_excel(towrite, index=False)
        towrite.seek(0)
        st.download_button(
            label="Download Excel File",
            data=towrite,
            file_name="member_status_" + st.session_state.clan_name.replace(" ", "_") + "_" + datetime.datetime.now().strftime("%Y_%m_%d_%I_%M_%S") + ".xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
else:
    st.write("""
             Enter a clan tag and press 'Go fetch!' to display the data.
             You can find the clan tag just below the clan name in the My Clan info screen.
             """)

st.divider()

"""
The code and documentation for this Streamlit app is available on GitHub: [GitHub Repository](https://github.com/sunefibaek/clan_status)
"""