# -----------------------------------------------------------------------------
# File: storageroom.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys
import time as t # 'time' module allows us to measure time in seconds
import sqlite3
from .utils import chooseNextRoom

def enterStorageroom(state, saveName, time_played, startTime):
    if not state["visited"]["storageroom"]:
        # Message if you dont have the storage key for your room
        if "storage_key" not in state["inventory"]:
            print("\n🚪 The door to the Storage room is locked.")
            print("You rattle the rusty handle and shove your shoulder against it, but it doesn’t move an inch.")
            print("🔐 A storage key is needed… maybe it’s lying around somewhere in the school.")
            return "corridor"
        #Message if you do have the key to enter
        else:
            print("\n🗝️ You slide the key into the stiff lock and twist until it finally clicks.")
            print("The heavy door creaks open, releasing a puff of dusty air.")
    #message when player enters the room
    print("\n🏫 You step into the Storage Room.")
    print("The room is full of different things sitting on neatly arranged shelves.")
    print("The door shuts behind you with a loud bang. It's completely silent and you start creeping out.")

    #look around command
    def handle_look():

        print("\nYou made your entry and you take a look of the room")
        #message if its the first time visiting storageroom with unopened suitcase
        if not state["visited"]["storageroom"]:
            print("You sense the room is hidden with full of secrets and treasure no one knows about")
            print("The room is dusty, and full of unopened boxes that supposedly havent been open in a long time")
            print("Theres one shining suitcase that strikes your eyes")
            print('A note lies on it, stating "I have keys but open no doors. I have space but no room. You can enter, but you can’t go outside. What am I?"')
            print("Seems like a challenging riddle, maybe it gives me access to whatever is hiding in the suitcase?")
        #message if its not the first time visiting storageroom with opened suitcase
        else:
            print("The shining suitcase has already been opened, you already solved the riddle!")
            if "teacher_key" not in state["inventory"]:
                print("The suitcase has been opened, what is it? Take a look whats inside!")
            else:
                print("Youve already taken the teachers key!")
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    #'?' command
    def handle_help():
        print("\nAvailable commands:")
        print("- look around         : Examine the room and its secret contents.")
        if not state["visited"]["storageroom"]:
            print("- answer <riddle>     : Attempt to solve the riddle.")
        if state["visited"]["storageroom"] and "teacher_key" not in state["inventory"]:
            print("- look inside            : Take a look whats inside the Suitcase.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")
        print("- pause                : Pause the game.")
    #command 'look inside'
    def handle_open(where):
        if where == "inside":
            #if player hasnt solved the riddle yet
            if not state["visited"]["storageroom"]:
                print("❌ I dont see no key. Maybe solving the puzzle will reveal whats in the suitcase.")
            #if the already player has teacher key
            elif "teacher_key" in state["inventory"]:
                print("You already have the key in your backpack.")
            #if the riddle is solved but teachers key not yet taken
            else:
                print("🔑 The suitcase is open and you see a small teachers key in it and a red button.")
                print("You take it and tuck it safely into your backpack.")
                print("You look at the red button hesitating but you still press it.")
                print("The door behind you opens!")

                state["inventory"].append("teacher_key")
        else:
            print(f"There is nothing here to take.")
    # go <place> command
    def handle_go(destination):
        if destination in ["corridor", "back"]:
            print("You open the door and step back into the corridor")
            return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None
    #comman answer <something> - solving suitcase riddle
    def handle_answer(answer):
        #message if you have already solved the riddle
        if state["visited"]["storageroom"]:
            print("✅ You've already solved this challenge.")
        #if you answer any of the three below in the list, its correct
        normalized = answer.strip().lower()
        if normalized in ["keyboard", "keyboards", "a keyboard"]:
            print("✅ Correct!")
            #state changes to visited
            state["visited"]["storageroom"] = True
            print("The Suitcase starts slowy oppening. Look whats inside!")
        else:
            #if you get it wrong the suitcase is about to explode
            print("❌ Incorrect. The suitcase is beeping.")
            print("You think its about to explode so you quickly exit the room.")
            return "corridor"

    def handle_pause(state, saveName, time_played, startTime):
        # state: the dictionary storing current room, previous room, inventory, and visited rooms
        #saveName: the name of the save file (or "no save" if it's a new game)
        #time_played: total time played in previous sessions (in seconds)
        elapsed_time = (t.time() - startTime) + time_played
        flag = True
        conn = sqlite3.connect("GameSave.db")
        cur = conn.cursor()

        # collect relavant IDs of the rooms in the current game file being played
        cur.execute("""SELECT roomId FROM Rooms WHERE roomName = ?""", (state["current_room"],))
        currentId = cur.fetchone()[0]

        cur.execute("""SELECT roomId FROM Rooms WHERE roomName = ?""", (state["previous_room"],))
        previousId = cur.fetchone()[0]

        cur.execute("""SELECT saveId FROM Saves WHERE saveName = ?""", (saveName,))
        saveId = cur.fetchone()

        if saveId:
            saveId = saveId[0]

            #  if there is already a saveID that has the current save name it updates the rooms and time played
            cur.execute(
                "UPDATE Saves SET currentId = ?, previousId = ?, time = ? WHERE saveId = ?",
                (currentId, previousId, float(elapsed_time), saveId)
            )

            # deletes all room states for a save id and iterates through the state of each room and adds it back in
            cur.execute("DELETE FROM SaveRoomState WHERE saveId = ?", (saveId,))
            for room_name, visited in state.get("visited", {}).items():
                cur.execute("SELECT roomId FROM Rooms WHERE roomName = ?", (room_name,))
                r = cur.fetchone()
                if r:
                    cur.execute(
                        "INSERT INTO SaveRoomState (saveId, roomId, visited) VALUES (?, ?, ?)",
                        (saveId, r[0], 1 if visited else 0)
                    )

            # deletes all items from inventory for a save id and iterates through the current files inventory and adds it back in
            cur.execute("DELETE FROM SaveInventory WHERE saveId = ?", (saveId,))
            for item_name in state.get("inventory", []):
                cur.execute("SELECT itemId FROM Items WHERE itemName = ?", (item_name,))
                i = cur.fetchone()
                if i:
                    cur.execute(
                        "INSERT INTO SaveInventory (saveId, itemId) VALUES (?, ?)",
                        (saveId, i[0])
                    )


        else:
            # If it doesn't exist, create a new one with that name
            cur.execute(
                "INSERT INTO Saves (saveName, currentId, previousId, time) VALUES (?, ?, ?, ?)",
                (saveName, currentId, previousId, float(elapsed_time))
            )
            save_id = cur.lastrowid

            # --- Update SaveRoomState table to reflect visited rooms ---
            for room_name, visited in state.get("visited", {}).items():
                cur.execute("SELECT roomId FROM Rooms WHERE roomName = ?", (room_name,))
                r = cur.fetchone()
                if r:
                    cur.execute(
                        "INSERT INTO SaveRoomState (saveId, roomId, visited) VALUES (?, ?, ?)",
                        (save_id, r[0], 1 if visited else 0)
                    )

            # --- Update SaveInventory table with player's items ---
            for item_name in state.get("inventory", []):
                cur.execute("SELECT itemId FROM Items WHERE itemName = ?", (item_name,))
                i = cur.fetchone()
                if i:
                    cur.execute(
                        "INSERT INTO SaveInventory (saveId, itemId) VALUES (?, ?)",
                        (save_id, i[0])
                    )

        # --- Commit changes to the database ---
        conn.commit()
        print(f"💾 Save '{saveName}' updated successfully!")
        print(f"Total playtime: {elapsed_time:.2f} seconds.")
        conn.close()
        sys.exit()

# --- Commandoloop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command.startswith("look "):
            where = command[5:].strip()
            handle_open(where)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            answer = command[7:].strip()
            result = handle_answer(answer)
            if result:
                return result

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        elif command == "pause":
            handle_pause(state, saveName, time_played, startTime)


        else:
            print("❓ Unknown command. Type '?' to see available commands.")




