from flask import Flask , render_template , url_for,request,redirect,session,jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from string import ascii_uppercase
import random
from models import Player,Move
from engine import GameState
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)

players_data:dict[str,dict[str:Player]] = {}
DEBUG = True

rooms = {}
def debug(msg):
    global DEBUG
    if DEBUG:
        print()
        print(f"\033[31m{msg}\033[0m")

def generate_room(lenth = 4):
    while True:
        room = ""
        for _ in range(lenth):
            room += random.choice(ascii_uppercase)
        if room  in rooms:
            continue
        return room
    


@app.route("/", methods=["GET", "POST"])
def index():
    p_id = session.get("player_id")



    room = request.args.get("room")
    #here
    if not p_id:
        if room:
            return render_template("loading.html",room=room)
        else:
            return render_template("loading.html")


    if p_id not in players_data:
        players_data[p_id] = {
            "player": Player(p_id, None, None),
            "room": None
        }

    player_data = players_data[p_id]
    player = player_data["player"]

    # update name if provided


    current_room = player_data.get("room")

    # redirect if already in room and has name
    if current_room and player.name:
        return redirect(url_for("room", room=current_room))

    # render with room if joining one
    if current_room and not player.name:
        return render_template("home.html", room=current_room)

    if room and not player.name:
        return render_template("home.html", room=room)

    if player.name:
        return render_template("home.html", name=player.name)

    debug("home page:")
    debug(f"player_data:\n{players_data}")
    debug(f"rooms:\n{rooms}")

    return render_template("home.html")



@app.route("/set_identity", methods=["POST"])
def set_identity():
    data = request.get_json()
    player_id = data.get("player_id")
    if player_id in players_data:
        pass
    session["player_id"] = player_id
    session.permanent = True 
    return '', 204

@socketio.on("create-room")
def create_room(data:dict):
    player_id = data.get("player_id")
    name=data.get("name")
    room = generate_room()
    players_data[player_id]["player"].name = name
    players_data[player_id]["room"] = room
    rooms[room] = {}
    rooms[room]["host"] = player_id
    player:Player = players_data[player_id]["player"] 
    players: dict[str, Player] = {player_id: player}
    rooms[room]["players"] = players
    debug("create-room:")
    debug(f"player_data:\n{players_data}")
    debug(f"rooms:\n{rooms}")
    debug(rooms[room]["players"][player_id] is players_data[player_id]["player"])
    emit("room_joined", {"url": url_for("room", room=room)})

@socketio.on("join-room")
def handle_join_room(data):
    player_id = data.get("player_id")
    name = data.get("name")
    room = data.get("room")
    if not room in rooms:
        emit("error",{"message":"the room does not exist"})
        return
    if rooms[room].get("status") == "started" and player_id not in rooms[room]["players"].keys():
        emit("error",{"message":"the room has already started"})
        return
    players_data[player_id]["room"] = room
    players_data[player_id]["player"].name = name
    player = players_data[player_id]["player"]
    rooms[room]["players"][player_id] = player
    emit("room_joined", {"url": url_for("room", room=room)})


@app.route("/room/<room>",methods=["GET","POST"])
def room(room):
    player_id = session.get("player_id")
    #cheacking that the player exist in player_data
    if not players_data.get(player_id):
        return redirect(url_for("index",room=room))

    if room not in rooms:
        return redirect(url_for("index"))
    if players_data[player_id]["room"] != room:
        #edit in the future
        if players_data[player_id]["room"]:return redirect(url_for("room",room = players_data[player_id]["room"]))
        else:
            if not players_data[player_id]["player"].name:
                return redirect(url_for("index",room=room))
            players_data[player_id]["room"] = room
            rooms[room]["players"][player_id] = players_data[player_id]["palyer"]
    is_host = rooms[room].get("host") == player_id
    debug("room page:")
    debug(f"player_data:\n{players_data}")
    debug(f"rooms:\n{rooms}")

    return render_template("room.html",room = room,is_host = is_host)






@socketio.on("room-page-joined")
def success_messages(data:dict):
    session["id"] = data.get("player_id")
    room = players_data.get(data.get("player_id")).get("room")
    is_host = rooms[room].get("host") == session.get("id")
    if rooms[room].get("status") == "started":
        socketio.emit("started",{"type":players_data[session.get("id")]["player"].type})
        return
    join_room(room) 
    emit("success",{"message":f"you have joined the room: {room} successfully."})
    # debug(rooms)
    # debug(f"players:\n{[rooms[room]["players"][id].name for id in rooms[room]["players"].keys()]}")
    emit("player-joined",{"players":[rooms[room]["players"][id].name for id in rooms[room]["players"].keys()]},to=room)


@socketio.on("Start_game")
def Start_game():
    room = players_data.get(session.get("id")).get("room")

    if len(rooms[room]["players"]) <1:
        socketio.emit("error",{"message":"the number of players must be more then 4 players"})
        return

    rooms[room]["game"] = GameState(rooms[room]["players"])
    rooms[room]["game"].choose_type()
    debug(players_data[session.get("id")]["player"].type)
    rooms[room]["status"] = "started"
    debug("Start Game")
    debug(f"player_data:\n{players_data}")
    debug(f"rooms:\n{rooms}")
    debug(f"{rooms[room]["players"] == rooms[room]["game"].players}")
    socketio.emit("Game-on",{p.id:p.type for p in rooms[room]["game"].players.values()},to=room)



# @socketio.on("join")
# def join():
#     room = session.get("room")
#     join_room(room)
#     debug(f"{session.get('name')} joined the room: {session.get('room')}")

# @socketio.on("connect")
# def connect(auth):
#     room = session.get("room")
#     name = session.get("name")
#     if not room or not name:
#         return
#     if room not in rooms:
#         leave_room(room)
#         return
#     join_room(room)
#     emit("message",{"name":name,"message":"has entered the room"},to=room)
    
#     debug(f"{name} joined {room}")


# @socketio.on("disconnect")
# def disconnect():
#     room = session.get("room")
#     name = session.get("name")

#     if not room or not name:
#         return

#     leave_room(room)
#     if rooms[room]["host"] == name:
#         del rooms[room]
#         return
#     if room in rooms and name in rooms[room]["players"]:
#         del rooms[room]["players"][name]

#     if len(rooms[room]["players"]) == 0:
#         del rooms[room]
#         return
        
#     emit("disconnect",{"message":f"{name} disconnected"},to=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)