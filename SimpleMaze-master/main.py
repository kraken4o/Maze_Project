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

from rooms import enterCorridor, enterStudyLandscape, enterClassroom2015, enterProjectRoom3, enterEquinoxroom, enterClassroom2031,enterteacher_room_maze, enterStorageroom

print("****************************************************************************")
print("*                      Welcome to the School Maze!                         *")
print("*        Your goal is to explore all important rooms in the school.        *")
print("*    You may need to solve challenges to collect items and unlock rooms.   *")
print("*               Once you've visited all rooms, you win!                    *")
print("****************************************************************************")

"""state = {
    "current_room": "corridor",
    "previous_room": "corridor",
    "visited": {
        "classroom2015": False,
        "projectroom3": False,
        "equinoxroom": False,
        "classroom2031": False,
        "teacher_room_maze": False,
        "storageroom": False,
    },
    "inventory": []
}"""

connection = sqlite3.connect("GameSave.db")
crsr = connection.cursor()

fileName = input("what is the name of your save file, if you want to start a new one type \"no save\": ").lower()
startTime = time.time()

crsr.execute("SELECT * FROM saves")
saves = crsr.fetchall()

#print(saves)

for i in saves:
    if fileName in i:
        state = i[1]
        state = ast.literal_eval(state)
        time = i[2]
        break




while True:
    current = state["current_room"]

    if current == "corridor":
        state["current_room"] = enterCorridor(state)

    elif current == "studylandscape":
        state["current_room"] = enterStudyLandscape(state)

    elif current == "classroom2015":
        state["current_room"] = enterClassroom2015(state)

    elif current == "projectroom3":
        state["current_room"] = enterProjectRoom3(state)

    elif current=="equinoxroom":
        state["current_room"]=enterEquinoxroom(state)
    
    elif current=="classroom2031":
        state["current_room"]=enterClassroom2031(state, fileName, time, startTime)

    elif current=="teacher_room_maze":
        state["current_room"]=enterteacher_room_maze(state)

    elif current=="storageroom":
        state["current_room"]=enterStorageroom(state)

    else:
        print("Unknown room. Exiting game.")
        break
