from models import Player, Move
import random
class GameState:
    def __init__(self,players:dict[str,Player]):
        self.players:dict[str,Player] = {p.id:p for p in players.values()}
        self.round = 0
        self.moves = {}
        self.number_of_citizense = len([p.id for p in players.values() if p.type == "citizense"])

    def choose_type(self):
        Players = self.players
        ids = list(Players.keys())
        num_of_players = len(ids)

        if num_of_players >= 6:
            mafia_num = 2
        else:mafia_num=1

        mafia_ids = random.sample(ids,mafia_num)
        remaining = [id for id in ids if id not in mafia_ids]
        
        doctor_id = random.choice(remaining)
        remaining.remove(doctor_id)

        elder_id = random.choice(remaining)
        remaining.remove(elder_id)

        for id in ids:
            if id in mafia_ids:
                Players[id].type = "mafia"
            elif id == doctor_id:
                Players[id].type = "doctor"
            elif id == elder_id:
                Players[id].type = "elder"
            else:
                Players[id].type = "citizen"

        self.players = Players
        return 
    
    def submit_move(self,move:Move):
        if not(move.target in [p for p in self.players.keys()]):
            return {"valid":0,"message":"the player does not exist"}
        if move.player_id in self.moves:
            return {"valid":0,"message":"you have already played"}
        if self.players[move.player_id].type == "elder":
            self.moves[move.player_id] = {
                "target":move.target
            }
            if self.players[move.target].type == "mafia":
                return f"{self.players[move.target].id} is the mafia",0
            else:
                return f"{self.players[move.target].id} is not a mafia",0
        if move.target:
            self.moves[move.player_id] = {
                "target":move.target
            }
        if len(self.moves) == len(self.players) - self.number_of_citizense:
            return self.resolve_round()
        return "hand the phone to the next player",0
    
    def resolve_round(self):
        if self.round <1:
            self.round = 1
            for p in self.players.values():
                p.round = 1
            players = {}
            for id in self.players.keys():
                players[id] = self.avalible_players(id)
            return {"msg":"Round 1 Started","vote":0,"players":players}
        
        
        rescued_player = None
        for player_id,move in self.moves.items():
            actor = self.players[player_id]
            target = self.players[move["target"]].id
            if self.players[player_id].type == "mafia":
                player_killed = self.players[target].id
            elif self.players[player_id].type == "doctor":
                rescued_player = self.players[target].id
            
        if player_killed == rescued_player:
            del self.players[player_killed]
            self.moves = {}
            self.round +=1
            print(f"{player_killed} was killed by the mafia")
            return self.voting()
        print(f"{player_killed} was killed by the mafia.... but the doctor rescued him")
        return self.voting()
    
    def avalible_players(self,player_id:str):
        a_players = {}
        if self.players[player_id].type == "citizen":
            return a_players
        else:
            for player in self.players.values():
                if player.type == self.players[player_id].type:
                    continue
                else:
                    a_players[player.id] = {"name":player.name,"id":player.id}
        
        return dict(sorted(a_players.items()))
    
    def voting(self):
        votes = []
        for player in self.players:
            votes.append(input("enter your vote or write skip to skip the turn: "))
        counts ={}
        for p in votes:
            print(type(p))
            if p in counts:
                counts[p] +=1
            else:
                counts[p] = 1
        vote = None
        max_count = 0

        for player,count in counts.items():
            if count > max_count:
                max_count = count
                vote = player

        
        if vote:
            if self.players[vote].type == "mafia":
                return f"{vote} is the mafia, the citizense win",1
            else:
                del self.players[vote]
                return f"{vote} is out, he is not the mafia",0
        
