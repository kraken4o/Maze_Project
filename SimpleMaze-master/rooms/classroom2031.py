import sys

def enterClassroom2031(state):

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
            if "otherkey" not in state["inventory"]:
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
        if state["visited"]["classroom2031"] and "otherkey" not in state["inventory"]:
            print("- take otherkey            : Pick up the otherkey once it's revealed.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "otherkey":
            if not state["visited"]["classroom2031"]:
                print("❌ There's no key visible yet. Maybe solving the puzzle will reveal more.")
            elif "otherkey" in state["inventory"]:
                print("You already have the otherkey in your backpack.")
            else:
                print("🔑 you reach over the table and grab the otherkey")
                print("and tuck it safely into your backpack.")
                state["inventory"].append("otherkey")
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


    def handle_pause(state):
        print()



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

        elif command == "quit":
            print("👋 You drop your backpack, leave the maze behind, and step back into the real world.")
            sys.exit()

        else:
            print("❓ Unknown command. Type '?' to see available commands.")


