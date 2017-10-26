#! encoding=utf-8

# Creation Date: 2017-10-20 09:42:05
# Created By: Heyi Tang

import json
import random
import os
import datetime

class SpyFalls:
    def __init__(self):
        self.spyfalls = {}
        self.games = {}
        self.users = {}

    def gen_id(self):
        upper = 1000000
        lower = 1000
        id = random.randint(lower, upper)
        while str(id) in self.games:
            id = random.randint(lower, upper)
        return id

    def game(self, id):
        return self.games.get(str(id))

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
        if not game:
            return False
        idx = int(idx)
        cur = game["occupied"][idx]
        if cur is not None and self.exist_user(cur):
            return False
        game["occupied"][idx] = userid
        return True

    def create(self, player_count, upper, lower, scene_count = 10, key = "zh-cn-26", spyschool = 0):
        fname = "%s.json" % (key)
        if not os.path.exists(fname):
            key = "zh-cn-26"
            fname = "%s.json" % key
        if not key in self.spyfalls:
            self.spyfalls[key] = SpyFall(fname)
        id = self.gen_id()
        game = self.spyfalls[key].create(player_count, upper, lower, scene_count, spyschool)
        self.games[str(id)] = game
        game["id"] = id
        game["locid"] = key
        game["occupied"] = [False] * player_count
        return id

    def get_roles(self, locid, scene):
        if not locid in self.spyfalls:
            return {}
        return self.spyfalls[locid].roles.get(scene,{})

    def print_game(self, id):
        game = self.games.get(str(id))
        for k,v in game.items():
            print k
            if k == "roles":
                for role in v:
                    print role
            elif k == "players":
                for i, player in enumerate(v):
                    print i, player
            else:
                print v

class SpyFall:
    def __init__(self, fname):
        data = json.load(open(fname))
        self.names = data.get("names",{})
        self.roles = {}
        for name in self.names.keys():
            roles = data.get("roles",{}).get(name,[])
            if len(roles) < 2:
                self.names.pop(name)
                continue
            self.roles[name] = roles
        self.scenes = []
        self.scene2name = {}
        for key,val in self.names.items():
            scenename = "%s:%s" % (key, val)
            self.scenes.append(scenename)
            self.scene2name[key] = scenename
        self.games = {}
        if len(self.roles) < 3:
            print "Error Handle"
            return

    def create(self, player_count, upper, lower = 0, scene_count = 10, spyschool = 0):
        game = {}
        game["upper"] = upper
        game["lower"] = lower
        game["spy_count"] = random.randint(lower, upper)
        game["count"] = player_count
        max_scene = len(self.roles.keys())
        if scene_count > max_scene:
            scene_count = max_scene
        scenes = random.sample(self.roles.keys(), scene_count)
        game["scenes"] = map(lambda s:self.scene2name[s], scenes)
        loc = random.choice(scenes)
        game["scenecount"] = scene_count
        game["loc"] = "%s:%s" % (loc, self.names[loc])
        players = [u"Spy:间谍"] * game["spy_count"]
        remain = player_count - game["spy_count"]
        roles = self.roles[loc]
        while remain >= len(roles):
            players += roles
            remain -= len(roles)
        if remain > 0:
            players += random.sample(roles, remain)
        random.shuffle(players)
        if spyschool == 1:
            if random.randint(0,scene_count) == 0:
                players = [u"Spy:间谍"] * player_count
        game["spyschool"] = spyschool
        game["players"] = players
        game["roles"] = roles
        return game

if __name__ == "__main__":
    spyfall = SpyFalls()
    ids = [spyfall.create(5,1,1, "zh-cn-26"), spyfall.create(9,2,0,"zh-tw-52"), spyfall.create(15,3,1,"full")]
    for id in ids:
        spyfall.print_game(id)
