class Player:
    def __init__(self,player_id,player_name,player_type,round):
        self.id = player_id
        self.name = player_name
        self.type = player_type
        self.round = round

class Move:
    def __init__(self,player_id,target=None):
        self.player_id = player_id
        self.target= target
