import streamlit as st
from .db import *
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import time

def is_overlapping_booking(new_room, new_start, new_end, existing_room, existing_start, existing_end):
    return new_start < existing_end and new_end > existing_start and new_room == existing_room

st.set_page_config(page_title = 'Room Booking System')
st.markdown("# Room Booking System")

def addRoom():
    st.markdown("### 📋 Add Room")
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
    st.markdown("### 🏫 View Rooms")
    rooms = get_rooms()
    if rooms:
        room_df = pd.DataFrame(rooms, columns=["Room Number", "Capacity", "Building"])
        room_df = room_df.reset_index(drop = True)
        st.dataframe(room_df.reset_index(drop=True), use_container_width = True)  # Display table without index
    else:
        st.write("No rooms available.")

def addBooking():
    st.markdown("### 🛋️ Book Room")
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
                new_end = datetime.combine(date_chosen, end_time)
                existing_bookings = get_bookings_by_date(date_chosen)
                overlapfound = False
                for booking in existing_bookings:
                    existing_room, existing_start_time, existing_end_time = booking[0], booking[1], booking[2]
                    existing_start = datetime.combine(date_chosen, datetime.strptime(existing_start_time, "%H:%M:%S").time())
                    existing_end = datetime.combine(date_chosen,  datetime.strptime(existing_end_time, "%H:%M:%S").time())
                    if is_overlapping_booking(room_selected, new_start, new_end, existing_room, existing_start, existing_end):
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

def getBookings():
    st.markdown("### 📅 View Bookings")
    bookings = get_bookings()
    if bookings:
        booking_dict = {
            'Booking ID' : [],
            'Rooms': [],
            'Dates': [],
            'Start Time': [],
            'End Time': [],
            'Booked For': [],
            'Booked By': [],
        }

        for booking in bookings:
            booking_id, room_id, booked_date, start_time, end_time, booked_for, booked_by = booking
            booking_dict['Booking ID'].append(booking_id)
            booking_dict['Rooms'].append(room_id)
            booking_dict['Dates'].append(booked_date)
            booking_dict['Start Time'].append(start_time)
            booking_dict['End Time'].append(end_time)
            booking_dict['Booked For'].append(booked_for)
            booking_dict['Booked By'].append(booked_by)

        booking_df = pd.DataFrame(booking_dict)
        booking_df['Start Time'] = pd.to_datetime(booking_df['Start Time'], format='%H:%M:%S').dt.strftime('%H:%M:%S')
        booking_df['End Time'] = pd.to_datetime(booking_df['End Time'], format='%H:%M:%S').dt.strftime('%H:%M:%S')
        booking_df['Dates'] = pd.to_datetime(booking_df['Dates']).dt.date

        view_selection = st.radio('Select View:', ('Timeline View', 'Tabular View'))

        if view_selection == 'Timeline View':
            # Filter and visualize bookings by date
            selected_date = st.date_input('Filter by date', date.today())
            filtered_df = booking_df[booking_df['Dates'] == selected_date]

            if not filtered_df.empty:
                fig = px.timeline(
                        filtered_df,
                        x_start=pd.to_datetime(filtered_df['Start Time'], format='%H:%M:%S'),
                        x_end=pd.to_datetime(filtered_df['End Time'], format='%H:%M:%S'),
                        y='Rooms',
                        title=f"Room Booking Timeline for {selected_date}",
                        color='Booked For',
                        hover_data={
                            'Booked For': True,
                            'Booked By': True,
                            'Start Time': False,
                            'End Time': False,
                            'Dates': False,
                        }
                    )
                fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title='Rooms',
                        xaxis=dict(tickformat='%H:%M', dtick=1800000, showgrid=True, tickmode='auto'),
                        yaxis=dict(title_standoff=10)
                    )
                st.plotly_chart(fig)
            else:
                st.write('No bookings available for the selected date.')
        else:
            # Date Filter
            selected_date = st.date_input('Select Date', date.today())
        
            # Room Number Filter
            room_options = booking_df['Rooms'].unique()
            selected_room = st.selectbox('Select Room', options=['All'] + list(room_options))

            # Filter DataFrame based on selections
            if selected_room == 'All':
                filtered_df = booking_df[booking_df['Dates'] == selected_date]
            else:
                filtered_df = booking_df[(booking_df['Dates'] == selected_date) & (booking_df['Rooms'] == selected_room)]
            # --------------
            for i, row in filtered_df.iterrows():
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                col1.write(row['Rooms'])
                col2.write(row['Dates'])
                col3.write(row['Start Time'])
                col4.write(row['End Time'])
                col5.write(row['Booked For'])
                col6.write(row['Booked By'])

                if col7.button('Delete', key = f"delete_{row['Booking ID']}"):
                    st.session_state[f"confirm_delete_{row['Booking ID']}"] = True

                if st.session_state.get(f"confirm_delete_{row['Booking ID']}"):
                    delete_booking(row['Booking ID'])
                    st.success(f"Booking for room {row['Rooms']} on {row['Dates']} deleted")
                    time.sleep(1)
                    st.rerun()
            
    else:
        st.write('No bookings found.')


