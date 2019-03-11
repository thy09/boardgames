#! encoding=utf-8

# Creation Date: 2017-10-26 11:00:04
# Created By: Heyi Tang

import os
import codecs
import random

VAR_ROLES = {
        "wolf":1,
        "beholder":0,
        "minion":0,
        }
CONST_ROLES = {
        "mayor":1,
        "seer": 1,
        }

class WereWords:
    actions = {"choose_word": "choose_word", "view_word":"view_word"}
    def __init__(self):
        self.word_dicts = {}
        self.all_words = set()
        initials = ["codenames"]
        for name in initials:
            self.load_words(name)

    def gen_words(self, dict_name, candidates):
        words = self.word_dicts.get(dict_name)
        if words is None and dict_name is not None:
            words = self.load_words(dict_name)
        if words is None:
            words = self.all_words
        return random.sample(words, candidates)

    def load_words(self, name):
        fname = "./res/%s.words" % name
        if os.path.exists(fname):
            words = set()
            for line in codecs.open(fname, encoding = "utf-8"):
                words.add(line.rstrip())
                self.all_words.add(line.rstrip())
            self.word_dicts[name] = words
            return words

    def create(self, args):
        game = {"type": "Werewords", "tpl":"werewords.html"}
        game["count"] = int(args.get("count", 6))
        villagers = game["count"] + 1
        game["players"] = []
        for role, count in CONST_ROLES.items():
            villagers -= count
            game["players"] += [role] * count
        for role, count in VAR_ROLES.items():
            game[role] = int(args.get(role, count))
            villagers -= game[role]
            game["players"] += [role] * game[role]
        if villagers < 0:
            return None
        game["players"] += ["villager"] * villagers
        random.shuffle(game["players"])
        game["candidates"] = int(args.get("candidates", 5))
        game["words"] = self.gen_words(args.get("dict"), game["candidates"])
        return game

    def view_word(self, game, data):
        if "word" in game:
            return {"status":"success", "word":game["word"]}
        return {"status":"to_choose"}

    def choose_word(self, game, data):
        game["word"] = game["words"][int(data["idx"])]
        return {"status":"success", "word": game["word"]}

    def do_action(self, game, data):
        if not data.get("type") in WereWords.actions:
            return {"status": "INVALID_TYPE"}
        return getattr(self, self.actions[data["type"]])(game, data)

