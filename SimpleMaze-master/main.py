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

state = {
    "current_room": "corridor",
    "previous_room": "corridor",
    "visited": {
        "classroom2015": False,
        "projectroom3": False,
        "equinoxroom": False,
        "classroom2031": False,
        "teacherroom": False,
        "storageroom": False,
    },
    "inventory": []
}

# Connect to the database (creates GameSave.db if it doesn't exist)
connection = sqlite3.connect("GameSave.db")
crsr = connection.cursor()

crsr.execute("""
CREATE TABLE IF NOT EXISTS saves (
    saveName TEXT PRIMARY KEY,
    state TEXT,
    saveTime REAL
)
""")
connection.commit()

fileName = input("what is the name of your save file, if you want to start a new one type \"no save\": ").lower()

time_played = 0.0

crsr.execute("SELECT * FROM saves")
saves = crsr.fetchall()

#print(saves)

for i in saves:
    if fileName in i:
        state = i[1]
        state = ast.literal_eval(state)
        time_played = i[2]
        print(f"💾 Save file '{fileName}' loaded. Total time played so far: {time_played:.2f} seconds.")
        break

startTime = time.time()
# Starttime is in the main function and is also the seconds since the epoch but was taken earlier, when you enter your file to run the game.

while True:
    current = state["current_room"]

    if current == "corridor":
        state["current_room"] = enterCorridor(state, fileName, time_played, startTime)

    elif current == "studylandscape":
        state["current_room"] = enterStudyLandscape(state)

    elif current == "classroom2015":
        state["current_room"] = enterClassroom2015(state, fileName, time_played, startTime)

    elif current == "projectroom3":
        state["current_room"] = enterProjectRoom3(state)

    elif current=="equinoxroom":
        state["current_room"]=enterEquinoxroom(state, fileName, time, startTime)
    
    elif current=="classroom2031":
        state["current_room"]=enterClassroom2031(state, fileName, time_played, startTime)

    elif current=="teacherroom":
        state["current_room"] = enterTeacherroom(state, fileName, time_played, startTime)

    elif current=="storageroom":
        state["current_room"]=enterStorageroom(state, fileName, time_played, startTime)

    else:
        print("Unknown room. Exiting game.")
        break
