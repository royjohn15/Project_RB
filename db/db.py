import sqlite3

# add room
def add_room(room_number, capacity, building):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO ROOMS (room_id, capacity, building) VALUES (?, ?, ?)', (room_number, capacity, building))
    conn.commit()
    conn.close()

# retrieve rooms
def get_rooms():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT room_id, capacity, building FROM ROOMS')
    rooms = c.fetchall()
    conn.close()
    return rooms

# update room
# def update_room(room_id, capacity, building):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('UPDATE ROOMS SET capacity = ? && building = ?', (capacity, building))
#     conn.commit()
#     conn.close()

# delete room
def delete_room(room_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM ROOMS WHERE room_id = ?', (room_id,))
    conn.commit()
    conn.close()

# add booking
def add_booking(room_number, date, start_time, end_time, booked_for, booked_by):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO BOOKINGS (room_id, date, start_time, end_time, booked_for, booked_by) VALUES (?, ?, ?, ?, ?, ?)', (room_number, str(date), str(start_time), str(end_time), booked_for, booked_by))
    conn.commit()
    conn.close()

# retrieve bookings
def get_bookings():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT room_id, date, start_time, end_time, booked_for, booked_by  FROM BOOKINGS')
    bookings = c.fetchall()
    conn.close()
    return bookings




