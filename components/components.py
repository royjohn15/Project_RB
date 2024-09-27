import streamlit as st
from .db import *
import pandas as pd
from datetime import datetime, date

def is_overlapping_booking(new_start, new_end, existing_start, existing_end):
    return new_start < existing_end or new_end > existing_start

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



def getRooms():
    rooms = get_rooms()
    if rooms:
        room_df = pd.DataFrame(rooms, columns=["Room Number", "Capacity", "Building"])
        st.dataframe(room_df.reset_index(drop=True))  # Display table without index
    else:
        st.write("No rooms available.")

def addBooking():
    rooms = get_rooms()
    room_ids = [room[0] for room in rooms]

    if room_ids:
        col1, col2 = st.columns(2)
        with col1:
            room_selected = st.selectbox('Choose a room', options = room_ids)
        with col2:
            date_chosen = st.date_input('Choose the date', date.today(), format = 'DD-MM-YYYY')

        col3, col4 = st.columns(2)
        with col3:
            start_time = st.time_input("Start time", value = None)
        with col4:
            end_time = st.time_input("End time", value = None)
        booked_for = st.text_input("Booked for", help="Name of the event, e.g., Meeting")
        booked_by = st.text_input("Booked by", help="Person responsible for booking")
        if st.button('Book Room'):
            if room_selected and date_chosen and start_time and end_time and booked_for and booked_by:
                new_start = datetime.combine(date_chosen, start_time)
                st.write(new_start)
                new_end = datetime.combine(date_chosen, end_time)
                existing_bookings = get_bookings_by_date(date_chosen)
                overlapfound = False
                for booking in existing_bookings:
                    existing_start_time, existing_end_time = booking[1], booking[2]
                    existing_start = datetime.combine(date_chosen, datetime.strptime(existing_start_time, "%H:%M:%S").time())
                    existing_end = datetime.combine(date_chosen,  datetime.strptime(existing_end_time, "%H:%M:%S").time())
                    if is_overlapping_booking(new_start, new_end, existing_start, existing_end):
                        overlapfound = True
                        break
                if overlapfound:
                    st.error('Booking overlaps with an existing booking. Please choose a different time.')
                else:
                    add_booking(room_selected, date_chosen, start_time, end_time, booked_for, booked_by)
                    st.success('Booking Successful')
            else:
                st.warning('Please enter all the fields')
    else:
        st.warning('No rooms available for booking. Please add rooms first.')



