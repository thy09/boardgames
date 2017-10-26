#! encoding=utf-8

# Creation Date: 2017-10-26 10:46:14
# Created By: Heyi Tang

import datetime
import random

import werewords

ALL_GAMES = {
        "werewords":werewords.WereWords
        }


class GameManager:
    def __init__(self):
        self.games = {}
        self.generators = {}
        self.users = {}

    def new_user(self):
        upper = 99999999
        lower = 10000000
        uid = str(random.randint(lower, upper))
        while uid in self.users:
            uid = str(random.randint(lower, upper))
        return uid

    def update_user(self, uid):
        expire_time = 1200
        self.users[uid] = datetime.datetime.now() + datetime.timedelta(seconds = expire_time)

    def exist_user(self, uid):
        if not uid in self.users:
            return False
        expire = self.users.get(uid)
        if expire <= datetime.datetime.now():
            self.users.pop(uid)
            return False
        return True

    def user_sit(self, id, idx, userid):
        game = self.game(id)
        if not game or not game.get("occupied"):
            return False
        idx = int(idx)
        cur = game["occupied"][idx]
        if cur is not None and self.exist_user(cur):
            return False
        game["occupied"][idx] = userid
        return True

    def new_game_id(self):
        upper = 1000000
        lower = 1000
        id = random.randint(lower, upper)
        while str(id) in self.games:
            id = random.randint(lower, upper)
        return id

    def game(self, id):
        return self.games.get(str(id))

    def create(self, game_type, args):
        if not game_type in self.generators:
            if not game_type in ALL_GAMES:
                return None
            self.generators[game_type] = (ALL_GAMES[game_type])()
        game = self.generators[game_type].create(args)
        if "count" in game:
            game["occupied"] = [None] * game["count"]
        game["id"] = self.new_game_id()
        self.games[str(game["id"])] = game
        return game["id"]

    def do_action(self, game, data):
        game_class = self.generators[game["type"].lower()]
        return game_class.do_action(game, data)

    def print_game(self, id):
        game = self.game(id)
        if not game:
            print "%s is invalid!" % id
            return
        for k,v in game.items():
            if isinstance(v,list):
                v = ",".join(map(unicode,v))
            print k, v
        print ""

if __name__ == "__main__":
    manager = GameManager()
    for i in range(3):
        id = manager.create("werewords", {})
        manager.print_game(id)
        manager.print_game(i)

