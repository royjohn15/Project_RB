import streamlit as st
from .db import *


def addRoom():
    col1, col2, col3 = st.columns(3)
    with col1:
        room_number = st.text_input('**Room Number:**', key="room_number", help="Enter the room number, e.g., 101.")
    with col2:
                capacity = st.text_input('**Capacity:**', key="capacity", help="Enter the capacity, e.g., 20.")
    with col3:
        building = st.text_input('**Building:**', key="building", help="Enter the building name or code.")

    if st.button('Add Room'):
        if room_number and capacity and building:
            try:
                add_room(room_number, capacity, building)
                st.success(f"Room {room_number} added successfully.")
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: ROOMS.room_id' in str(e):
                    st.error('Room already exists!')
                else:
                    st.error('An error occurred while adding the room. Please try again.')
        else:
            st.warning("Please fill in all fields.")


