import streamlit as st
import plotly.express as px
from components.components import addRoom, getRooms, addBooking


def main():
    tabs = st.tabs(['View Bookings', 'Book Room', 'View Rooms', 'Add Rooms', 'Room Statistics'])

    with tabs[1]:
        addBooking()

    with tabs[2]:
        getRooms()

    with tabs[3]:
        addRoom()

if __name__ == '__main__':
    main()
