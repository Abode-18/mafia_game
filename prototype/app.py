from flask import Flask , render_template , url_for,request,redirect,session,jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from string import ascii_uppercase
import random
from models import Player,Move
from engine import GameState
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)

players_data = {}
DEBUG = True

rooms = {}
def debug(msg):
    global DEBUG
    if DEBUG:
        print()
        print(f"\033[31m{msg}\033[0m")

def choose_type(Players:dict[str:Player]):
    num_of_players = len(Players)
    types = ["mafia","doctor","citizen"]
    record = {"mafia":0,"doctor":0,"citizen":0}
    for player in Players.values():
        player.type = random.choice(types)
        record[player.type] += 1
        if record["mafia"] >= 2:
            if "mafia" in types:
                types.remove("mafia")
        if record["doctor"] >= 1:
            if "doctor" in types:
                types.remove("doctor")
    return Players

def generate_room(lenth = 4):
    while True:
        room = ""
        for _ in range(lenth):
            room += random.choice(ascii_uppercase)
        if room  in rooms:
            continue
        return room
    


@app.route("/" ,methods = ["GET","POST"])
def index():
    return render_template("home.html")


@app.route("/set_identity", methods=["POST"])
def set_identity():
    data = request.get_json()
    player_id = data.get("player_id")
    session["player_id"] = player_id
    session.permanent = True 
    debug(f"before: {session.get('player_id')}")
    return '', 204

@socketio.on("create-room")
def create_room(data:dict):
    debug(f"data:\n{data}")
    player_id = data.get("player_id")
    name=data.get("name")
    room = generate_room()
    players_data[player_id] = {"name":name,"room":room}
    rooms[room] = {}
    rooms[room]["host"] = player_id
    players: dict[str, Player] = {player_id: Player(player_id=player_id,player_name=name, player_type=None)}
    rooms[room]["players"] = players
    # debug(f"{name} created the room {room}")
    emit("room_joined", {"url": url_for("room", room=room)})

@app.route("/room/<room>",methods=["GET","POST"])
def room(room):
    player_id = session.get("player_id")
    # if request.method == "POST":
    #     player_id = request.get_json().get("player_id")
    #     return jsonify({"status": "success", "message": f"Hello {players_data.get(player_id)}!"})
    debug(f"After: {session.get('player_id')}")
    name = players_data.get(player_id,{}).get("name")
    # debug(name)
    if room not in rooms:return redirect(url_for("index"))
    if not players_data.get(player_id):return redirect(url_for("index",name=name))
    return render_template("room.html",room = room)



@socketio.on("join-room")
def handle_join_room(data):
    player_id = data.get("player_id")
    name = data.get("name")
    room = data.get("room")
    if not room in rooms:
        emit("error",{"message":"the room does not exist"})
        return
    players_data[player_id] = {"name":name,"room":room}
    rooms[room]["players"][player_id] = Player(player_id=player_id,player_name=name,player_type=None)
    emit("room_joined", {"url": url_for("room", room=room)})


@socketio.on("room-page-joined")
def success_messages(data:dict):
    debug(f"players_data:\n\n\n {players_data}")
    session["id"] = data.get("player_id")
    room = players_data.get(data.get("player_id")).get("room")
    join_room(room) 
    emit("success",{"message":f"you have joined the room: {room} successfully."})
    debug(f"players:\n{[rooms[room]["players"][id].name for id in rooms[room]["players"].keys()]}")
    emit("player-joined",{"players":[rooms[room]["players"][id].name for id in rooms[room]["players"].keys()]},to=room)






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