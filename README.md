# Snakes
Online multiplayer Snakes game

This contains code for both the server and the client. The game will have a single server and multiple clients/players.<br/><br/>
#### The command for starting the server should be as follows:
+ python server.py **IP-address** **port** **number-of-players** </br>
    - e.g python Snakes_Server.py 192.168.5.5 2000 5 <br/>
    - e.g python Snakes_Server.py 127.0.0.1 2000 3<br/><br/>
#### The command for starting the client should be as follows:
+ python Snakes_Client.py **IP-address-of-server** **port-of-server**<br/>
    - e.g python Snakes_Client.py 192.168.5.5 2000<br/>
    - e.g python Snakes_Client.py 127.0.0.1 2000<br/>

The game ends when there is only one player left, in which case the last player left is the winner. Collision with the sides or with other snakes kills the snake; if there is a head-on collisions between two snakes, then both snakes die. Eating food makes the snake longer and gives the player points. <br/>
Each client/player has a scoreboard with his/her kill-count i.e (number of snakes that collided with said player's snake) and food-count.
