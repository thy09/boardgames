#! encoding=utf-8

# Creation Date: 2017-10-26 10:46:14
# Created By: Heyi Tang

import datetime
import random

import werewords
import sushigo

ALL_GAMES = {
        "werewords":werewords.WereWords,
        "sushigoparty": sushigo.SushiGoParty,
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
    def game_info(self, id):
        game = self.game(id)
        if not game:
            return None
        game_class = self.generators[game["type"].lower()]
        if hasattr(game_class, "game_info"):
            return game_class.game_info(game)
        return game

    def create(self, game_type, args):
        if not game_type in self.generators:
            if not game_type in ALL_GAMES:
                game_type = random.choice(ALL_GAMES.keys())
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

    def do_action_sockio(self, game, data):
        game_class = self.generators[game["type"].lower()]
        if hasattr(game_class, "do_action_sockio"):
            return game_class.do_action_sockio(game, data)

    def print_item(self, item, depth = 0):
        if isinstance(item, list) and depth<3:
            print depth*"-", "List Len=", len(item)
            for x in item:
                self.print_item(x, depth+1)
        elif isinstance(item, dict) and depth<3:
            for k,v in item.items():
                print depth*"-", k
                self.print_item(v, depth+1)
        else:
            print depth*"-", item

    def print_game(self, id):
        game = self.game(id)
        if not game:
            print "%s is invalid!" % id
            return
        print "\nStart to Print Game"
        self.print_item(game)

if __name__ == "__main__":
    manager = GameManager()
    for i in range(3):
        id = manager.create("sushigoparty", {})
        manager.print_game(id)
        manager.print_game(i)

