# -----------------------------------------------------------------------------
# File: corridor.py
# ACS School Project - Simple Maze Example
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: July 2025
# -----------------------------------------------------------------------------
import sqlite3
import sys
import time as t
from .utils import chooseNextRoom

def enterCorridor(state, saveName, time_played, startTime):
    print("\n🚶 You are standing in the school's main corridor.")
    print("You see a long corridor with many doors and glass walls on both side. Behind these door are rooms, waiting to be explored.")

    # --- List of accessible rooms from here ---
    available_rooms = ["classroom2015", "projectroom3", "studylandscape","equinoxroom","classroom2031","teacherroom","storageroom"]

    # --- Command handlers ---

    def handle_look():
        """Describe the corridor and show where the player can go."""
        print("\nYou take a look around.")
        print("Students and teachers are walking in both directions along the corridor. You see several labeled doors.")
        print(f"- Possible doors: {', '.join(available_rooms)}")
        print("- You current inventory:", state["inventory"])

    def handle_help():
        """List available commands and explain navigation."""
        print("\nAvailable commands:")
        print("- look around         : See what's in the corridor and where you can go.")
        print("- go <room name>      : Move to another room. Example: go classroom2015")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")
        print("- pause                : Pause the game.")
        print("- status              : shows status of game")
        print("- scoreboard            : Shows top 5 scores")
        print(f"- current inventory    : {state['inventory']} ")

    def handle_go(room_name):
        """Move to a listed room."""
        room = room_name.lower()
        if room in available_rooms:
            print(f"You walk toward the door to {room}.")
            state["previous_room"] = "corridor"
            return room
        else:
            print(f"❌ '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    def handle_pause():

        percentComplete, elapsed_time = handle_status()

        conn = sqlite3.connect("GameSave.db")
        cur = conn.cursor()

        cur.execute("""SELECT roomId FROM Rooms WHERE roomName = ?""", (state["current_room"],))
        currentId = cur.fetchone()[0]

        cur.execute("""SELECT roomId FROM Rooms WHERE roomName = ?""", (state["previous_room"],))
        previousId = cur.fetchone()[0]

        cur.execute("""SELECT saveId FROM Saves WHERE saveName = ?""", (saveName,))
        saveId = cur.fetchone()

        if saveId:
            saveId = saveId[0]

            # --- Update the Saves table ---
            cur.execute(
                "UPDATE Saves SET currentId = ?, previousId = ?, time = ?, completion = ? WHERE saveId = ?",
                (currentId, previousId, float(elapsed_time), float(percentComplete), saveId)
            )

            # --- Refresh SaveRoomState for this save ---
            cur.execute("DELETE FROM SaveRoomState WHERE saveId = ?", (saveId,))
            for room_name, visited in state.get("visited", {}).items():
                cur.execute("SELECT roomId FROM Rooms WHERE roomName = ?", (room_name,))
                r = cur.fetchone()
                if r:
                    cur.execute(
                        "INSERT INTO SaveRoomState (saveId, roomId, visited) VALUES (?, ?, ?)",
                        (saveId, r[0], 1 if visited else 0)
                    )

            # --- Refresh SaveInventory for this save ---
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
                "INSERT INTO Saves (saveName, currentId, previousId, time, completion) VALUES (?, ?, ?, ?, ?)",
                (saveName, currentId, previousId, float(elapsed_time), float(percentComplete))
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

    def handle_status():

        elapsed_time = (t.time() - startTime) + time_played
        completed = 0
        totalgame = 0
        for i in state["visited"]:
            totalgame += 1
            if state["visited"][i] == True:
                completed += 1
        percentplayed = completed / totalgame * 100
        print(saveName, ":")
        print("you have completed " + str(percentplayed) + "% of the gate")
        print("time played:", elapsed_time)
        return percentplayed, elapsed_time

    def handle_scoreboard():


        conn = sqlite3.connect("GameSave.db")
        cur = conn.cursor()

        cur.execute("SELECT saveName, time, completion FROM saves")
        completionList = cur.fetchall()

        sorted_records = sorted(completionList, key=lambda x: (-x[2], x[1]))

        # Get top N records
        top_scores = sorted_records[:5]

        # Print results
        print("Top Scores:")
        for name, time, percent in top_scores:
            print(f"Name: {name}, Time: {time}, Percent: {percent}%")


    # --- Main corridor command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command == "pause":
            handle_pause()

        elif command == "status":
            handle_status()

        elif command == "scoreboard":
            handle_scoreboard()

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            if result:
                return result

        elif command == "quit":
            print("👋 You leave the school and the adventure comes to an end. Game over.")
            sys.exit()


        else:
            print("❓ Unknown command. Type '?' to see available commands.")
