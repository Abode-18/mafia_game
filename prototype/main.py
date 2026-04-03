from models import Player,Move
from engine import GameState

players = {
    "p1":Player("p1","mafia"),
    "p2":Player("p2","elder"),
    "p3":Player("p3","doctor"),
    "p4":Player("p4","citizense"),
    "p5":Player("p5","citizense"),
}
game = GameState(players)
citizense = []
for p in players.values():
    a = input(f"{p.id} you are {p.type} press enter and hand the phone to the next player")
    if p.type == "citizense":
        target = None
        citizense.append(p)
        del players[p]

state = 0
print(citizense)
while not state:
    for player in citizense:
        target = input(f"{player.id} enter the target player: (if you are a citizense type anything)")
        massage,state = game.submit_move(Move(player.id,None))
    for player in players.values():
        target = input(f"{player.id} enter the target player: (if you are a citizense type anything)")
        massage,state = game.submit_move(Move(player.id,target))
        if massage:
            print(massage)
