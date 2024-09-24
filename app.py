import streamlit as st
from datetime import datetime, timedelta, date
from db.db import *
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Set app layout to full page
st.set_page_config(layout="wide")

# Helper function to check for overlapping bookings
def is_overlapping_booking(new_start, new_end, existing_start, existing_end):
    return new_start < existing_end and new_end > existing_start

# Main Streamlit app
def main():
    st.title("Room Booking System")

    # Create tabs for different sections
    tabs = st.tabs(["Add Room", "View Rooms", "Book Room", "View Bookings", "Room Statistics"])

    # Add Room Section
    with tabs[0]:
        st.header("Add Room")
        room_number = st.text_input('**Room Number:**', key="room_number")
        capacity = st.text_input('**Capacity:**', key="capacity")
        building = st.text_input('**Building:**', key="building")

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

    # View Rooms Section
    with tabs[1]:
        st.header('Rooms List')
        rooms = get_rooms()
        room_ids = []
        for room in rooms:
            room_id, capacity, building = room
            room_ids.append(room_id)
            delete_button_id = f'delete_button_{room_id}'

            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.write(f'**Room Number: {room_id}**')
            with col2:
                st.write(f'**Capacity: {capacity}**')
            with col3:
                st.write(f'**Building: {building}**')
            with col4:
                if st.button('**X**', key=delete_button_id, type="primary"):
                    delete_room(room_id)
                    st.success('Room deleted successfully.')
                    st.rerun()

            st.write('---')

    # Book Room Section
    with tabs[2]:
        st.header("Book Room")
        room_selected = st.selectbox("Choose a room", options=room_ids)
        dates_chosen = st.date_input('Choose the date', date.today(), format='DD.MM.YYYY')

        start_time = st.time_input("Start time", value=None)
        end_time = st.time_input("End time", value=None)
        event = st.text_input("Event")
        booked_for = st.text_input("Booked by")

        if st.button('Book Room'):
            if room_selected and dates_chosen and start_time and end_time and event and booked_for:
                # Convert selected times to full datetime objects
                new_start_datetime = datetime.combine(dates_chosen, start_time)
                new_end_datetime = datetime.combine(dates_chosen, end_time)

                # Get existing bookings for the selected room on the same date
                existing_bookings = get_bookings_for_room_on_date(room_selected, dates_chosen)

                overlap_found = False

                for booking in existing_bookings:
                    existing_start_time, existing_end_time = booking[2], booking[3]
                    existing_start_datetime = datetime.combine(dates_chosen, datetime.strptime(existing_start_time, "%H:%M:%S").time())
                    existing_end_datetime = datetime.combine(dates_chosen, datetime.strptime(existing_end_time, "%H:%M:%S").time())

                    if is_overlapping_booking(new_start_datetime, new_end_datetime, existing_start_datetime, existing_end_datetime):
                        overlap_found = True
                        break

                if overlap_found:
                    st.error("Booking overlaps with an existing booking. Please choose a different time.")
                else:
                    add_booking(room_selected, dates_chosen, start_time, end_time, event, booked_for)
                    st.success("Booking Successful")
            else:
                st.warning('Please enter all the fields.')

    # View Bookings Section
    with tabs[3]:
        st.header("View Bookings")
        bookings = get_bookings()
        booking_dict = {
            'Rooms': [],
            'Dates': [],
            'Start Time': [],
            'End Time': [],
            'Booked For': [],
            'Booked By': []
        }
        for booking in bookings:
            room_id, booked_date, start_time, end_time, booked_for, booked_by = booking
            booking_dict['Rooms'].append(room_id)
            booking_dict['Dates'].append(booked_date)
            booking_dict['Start Time'].append(start_time)
            booking_dict['End Time'].append(end_time)
            booking_dict['Booked For'].append(booked_for)
            booking_dict['Booked By'].append(booked_by)

        booking_df = pd.DataFrame(booking_dict)
        booking_df['Start Time'] = pd.to_datetime(booking_df['Start Time'], format = '%H:%M:%S', errors = 'coerce').dt.strftime('%H:%M:%S')
        booking_df['End Time'] = pd.to_datetime(booking_df['End Time'], format = '%H:%M:%S', errors = 'coerce').dt.strftime('%H:%M:%S')
        booking_df['Dates'] = pd.to_datetime(booking_df['Dates']).dt.date
        st.write(booking_df)

        # Search by room and date
        selected_date = st.date_input('Enter the date', date.today())
        filtered_df = booking_df[
            booking_df['Dates'] == selected_date
        ]
        # st.write(filtered_df)

        if not filtered_df.empty:
            fig = px.timeline(
                filtered_df,
                x_start=pd.to_datetime(filtered_df['Start Time'], format = '%H:%M:%S'),
                x_end=pd.to_datetime(filtered_df['End Time'], format = '%H:%M:%S'),
                y='Rooms',
                title=f"Room Booking Timeline for {selected_date}",
                labels={'Room': 'Rooms', 'Event': 'Booked For', 'Booked by': 'Booked By'},
                color='Rooms'
            )
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title='Rooms',
                xaxis=dict(
                    tickformat='%H:%M',
                    dtick=1800000,
                    showgrid=True,
                    tickmode='auto'
                ),
                yaxis=dict(title_standoff=10)
            )
            st.plotly_chart(fig)
        else:
            st.write('No bookings available')

    # Room Statistics Section
    with tabs[4]:
        st.header("Room Usage Statistics")

        # Room Utilization (Percentage of time booked per day)
        room_usage = booking_df.groupby('Rooms').size().reset_index(name='Booking Count')
        fig_utilization = px.bar(room_usage, x='Rooms', y='Booking Count', title="Room Utilization by Number of Bookings")
        st.plotly_chart(fig_utilization)

        # Heatmap for bookings by hour and day of the week
        booking_df['Day of Week'] = pd.to_datetime(booking_df['Dates']).dt.day_name()
        booking_df['Hour'] = pd.to_datetime(booking_df['Start Time']).dt.hour

        heatmap_data = booking_df.groupby(['Day of Week', 'Hour']).size().reset_index(name='Bookings Count')
        fig_heatmap = px.density_heatmap(heatmap_data, x='Hour', y='Day of Week', z='Bookings Count', title="Bookings Heatmap by Hour and Day of the Week")
        st.plotly_chart(fig_heatmap)

        # Peak Time Analysis
        peak_times = booking_df.groupby('Hour').size().reset_index(name='Booking Count')
        fig_peak_times = px.line(peak_times, x='Hour', y='Booking Count', title="Peak Booking Times")
        st.plotly_chart(fig_peak_times)

# Function to get bookings for a specific room on a specific date
def get_bookings_for_room_on_date(room_id, booking_date):
    return [booking for booking in get_bookings() if booking[0] == room_id]

if __name__ == '__main__':
            main()
