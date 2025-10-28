# -----------------------------------------------------------------------------
# File: studylandscape.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------

import sys
import time as t
import sqlite3
from .utils import chooseNextRoom

def enterStudyLandscape(state, saveName, time_played, startTime):
    state["visited"]["studylandscape"] = True
    print("\n🛋️ You step into the study landscape.")
    print("Soft chairs and tables to work and chat with fellow students and a quiet hum of a coffee machine.")
    print("It feels like a place to work but also to pause and catch your breath.")

    # --- Command handlers ---

    def handle_look():
        """Describe the lobby and show exits."""
        print("\nYou take a slow look around.")
        print("There are a few posters on the wall about upcoming student events.")
        print("A group of students is sitting in the corner gazing at a laptop")
        print("- Possible exit: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        """Show help message with available commands."""
        print("\nAvailable commands:")
        print("- look around         : See what’s in the lobby.")
        print("- go corridor / back  : Return to the main corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")
        print("- pause                : Pause the game.")

    def handle_go(destination):
        """Handle movement to another room."""
        if destination in ["corridor", "back"]:
            print("You leave the study landscape and head back into the corridor.")
            state["previous_room"] = "studylandscape"
            return "corridor"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

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

    # --- Main command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command == "pause":
            handle_pause(state, saveName, time_played, startTime)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "quit":
            print("👋 You sit back in the softest chair, close your eyes, and exit the adventure. Game over.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
