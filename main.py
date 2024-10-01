import streamlit as st
from components.components import addRoom, getRooms, addBooking, getBookings


def main():
    tabs = st.tabs(['View Bookings', 'Book Room', 'View Rooms', 'Add Rooms'])

    with tabs[0]:
        getBookings()

    with tabs[1]:
        addBooking()
    with tabs[2]:
        getRooms()

    with tabs[3]:
        addRoom()

if __name__ == '__main__':
    main()
