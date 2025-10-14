# -----------------------------------------------------------------------------
# File: main.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
import sqlite3
import time
import ast

from rooms import enterCorridor, enterStudyLandscape, enterClassroom2015, enterProjectRoom3, enterEquinoxroom, enterClassroom2031,enterTeacherroom, enterStorageroom

print("****************************************************************************")
print("*                      Welcome to the School Maze!                         *")
print("*        Your goal is to explore all important rooms in the school.        *")
print("*    You may need to solve challenges to collect items and unlock rooms.   *")
print("*               Once you've visited all rooms, you win!                    *")
print("****************************************************************************")
#--------------------
# Path to your SQLite database
db_path = "NewSave.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ask for the save file name
fileName = input("Enter save file name: ").strip()

# 1. Find the save record
cursor.execute("""
    SELECT saveId, currentId, previousId, time
    FROM Saves
    WHERE saveName = ?
    LIMIT 1
""", (fileName,))
row = cursor.fetchone()

if row:
    save_id, current_id, previous_id, time_played = row

    # 2. Resolve current_room and previous_room names
    cursor.execute("SELECT roomName FROM Rooms WHERE roomId = ?", (current_id,))
    current_room_row = cursor.fetchone()
    current_room = current_room_row[0] if current_room_row else None

    cursor.execute("SELECT roomName FROM Rooms WHERE roomId = ?", (previous_id,))
    previous_room_row = cursor.fetchone()
    previous_room = previous_room_row[0] if previous_room_row else None

    # 3. Build visited dictionary
    cursor.execute("""
        SELECT r.roomName, srs.visited
        FROM SaveRoomState srs
        JOIN Rooms r ON r.roomId = srs.roomId
        WHERE srs.saveId = ?
    """, (save_id,))
    visited = {room_name: bool(visited_int) for room_name, visited_int in cursor.fetchall()}

    # 4. Build inventory list
    cursor.execute("""
        SELECT i.itemName
        FROM SaveInventory si
        JOIN Items i ON i.itemId = si.itemId
        WHERE si.saveId = ?
    """, (save_id,))
    inventory = [item_name for (item_name,) in cursor.fetchall()]

    # 5. Construct state
    state = {
        "current_room": current_room,
        "previous_room": previous_room,
        "visited": visited,
        "inventory": inventory
    }

    # Print results
    print("State loaded successfully:\n")
    print(state)
    print(f"\nTime played: {time_played}")

else:
    print(f"No save file named '{fileName}' found in the database.")

# Close connection
conn.close()

#------------------


startTime = time.time()
# Starttime is in the main function and is also the seconds since the epoch but was taken earlier, when you enter your file to run the game.

while True:
    current = state["current_room"]

    if current == "corridor":
        state["current_room"] = enterCorridor(state, fileName, time_played, startTime)

    elif current == "studylandscape":
        state["current_room"] = enterStudyLandscape(state, fileName, time_played, startTime)

    elif current == "classroom2015":
        state["current_room"] = enterClassroom2015(state, fileName, time_played, startTime)

    elif current == "projectroom3":
        state["current_room"] = enterProjectRoom3(state, fileName, time_played, startTime)

    elif current=="equinoxroom":
        state["current_room"]=enterEquinoxroom(state, fileName, time_played, startTime)
    
    elif current=="classroom2031":
        state["current_room"]=enterClassroom2031(state, fileName, time_played, startTime)

    elif current=="teacherroom":
        state["current_room"] = enterTeacherroom(state, fileName, time_played, startTime)

    elif current=="storageroom":
        state["current_room"]=enterStorageroom(state, fileName, time_played, startTime)

    else:
        print("Unknown room. Exiting game.")
        break
