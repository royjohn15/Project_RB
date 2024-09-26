import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.express as px
from components.add_room import addRoom


def main():
    tabs = st.tabs(['View Bookings', 'Book Room', 'View Rooms', 'Add Rooms', 'Room Statistics'])

    with tabs[3]:
        addRoom()



if __name__ == '__main__':
    main()
