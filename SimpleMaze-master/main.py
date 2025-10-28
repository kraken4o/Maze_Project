# -----------------------------------------------------------------------------
# File: main.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
import sqlite3
import time

from rooms import enterCorridor, enterStudyLandscape, enterClassroom2015, enterProjectRoom3, enterEquinoxroom, enterClassroom2031,enterTeacherroom, enterStorageroom

print("****************************************************************************")
print("*                      Welcome to the School Maze!                         *")
print("*        Your goal is to explore all important rooms in the school.        *")
print("*    You may need to solve challenges to collect items and unlock rooms.   *")
print("*               Once you've visited all rooms, you win!                    *")
print("****************************************************************************")
#--------------------
conn = sqlite3.connect("GameSave.db")
crsr = conn.cursor()
fileName = ""
state = {}

flag = True
while flag:
    fileName = input("what is the name of your save file? if you want to create a file enter \"new save\": ").strip()

    if fileName == "new save":
        fileName = input("what would you like to name your file: ").strip()
        crsr.execute("""SELECT saveName FROM saves WHERE saveName = ?""", (fileName,))
        fetchedName = crsr.fetchone()
        if fetchedName:
            print("there is already a save file with this name")
        else:
            state = {'current_room': 'corridor',
                     'previous_room': 'corridor',
                     'visited': {'classroom2015': False,
                                 'projectroom3': False,
                                 'equinoxroom': False,
                                 'classroom2031': False,
                                 'teacherroom': False,
                                 'storageroom': False,
                                 'studylandscape': False},
                     'inventory': []}
            time_played = 0.0
            percentPlayed = 0.0
            flag = False
    else:

        crsr.execute("""SELECT saveId FROM Saves WHERE saveName = ?""", (fileName,))
        something = crsr.fetchone()
        if something:
            saveId = something[0]
        else:
            print("there is no save file with this name")
            continue


        crsr.execute("""SELECT time FROM saves WHERE saveName = ?""", (fileName,))
        time_played = crsr.fetchone()[0]


        crsr.execute("""SELECT roomName, roomId FROM Rooms, Saves WHERE roomId = currentId AND saveId = ?""", (saveId,))
        currentRoomData = crsr.fetchone()
        currentRoom = currentRoomData[0]
        currentId = currentRoomData[1]

        crsr.execute("""SELECT roomName, roomId FROM Rooms, Saves WHERE roomId = previousId AND saveId = ?""", (saveId,))
        previousRoomData = crsr.fetchone()
        previousRoom = previousRoomData[0]
        previousId = previousRoomData[1]

        crsr.execute("""
                SELECT r.roomName, srs.visited
                FROM SaveRoomState srs
                JOIN Rooms r ON r.roomId = srs.roomId
                WHERE srs.saveId = ?
            """, (saveId,))
        visited = {room_name: bool(visited_int) for room_name, visited_int in crsr.fetchall()}


        crsr.execute("""
                SELECT i.itemName
                FROM SaveInventory si
                JOIN Items i ON i.itemId = si.itemId
                WHERE si.saveId = ?
            """, (saveId,))
        inventory = [item_name for (item_name,) in crsr.fetchall()]

        crsr.execute("""SELECT completion FROM saves WHERE saveId = ?""", (saveId,))
        percentPlayed = crsr.fetchone()[0]

        state = {
            "current_room": currentRoom,
            "previous_room": previousRoom,
            "visited": visited,
            "inventory": inventory
        }
        flag = False

#------------------
# Time in seconds since epoch at the start of the current game instance.
startTime = time.time()



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
