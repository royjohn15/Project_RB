import streamlit as st
from datetime import datetime, date
from db.db import *
import pandas as pd
import plotly.express as px

# Set app layout to full page and apply custom theme
# st.set_page_config(layout="wide", page_title="Room Booking System")

# Helper function to check for overlapping bookings
def is_overlapping_booking(new_start, new_end, existing_start, existing_end):
    return new_start < existing_end and new_end > existing_start

# Main Streamlit app
def main():
    st.markdown("<h1 style='text-align: center;'>Room Booking System</h1>", unsafe_allow_html=True)
    
    # Tabs for different sections
    tabs = st.tabs(["Add Room", "View Rooms", "Book Room", "View Bookings", "Room Statistics"])

    # Add Room Section
    with tabs[0]:
        st.markdown("### 📋 Add Room")
        with st.expander("Add a New Room"):
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

    # View Rooms Section
    with tabs[1]:
        st.markdown("### 🏫 View Rooms")
        rooms = get_rooms()
        if rooms:
            room_df = pd.DataFrame(rooms, columns=["Room Number", "Capacity", "Building"])
            st.dataframe(room_df.reset_index(drop=True))  # Display table without index
        else:
            st.write("No rooms available.")

    # Book Room Section
    with tabs[2]:
        st.markdown("### 🛋️ Book Room")
        
        rooms = get_rooms()
        room_ids = [room[0] for room in rooms]

        if room_ids:
            col1, col2 = st.columns(2)
            with col1:
                room_selected = st.selectbox("Choose a room", options=room_ids)
            with col2:
                dates_chosen = st.date_input('Choose the date', date.today(), format='DD.MM.YYYY')

            col3, col4 = st.columns(2)
            with col3:
                start_time = st.time_input("Start time", value=None)
            with col4:
                end_time = st.time_input("End time", value=None)

            event = st.text_input("Event", help="Name of the event, e.g., Meeting")
            booked_for = st.text_input("Booked by", help="Person responsible for booking")

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
        else:
            st.warning("No rooms available for booking. Please add rooms first.")

    # View Bookings Section
    with tabs[3]:
        st.markdown("### 📅 View Bookings")
        bookings = get_bookings()

        if bookings:
            booking_dict = {
                'Rooms': [],
                'Dates': [],
                'Start Time': [],
                'End Time': [],
                'Booked For': [],
                'Booked By': [],
            }

            for booking in bookings:
                room_id, booked_date, start_time, end_time, booked_for, booked_by = booking  # Ensure you fetch the event as well
                booking_dict['Rooms'].append(room_id)
                booking_dict['Dates'].append(booked_date)
                booking_dict['Start Time'].append(start_time)
                booking_dict['End Time'].append(end_time)
                booking_dict['Booked For'].append(booked_for)
                booking_dict['Booked By'].append(booked_by)

            booking_df = pd.DataFrame(booking_dict)
            booking_df['Start Time'] = pd.to_datetime(booking_df['Start Time'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M:%S')
            booking_df['End Time'] = pd.to_datetime(booking_df['End Time'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M:%S')
            booking_df['Dates'] = pd.to_datetime(booking_df['Dates']).dt.date

            # Toggle button for view selection
            view_selection = st.radio("Select View:", ("Tabular View", "Timeline View"))

            if view_selection == "Tabular View":
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
                styled_df = (
                filtered_df.style
                .set_table_attributes('style="width:100%;border-collapse:collapse;"')  # Table width
                .set_properties(**{'text-align': 'left', 'padding': '10px'})  # Cell padding
                .set_table_styles(
                    [{
                        'selector': 'thead th',
                        'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-size', '14px')]
                    },
                    {
                        'selector': 'tbody tr:nth-child(even)',
                        'props': [('background-color', '#f2f2f2')]
                    },
                    {
                        'selector': 'tbody tr:hover',
                        'props': [('background-color', '#ddd')]
                    }]
                )  # Hide index
            )
                st.write(styled_df)  # Display without index
            else:
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
                        color='Rooms',
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
            st.write('No bookings found.')


    # Room Statistics Section
    with tabs[4]:
        st.markdown("### 📊 Room Usage Statistics")

        bookings = get_bookings()
        if bookings:
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
            booking_df['Start Time'] = pd.to_datetime(booking_df['Start Time'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M:%S')
            booking_df['End Time'] = pd.to_datetime(booking_df['End Time'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M:%S')
            booking_df['Dates'] = pd.to_datetime(booking_df['Dates']).dt.date

            # Room Utilization (Percentage of time booked per day)
            room_usage = booking_df.groupby('Rooms').size().reset_index(name='Booking Count')
            fig_utilization = px.bar(room_usage, x='Rooms', y='Booking Count', title="Room Utilization by Number of Bookings")
            st.plotly_chart(fig_utilization)

            # Heatmap for bookings by hour and day of the week
            booking_df['Day of Week'] = pd.to_datetime(booking_df['Dates']).dt.day_name()
            booking_df['Hour'] = pd.to_datetime(booking_df['Start Time']).dt.hour

            heatmap_data = booking_df.groupby(['Day of Week', 'Hour']).size().reset_index(name='Bookings Count')
            fig_heatmap = px.density_heatmap(
                heatmap_data,
                x='Hour',
                y='Day of Week',
                z='Bookings Count',
                title="Bookings Heatmap by Hour and Day of the Week"
            )
            st.plotly_chart(fig_heatmap)

            # Peak Time Analysis
            peak_times = booking_df.groupby('Hour').size().reset_index(name='Booking Count')
            fig_peak_times = px.line(peak_times, x='Hour', y='Booking Count', title="Peak Booking Times")
            st.plotly_chart(fig_peak_times)
        else:
            st.write("No bookings available to analyze.")

# Function to get bookings for a specific room on a specific date
def get_bookings_for_room_on_date(room_id, booking_date):
    return [booking for booking in get_bookings() if booking[0] == room_id and booking[1] == booking_date]

if __name__ == '__main__':
    main()
