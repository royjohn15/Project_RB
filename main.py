import streamlit as st
import pandas as pd
import plotly.express as px

# Sample booking data
data = {
    "Room": ["Room A", "Room A", "Room B", "Room B", "Room C", "Room C", 'Room D', 'Room E'],
    "Start Time": ["2024-09-25 10:00", "2024-09-25 14:00", "2024-09-25 11:00", 
                   "2024-09-25 15:00", "2024-09-25 09:00", "2024-09-25 13:00", '2024-09-25 17:00', '2024-09-25 17:30' ],
    "End Time": ["2024-09-26 12:00", "2024-09-25 16:00", "2024-09-25 12:00", 
                 "2024-09-25 17:00", "2024-09-25 10:00", "2024-09-25 14:00", '2024-09-25 17:30', '2024-09-25 18:00'],
}

# Create a DataFrame
df = pd.DataFrame(data)
df['Start Time'] = pd.to_datetime(df['Start Time'])
df['End Time'] = pd.to_datetime(df['End Time'])

# Set up Streamlit app
st.title("Room Booking Management")

# Calendar widget for date selection
selected_date = st.date_input("Select a date", pd.to_datetime("2024-09-25"))

# Filter the DataFrame for the selected date
filtered_df = df[(df['Start Time'].dt.date == selected_date) | 
                  (df['End Time'].dt.date == selected_date)]

# Check if there are bookings for the selected date
if not filtered_df.empty:
    # Extract only time components for better axis labeling
    filtered_df['Start Time Only'] = filtered_df['Start Time'].dt.strftime('%H:%M:%S')
    filtered_df['End Time Only'] = filtered_df['End Time'].dt.strftime('%H:%M:%S')

    # Create a Plotly Gantt chart
    fig = px.timeline(filtered_df, 
                      x_start="Start Time", 
                      x_end="End Time", 
                      y="Room", 
                      title=f"Room Booking Timeline for {selected_date}", 
                      labels={"Room": "Room"},
                      color="Room")

    # Update layout for better display
    fig.update_layout(
        xaxis_title="Time", 
        yaxis_title="Room",
        xaxis=dict(
            tickformat='%H:%M',  # Display only time (hours:minutes)
            dtick=1800000,  # Set ticks every half hour (1800000 ms = 30 min)
            showgrid=True,  # Enable gridlines
            tickmode="auto",  # Auto-spacing for ticks
        ),
        yaxis=dict(title_standoff=10)
    )

    # Display the chart
    st.plotly_chart(fig)
else:
    st.write("No bookings available for this date.")
