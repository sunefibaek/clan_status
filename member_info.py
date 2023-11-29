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
        await coc_client.login(st.secrets['COC_API_TOKEN'], st.secrets["COC_API_PASSWORD"])
    except coc.InvalidCredentials as error:
        exit(error)
    return coc_client

async def get_clan_members_war_status(tag):
    coc_client = await get_coc_client()
    try:
        clan = await coc_client.get_clan(tag)
        members = clan.members
        data = []
        for member in members:
            player = await coc_client.get_player(member.tag)
            data.append({
                'player': player.name,
                'Role': member.role,
                'warStatus': player.war_opted_in,
                'warStars': player.war_stars,
                'townHallLevel': player.town_hall,
                'townHallWeaponLevel': player.town_hall_weapon
            })
        return pd.DataFrame(data)
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
st.markdown("""
    ## Clan member war status
""")

clan_tag = st.text_input("Enter clan tag in the form #nnnnnnnn:")

if st.button('Go fetch!'):
    war_status_df = asyncio.run(get_clan_members_war_status(clan_tag))
    st.write(war_status_df)
else:
    st.write("Please enter the Clan ID and press 'Refresh' to see the data.")

if st.button('Generate Excel File'):
    towrite = io.BytesIO()
    #clan_member_status(get_clan_members, clan_tag).to_excel(towrite, index=False)
    asyncio.run(get_clan_members_war_status(clan_tag)).to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button(
        label="Download Excel File",
        data=towrite,
        file_name = "member_status_" + asyncio.run(get_clan_name(clan_tag)).replace(" ", "_") + "_" + datetime.datetime.now().strftime("%Y_%m_%d_%I_%M_%S") + ".xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

st.markdown("""
    The code and documentation for this Streamlit app is available on GitHub: [GitHub Repository](https://github.com/sunefibaek/clan_status)
""")