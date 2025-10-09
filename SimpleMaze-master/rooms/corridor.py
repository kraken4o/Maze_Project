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

    def handle_pause(state, saveName, time_played, startTime):

        flag = True
        conn = sqlite3.connect("GameSave.db")
        cursor = conn.cursor()

        #elapsed time is the total time accross all sessions
        elapsed_time = (t.time() - startTime) + time_played
        #t.time() here is the seconds since the epoch(Jan 1, 1970) when you hit pause
        #Starttime is in the main function and is also the seconds since the epoch but was taken earlier, when you enter your file to run the game.
        #time played adds the previous to the current seconds played ofn the same file
        if saveName == "no save":
            userName = input("enter name of save file: ")
            while flag:
                cursor.execute("""SELECT saveName FROM saves WHERE saveName = ?""", (userName,))
                saveList = cursor.fetchall()
                if saveList:
                    userName = input("save file already exists enter name of save file: ")
                else:
                    cursor.execute("""INSERT INTO saves (saveName, state, saveTime) VALUES (?, ?, ?)""", (userName, str(state), elapsed_time))
                    #new file adds states and elapsedtime
                    conn.commit()
                    print(f"💾 Game saved successfully! Total playtime: {elapsed_time:.2f} seconds.")
                    sys.exit()
        else:
            cursor.execute("""UPDATE Saves SET state = ?, saveTime = ? WHERE saveName = ?""", (str(state), elapsed_time, saveName))
            #updated the old databsee file with new state and elapsed time
            conn.commit()
            print(f"💾 Game updated successfully! Total playtime: {elapsed_time:.2f} seconds.")
            sys.exit()

    # --- Main corridor command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
            handle_help()

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            if result:
                return result

        elif command == "quit":
            print("👋 You leave the school and the adventure comes to an end. Game over.")
            sys.exit()

        elif command == "pause":
            handle_pause(state, saveName, time_played, startTime)

        else:
            print("❓ Unknown command. Type '?' to see available commands.")
