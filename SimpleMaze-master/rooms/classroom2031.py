import sys
import time as t
import sqlite3

def enterClassroom2031(state, saveName, time_played, startTime):
    import time
    # --- Check if the player has the key to enter ---
    if not state["visited"]["classroom2031"]:
        if "class key" not in state["inventory"]:
            print("\n🚪 The door to class room 2031 is locked.")
            print("You jiggle the handle. It's no use.")
            print("🔐 You need a key. Perhaps it's hidden elsewhere in the school?")
            return "corridor"
        else:
            print("\n🗝️ You insert the brass key into the lock and turn it with a satisfying click.")

    # narration when the user enters the room
    print("\n You step into classroom 2.031.")
    print("As you step in the door closes shut and the door has a small keypad above the handle.")
    print("to open the door a 3 digit code is meant to be typed in to unlock the room\n")

    # container for logic questions
    logicPuzzle = []

    # gives access to the txt files with the logic question
    puzzleFile = open("rooms/logicpuzzles.txt", "r", encoding="utf-8")

    # iterates through each line in the text file to add each logic puzzle to logicPuzzle list
    for line in puzzleFile:
        line = line.strip()
        logicPuzzle.append(line)

    logicAnswer = ["three", "friday", "thursday"]
    answerNum = 0

    def handle_look(questionList):

        print("\nlooking around the classroom.")
        if not state["visited"]["classroom2031"]:
            print("you see a single chair with a rotating desk with three puzzles on it.")
            print("\nyou read the puzzle in front of you.")
            print("it says:", questionList[0])
        else:
            print("you see an empty room with a rotating table")
            # checks if the key hasn't been picked up yet
            if "equinox key" not in state["inventory"]:
                print("In the middle of the table a key has appeared. This could possibly be used for later use.")
            else:
                print("there is nothing more to see in this room")
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        print("\nAvailable commands:")
        print("- look around         : Examine the room and its contents.")
        if not state["visited"]["classroom2031"]:
            print("- answer <answer>     : Attempt to solve the logic puzzle")
        if state["visited"]["classroom2031"] and "equinox key" not in state["inventory"]:
            print("- take equinox key            : Pick up the equinox key once it's revealed.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")
        print("- pause                : Pause the game.")
        print("- status               : Show the status of the game.")

    def handle_take(item):
        if item == "equinox key":
            if not state["visited"]["classroom2031"]:
                print("❌ There's no key visible yet. Maybe solving the puzzle will reveal more.")
            elif "equinox key" in state["inventory"]:
                print("You already have the equinox key in your backpack.")
            else:
                print("🔑 you reach over the table and grab the equinox key")
                print("and tuck it safely into your backpack.")
                state["inventory"].append("equinox key")
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["corridor", "back"] and input("enter the pin into the door: ") == "354": #asks for the pin code to the door
            print("🚪 You open the door and step back into the corridor.")
            return "corridor" # lets you out of the room if the door code is correct
        elif destination in ["corridor", "back"] :
            print(f"❌ the code was wrong.")
            return None
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_answer(answer, questionAnswer, ansNum, questionList):
        if state["visited"]["classroom2031"]:
            print("✅ You've already solved this challenge.")
            return ansNum
        elif answer == questionAnswer[0]:
            print("✅ Correct! the table rotates to the next logic puzzle")
            ansNum += 1
            questionAnswer.pop(0)
            questionList.pop(0)
            if ansNum >= 3:
                state["visited"]["classroom2031"] = True
                print("Suddenly you see something on the desk.")
            return ansNum
        else:
            print("❌ Incorrect. you wrote the answer but nothing happened perhaps the answer provided was wrong")
            return  ansNum

    def handle_pause(state, saveName, time_played, startTime):

        # --- Calculate how long the player has been playing for ---
        # Combine saved play time with current session duration
        elapsed_time = (time.time() - startTime) + time_played

        conn = sqlite3.connect("newsave.db")
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
                "UPDATE Saves SET currentId = ?, previousId = ?, time = ? WHERE saveId = ?",
                (currentId, previousId, float(elapsed_time), saveId)
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



    def handle_status(state, saveName, time_played, startTime):

        elapsed_time = (t.time() - startTime) + time_played
        completed = 0
        totalgame = 0
        for i in state["visited"]:
            totalgame += 1
            if state["visited"][i] == True:
                completed += 1
        print(saveName, ":")
        print("you have completed " + str((completed/totalgame)*100) + "% of the gate")
        print("time played:", elapsed_time)







    # --- Commandoloop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look(logicPuzzle)

        elif command == "?":
            handle_help()

        elif command.startswith("take "):
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            answer = command[7:].strip()
            answerNum = handle_answer(answer, logicAnswer, answerNum, logicPuzzle)

        elif command == "pause":
            handle_pause(state, saveName, time_played, startTime)

        elif command == "status":
            handle_status(state)

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")


