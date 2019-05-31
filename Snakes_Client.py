import socket, sys
import curses, pickle
import time, threading
import random

Games=[]
updateFromServerArray = []
kill_count = []
food_count = []
total_players = 0
my_number = 0
total_players = 0
Snakes = []

random.seed(1)
winner = 0

def updateFromServer():
    global winner
    while True:
        data = s.recv(2048)
        if data:
            recievedArray = pickle.loads(data)
            if len(recievedArray) == 1:
                winner = recievedArray[0]
                return
            else:
                updateFromServerArray[:] = recievedArray
        else:
            return

def initGame():
    global Games, total_players
    s = curses.initscr()
    curses.curs_set(0)

    sw, sh = 100, 40
    border = curses.newwin(sh+2, sw+2, 0, 0)
    border.box()

    w = curses.newwin(sh, sw, 1, 1)
    score_window = curses.newwin(total_players+3, sw+2, sh+3, 0)
    score_window.border()

    w.keypad(1)
    w.timeout(1)

    s.refresh()
    w.refresh()
    border.refresh()

    screenInfo = [sh, sw, w, score_window]

    for x in range(total_players):
        player_no = x+1
        game_thread = threading.Thread(target = Game, args = (player_no, screenInfo,))
        Games.append(game_thread)

    for game in Games:
        game.start()

def Game(player_no, screenInfo):
    global total_players, food, kill_count, food_count, winner

    sh, sw, w, sc_w = screenInfo
    sc_w.addstr(1, 2, "Player " + str(my_number) + "'s LIVE SCOREBOARD:")
    sc_w.addstr(player_no + 1, 2, "Player " + str(player_no) + "'s food count: 0\t\t" + " kill count: 0 ")
    sc_w.refresh()
    
    sc_w.refresh()

    t = threading.Thread(target = updateFromServer, args = ())
    t.start()

    snk_x = sw/4
    # snk_y = (sh/2)/player_no
    snk_y = sh/(total_players+1)*player_no

    snake = [
        [snk_y, snk_x],
        [snk_y, snk_x-1],
        [snk_y, snk_x-2],
        [snk_y, snk_x-3]
    ]
    
    food = [sh/2, sw/2]
    w.addch(food[0], food[1], curses.ACS_PI)

    key = curses.KEY_RIGHT
    updateToServerThread("key", key)

    playerLost, shutup = False, False
    while True:
        if winner != 0 and player_no == my_number:
            curses.endwin()
            if winner == -1:
                print("Nobody won!!")
            else:
                print("Player " + str(winner) + " won")
            quit()
            break
            
        if playerLost:
            Snakes[player_no - 1] = None
            if player_no == my_number  and not shutup:
                print ("Oops you lost!")
                updateToServerThread("playerLost", player_no)
                shutup = True
                while snake:
                    try:
                        p = snake.pop()
                        w.addch(p[0], p[1], " ")
                    except:
                        continue
                continue
            continue

        if snake[0][0] in [0, sh] or snake[0][1]  in [0, sw] or snake[0] in snake[1:]:
            playerLost = True
            continue

        myUpdate = updateFromServerArray[player_no-1]
        kill_by_player = updateFromServerArray[-3]
        food_change = updateFromServerArray[-2]
        dead_player = updateFromServerArray[-1]

        if kill_by_player:
            kill_count[kill_by_player-1] += 1
            updateScoreBoard(sc_w, food_count, kill_count)
            updateFromServerArray[-3] = None

        if dead_player == player_no:
            playerLost = True
            continue

        keys = [curses.KEY_DOWN, curses.KEY_UP, curses.KEY_LEFT, curses.KEY_RIGHT]
        keys2 = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT, curses.KEY_LEFT]

        if myUpdate:
            for k1, k2 in zip(keys, keys2):
                if key == k1 and myUpdate == k2:
                    myUpdate = key
            key = myUpdate

            updateFromServerArray[player_no-1] = None
            
            #if len(snake)>0:
            new_head = [snake[0][0], snake[0][1]]

            if key == curses.KEY_DOWN:
                new_head[0] += 1
            if key == curses.KEY_UP:
                new_head[0] -= 1
            if key == curses.KEY_LEFT:
                new_head[1] -= 1
            if key == curses.KEY_RIGHT:
                new_head[1] += 1

            snake.insert(0, new_head)
           # if len(snake)>0:
            if snake[0] == food and my_number == player_no:
                updateToServerThread("food", player_no)

            if food_change and player_no == food_change:
                food_count[player_no-1] += 1
                updateScoreBoard(sc_w, food_count, kill_count)
                updateFromServerArray[-2] = None
                food = None
                while food is None:
                    nf = [
                        random.randint(1, sh-1),
                        random.randint(1, sw-1)
                    ]
                    food = nf if nf not in snake else None
                w.addch(food[0], food[1], curses.ACS_PI)
            else:
                tail = snake.pop()
                Snakes[player_no-1]=snake
                w.addch(tail[0], tail[1], ' ')
            try:
                w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
            except:
                # playerLost = True
                continue

            Snakes[player_no-1]=snake

            for i, s in enumerate(Snakes):
                if s and s!=snake:
                    try:
                        if snake[0] in s[:]: #snake ka head kaheen bhi laga
                            playerLost = True
                            updateToServerThread("kill", i+1)
                            break
                            #yahan kill count daalna
                    except:
                        continue

            if playerLost:
                continue
                
        if player_no == my_number:
            next_key = w.getch()
            if next_key != -1:
                updateToServerThread("key", next_key)

def updateScoreBoard(sc_w, food_count, kill_count):
    global total_players
    sc_w.erase()
    sc_w.addstr(1, 2, "Player " + str(my_number) + "'s LIVE SCOREBOARD:")
    for index in range(total_players):
        sc_w.addstr(index + 2, 2, "Player " + str(index+1) + "'s food count: " + str(food_count[index]) + "\t\tkill count: " + str(kill_count[index]))
        # sc_w.refresh()
    sc_w.border()
    sc_w.refresh()

def updateToServer(updateType, update):
    dataDict = {updateType:update}
    s.sendall(pickle.dumps(dataDict))

def updateToServerThread(updateType, update):
    t = threading.Thread(target = updateToServer, args = (updateType, update,))
    t.start()

HOST = ""
PORT = 0
s = None

def main(argv):
    global HOST, PORT, s, my_number, total_players, kill_count, food_count, Snakes
    HOST = sys.argv[1] #ip
    PORT = int(sys.argv[2])
    print(HOST, PORT)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("Hello User, Game starting soon")

    info = pickle.loads(s.recv(1024))
    print(info)
    my_number, total_players = info["player"], info["total_players"]
    updateFromServerArray = [None] * (total_players+3)
    Snakes=[None]*total_players
    kill_count = [0]*total_players
    food_count = [0]*total_players
    print("Hello Player " + str(my_number) + " Game starting!!")
    time.sleep(1)

    initGame()

if __name__ == "__main__":
    main(sys.argv)