import sys
import curses
import socket, threading
import pickle
import time

clientsThreads = []
connections = []
movesInTimeframe = []
inGame = []
No_of_Players = 0
gamesLostCountdown = 0
movesInTimeframe = []
kill_count = []
food_count = []
inGame = []

def parseClientData(data, player_no):
    global snakes, No_of_Players, inGame
    global screen_width, screen_height

    recvDataDict = pickle.loads(data)
    dataType = list(recvDataDict.keys())[0]
    data = list(recvDataDict.values())[0]
    
    player_index = int(player_no)-1

    sendDataDict = data

    if dataType == "key":
        # print("key press")
        movesInTimeframe[player_index] = sendDataDict
    elif dataType == "food":
        # print("food")
        movesInTimeframe[-2] = data
    elif dataType == "playerLost":
        # print("Player ", data, " lost")
        no_alive_players = len(list(filter(lambda x: x==True, inGame)))
        if no_alive_players > 1:
            inGame[player_index] = False
        return data
    elif dataType == "kill":
        # print("Player ", data, " has murdered!!!!")
        movesInTimeframe[-3] = data
    else:
        return False
    return False

def updateFromClient(conn, player_no):
    global gamesLostCountdown
    playerLost = False
    while True:
        try:
            data=conn.recv(1024)
            if data:
                # print("parsing data..")
                playerLost = parseClientData(data, player_no)
            else:
                print ("Player " + player_no + " connection lost, empty data received")
                playerLost = True
        except:
            playerLost = True

        if playerLost:
            movesInTimeframe[-1] = playerLost if playerLost else player_no
            gamesLostCountdown -= 1
            print("Closing connection...")
            return

def newClientThread(conn):
    global gamesLostCountdown, No_of_Players
    print(threading.currentThread().getName() + " starting")
    player_no = threading.currentThread().getName()[-1]

    infoDict = {"player": int(player_no), "total_players": No_of_Players}
    conn.sendall(pickle.dumps(infoDict))

    time_start = time.clock()
    
    t = threading.Thread(target = updateFromClient, args = (conn, player_no, ))
    t.start()

    while True:
        time_elapsed = time.clock() - time_start
        tempMoves = [elem for elem in movesInTimeframe]
        if time_elapsed >= 0.05:
            for c in connections:
                c.sendall(pickle.dumps(tempMoves))
            movesInTimeframe[-3] = None # KILL
            movesInTimeframe[-2] = None #food
            movesInTimeframe[-1] = None #playerLost
            time_start = time.clock()
        if gamesLostCountdown <= 1:
            time.sleep(0.2)
            winner = [-1]
            if gamesLostCountdown == 1:
                winner[:] = [inGame.index(True)+1]
            for c in connections:
                c.sendall(pickle.dumps(winner))
            break

HOST = ""
PORT = 0
s = None

def main(argv):
    global No_of_Players, HOST, PORT, s, gamesLostCountdown, movesInTimeframe, kill_count, food_count, inGame
    HOST = sys.argv[1] #ip
    PORT = int(sys.argv[2])
    print(HOST, PORT)
    No_of_Players = int(sys.argv[3])

    gamesLostCountdown = No_of_Players
    movesInTimeframe = [None] * (No_of_Players+3)
    kill_count = [0] * (No_of_Players)
    food_count = [0] * (No_of_Players)
    inGame = [True] * No_of_Players

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(3)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target = newClientThread, args = (conn, ))
        clientsThreads.append(t)
        connections.append(conn)
        #start when a certain no of players have joined
        if len(clientsThreads) == No_of_Players:
            for t in clientsThreads:
                t.start()

if __name__ == "__main__":
    main(sys.argv)