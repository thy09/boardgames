#! encoding=utf-8

# Creation Date: 2017-10-26 10:46:14
# Created By: Heyi Tang

import datetime
import random
import redis
import json

import werewords

ALL_GAMES = {
        "werewords":werewords.WereWords
        }


class GameManager:
    def __init__(self):
        self.r = redis.StrictRedis()
        try:
            self.r.ping()
        except:
            self.r = redis.StrictRedis(host="redis")
        self.generators = {}

    def new_user(self):
        upper = 99999999
        lower = 10000000
        uid = str(random.randint(lower, upper))
        while self.r.exists("user"+uid):
            uid = str(random.randint(lower, upper))
        self.r.setex("user"+uid, 3600*24, "{}")
        return uid

    def exist_user(self,uid):
        if uid is None:
            return None
        return self.r.exists("user" + uid)

    def update_user(self, uid):
        self.r.expire("user"+uid, 3600*24)

    def user_sit(self, id, idx, userid):
        game = self.game(id)
        if not game or not game.get("occupied"):
            return False
        idx = int(idx)
        cur = game["occupied"][idx]
        if cur is not None:
            return False
        game["occupied"][idx] = userid
        self.save_game(id, game)
        return True

    def new_game_id(self):
        upper = 1000000
        lower = 1000
        gid = str(random.randint(lower, upper))
        while self.r.exists("game"+gid):
            gid = str(random.randint(lower, upper))
        return gid

    def save_game(self, gid, game):
        data = json.dumps(game)
        self.r.set("game" + gid, data)

    def game(self, gid):
        data = self.r.get("game%s" % (gid))
        try:
            return json.loads(data.decode())
        except Exception as e:
            print(e)
            return None

    def create(self, game_type, args):
        if not game_type in self.generators:
            if not game_type in ALL_GAMES:
                return None
            self.generators[game_type] = (ALL_GAMES[game_type])()
        game = self.generators[game_type].create(args)
        if "count" in game:
            game["occupied"] = [None] * game["count"]
        game["id"] = self.new_game_id()
        self.save_game(game["id"], game)
        return game["id"]

    def do_action(self, game, data):
        game_class = self.generators[game["type"].lower()]
        resp = game_class.do_action(game, data)
        self.save_game(game["id"], game)
        return resp

    def print_game(self, id):
        game = self.game(id)
        if not game:
            print("%s is invalid!" % id)
            return
        for k,v in game.items():
            if isinstance(v,list):
                v = ",".join(map(unicode,v))
            print(k,v)
        print("")

if __name__ == "__main__":
    manager = GameManager()
    for i in range(3):
        id = manager.create("werewords", {})
        manager.print_game(id)
        manager.print_game(i)

