# imports
import streamlit as st
from datetime import datetime, timedelta, date
from db.db import *
import plotly.express as px
import pandas as pd

# set app layout to full page
st.set_page_config(layout = "wide")

# main streamlit app
def main():
    st.title("Room Booking")

    # add room section
    room_number = st.text_input('**Room Number:**', key = "room_number")
    capacity = st.text_input('**Capacity:**', key = "capacity")
    building = st.text_input('**Building:**', key = "building")

    if st.button('Add Room'):
        if room_number:
            if capacity:
                if building:
                    try:
                        add_room(room_number, capacity, building)
                        st.success(f"Room {room_number} added successfully.")
                    except sqlite3.IntegrityError as e:
                        if 'UNIQUE constraint failed: ROOMS.room_id' in str(e):
                            st.error('Room already exists!')
                        else:
                            st.error('An error occurred while adding the room. Please try again.')
                else:
                    st.warning("Please enter the building.")
            else:
                st.warning("Please enter the capacity.")
        else:
            st.warning("Please enter the room number.")

    # view rooms
    st.header('Rooms List')
    rooms = get_rooms()
    room_ids = []
    for room in rooms:
        room_id, capacity, building = room
        room_ids.append(room_id)
        delete_button_id = f'delete_button_{room_id}'

        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        with col1:
            st.write(f'**Room Number: {room_id}**')
        with col2:
            if st.button('**X**', key = delete_button_id, type = "primary"):
                delete_room(room_id)
                st.success('Room deleted successfully.')
                st.rerun()
        
        st.write('---')
    
    # room booking
    st.title("Book Room")
    room_selected = st.selectbox("Choose a room", options = room_ids)
    dates_choosen = st.date_input(
                'Choose the date',
                date.today(),
                format = 'MM.DD.YYYY'
            )

    start_time = st.time_input("Start time", value = None)
    end_time = st.time_input("End time", value = None)
    event = st.text_input("Event")
    booked_for = st.text_input("Booked by")
    
    if st.button('Book Room'):
        if room_selected and dates_choosen and start_time and end_time and event and booked_for:
            add_booking(room_selected, dates_choosen, start_time, end_time, event, booked_for)
            st.success("Booking Successful")
        else:
            st.warning('Please enter all the fields.')


if __name__ == '__main__':
    main()
