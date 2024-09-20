# imports
import streamlit as st
from streamlit_date_picker import date_range_picker, PickerType
from streamlit_calendar import calendar
from components.calendar_features import calendar_configuration
from datetime import datetime, timedelta
from db.db import *



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
    for room in rooms:
        room_id, capacity, building = room
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

    room_id = st.text_input('**Room Number:**', key = 'room_id')
    calendar_options, custom_css = calendar_configuration()
    cal = calendar(options = calendar_options, custom_css = custom_css)
    st.write(cal)


if __name__ == '__main__':
    main()
