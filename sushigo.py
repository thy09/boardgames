#! encoding=utf-8

# Creation Date: 2017-10-26 20:30:26
# Created By: Heyi Tang

import random
import copy
from collections import defaultdict

ALL_TYPES = {
        "Nigiri":["nigiri"],
        "Maki":[
            "maki",
            "uramaki",
            "temaki",
            ],
        "Appetizers":[
            "tempura", "sashimi", "dumpling",
            "eel", "tofu",
            "onigiri", "edamame",
            "miso soup",
            ],
        "Special": [
            "soy sauce",
            "tea",
            "wasabi",
         #   "chopsticks",
            ],
        "Dessert": [
            "pudding",
            "green tea ice cream",
            "fruit",
            ],
        }
type_needed = {
        "Nigiri":1,
        "Maki":1,
        "Appetizers":3,
        "Special": 2,
        "Dessert":1,
        }
name2type = {}
for type_name, names in ALL_TYPES.items():
    for name in names:
        name2type[name] = type_name

class CardsGenerator:
    typecount = {
            "Nigiri": 12,
            "Maki": 12,
            "Appetizers": 8,
            "Special": 3,
            "Dessert": 15,
            }
    def __init__(self):
        self.name2type = name2type
        self.generators = {
                "maki": self.gen_maki,
                "uramaki": self.gen_uramaki,
                "nigiri": self.gen_nigiri,
                "fruit": self.gen_fruit,
                "onigiri": self.gen_onigiri,
                }

    def gen_cards(self, name):
        if name in self.generators:
            return self.generators[name](name)
        return self.gen_normal_cards(name)

    def gen_normal_cards(self, name):
        result = []
        for i in xrange(self.typecount[self.name2type[name]]):
            result.append({"name":name, "type":self.name2type[name]})
        return result

    def gen_nigiri(self, name):
        result = []
        nigiries = {"egg":[5,1], "salmon":[4,2], "squid": [3,3]}
        id = 0
        for subname, count_score in nigiries.items():
            count, score = count_score
            for i in range(count):
                result.append({"type": "Nigiri", "name":name, "sub_name":"%s %s"%(subname, name)})
                id += 1
        return result

    def gen_onigiri(self, name):
        cards = self.gen_normal_cards(name)
        for i, card in enumerate(cards):
            card["shape"] = i/3
        return cards

    def gen_maki(self, name):
        maki = self.gen_normal_cards(name)
        for idx, card in enumerate(maki):
            card["count"] = (idx/4)+1
        return maki

    def gen_uramaki(self, name):
        maki = self.gen_normal_cards(name)
        for idx, card in enumerate(maki):
            card["count"] = (idx/4)+3
        return maki

    def gen_fruit(self, name):
        fruit = self.gen_normal_cards(name)
        types = ["ww"]*2 + ["oo"]*2 + ["pp"]*2 + ["wo"]*3 + ["wp"]*3 + ["po"]*3
        for idx, card in enumerate(fruit):
            card["fruit"] = types[idx]
        return fruit

class SushiGoParty:
    count2cards = [0,0,10,10,9,9,8,8,7,6,5]
    des_idx = [[0,5,8,10],[0,7,12,15]]
    def __init__(self):
        self.cards_generator = CardsGenerator()
        self.actions = {"choose_card": self.choose_card,
                "update_score": self.update_score,
                }
        self.score_funcs = {"tea":self.score_tea,
                "soy sauce": self.score_soysauce,
                "onigiri": self.score_onigiri,
                "edamame": self.score_edamame,
                "temaki": self.score_maki,
                "uramaki": self.score_uramaki,
                "maki": self.score_maki,
                }
        self.cards_types = {}
        self.choose_actions = {"nigiri": self.choose_nigiri,
                }
        self.chosen_actions = {"nigiri": self.chosen_nigiri,
                }

    def create(self, args):
        game = {"type": "SushiGoParty", "tpl":"sushigo.html"}
        count = game["count"] = int(args.get("count", 2))
        game["round"] = 1
        game["turn"] = 0
        game["cards_type"] = self.parse_cards_type(args.get("cards_type","random"))
        game["players"] = [None] * count
        foods, des = self.gen_cards(game["cards_type"])
        game["chosen"] = []
        game["food_counted"] = {}
        for i in range(4):
            temp = []
            for j in range(count):
                temp.append([])
            game["chosen"].append(temp)
        offset = 5
        if count>5:
            offset = 7
        foods_round = foods + des[:offset]
        random.shuffle(foods_round)
        cards_per_player = self.count2cards[count]
        game["cpp"] = cards_per_player
        game["score"] = [[], [], [], []]
        game["total_foods"] = [[],[],[],[]]
        game["total_desserts"] = [defaultdict(int) for i in range(count)]
        if "fruit" in game["cards_type"]:
            for i in range(count):
                for k in "owp":
                    game["total_desserts"][i]["fruit:"+k] = 0
        game["player_cards"] = []
        for i in range(count):
            game["player_cards"].append(foods_round[i*cards_per_player:(i+1)*cards_per_player])
        game["rest_cards"] = foods_round[count*cards_per_player:]
        game["rest_desserts"] = des[offset:]
        return game

    def gen_cards(self, cards_type):
        foods = []
        desserts = []
        for name in cards_type:
            type = name2type[name]
            if type == "Dessert":
                desserts = self.cards_generator.gen_cards(name)
            else:
                foods += self.cards_generator.gen_cards(name)
        #for i, food in enumerate(foods):
         #   food["id"] = i
        #for j, des in enumerate(desserts):
         #   des["id"] = i+j
        random.shuffle(foods)
        random.shuffle(desserts)
        return foods, desserts

    def random_type(self):
        types = []
        for t, needed in type_needed.items():
            types += random.sample(ALL_TYPES[t], needed)
        return "-".join(types)

    def parse_cards_type(self, cards_type):
        if cards_type == "random":
            cards_type = self.random_type()
        elif cards_type in self.cards_types:
            cards_type = self.cards_types
        types = cards_type.split("-")
        if len(types) != 8:
            return self.parse_cards_type("random")
        return types

    def do_action_sockio(self, game, args):
        if args["type"] in self.actions:
            return self.actions[args["type"]](game, args)

    def all_chosen(self, game):
        cur = game["chosen"][game["round"]]
        for chosen in cur:
            if len(chosen) <= game["turn"]:
                return False
        return True

    def chosen_result(self, game):
        cur = game["chosen"][game["round"]]
        result = {}
        for i in range(game["count"]):
            result[i] = cur[i][game["turn"]]
        return result

    def update_food(self, game):
        cur = game["chosen"][game["round"]]
        cards = game["player_cards"]
        for i in range(game["count"]):
            card = cur[i][game["turn"]]
            idx = card["idx"]
            cards[i] = cards[i][:idx] + cards[i][idx+1:]
            if self.chosen_actions.has_key(card["name"]):
                self.chosen_actions[card["name"]](cur[i], card)
        game["player_cards"] = game["player_cards"][1:] + game["player_cards"][:1]
        game["turn"] += 1
        return

    def chosen_nigiri(self, chosen, card):
        if card.get("extra",{}).get("wasabi"):
            for ch in chosen:
                if ch["name"] == "wasabi":
                    if not ch.get("extra",{}).get("used"):
                        ch["extra"] = {"used": True}
                        return

    def choose_nigiri(self, game, card, args, player):
        if "wasabi" in args:
            card["extra"] = {"wasabi": True}
    def choose_card(self, game, args):
        player = int(args["player"])
        idx = int(args["card_idx"])
        chosen = game["chosen"][game["round"]][player]
        player_turn = int(args["turn"])
        if (player_turn != game["turn"]):
            return {"dest":"me", "type":"notify", "text":"INVALID_TURN"}
        card = copy.deepcopy(game["player_cards"][player][idx])
        card["idx"] = idx
        if self.choose_actions.get(card["name"]):
            self.choose_actions[card["name"]](game, card, args, player)
        if len(chosen) != game["turn"]:
            chosen[game["turn"]] = card
        else:
            chosen.append(card)
        game["chosen"][game["round"]][player] = chosen
        if self.all_chosen(game):
            result = self.chosen_result(game)
            self.update_food(game)
            return {"type":"all_chosen", "result": result}
        return {"type":"notify", "dest": "me", "text":"Success!"}

    def update_score(self, game, args):
        if game["turn"] != game["cpp"]:
            return
        if not game["round"] in game["food_counted"]:
            self.count_food_round(game)
        if len(game["score"][game["round"]]) == 0:
            game["score"][game["round"]] = []
            for player in range(game["count"]):
                score = 0
                for key, val in game["total_foods"][game["round"]][player].items():
                    if key in self.score_funcs:
                        score += self.score_funcs[key](key, val, player, game["chosen"][game["round"]])
                    else:
                        score += self.compute_score(key, val)
                game["score"][game["round"]].append(score)
            self.next_round(game)
            result = {
                #"foods": game["total_foods"][game["round"]], 
                #"desserts": game["total_desserts"],
                "score": game["score"][game["round"]-1],
                "type": "score",
                "round": game["round"]-1,
                }
            return result
    def compute_dessert(self, game):
        game["dessert_score"] = []
        if "pudding" in game["cards_type"]:
            puddings = []
            for player_d in game["total_desserts"]:
                puddings.append(player_d.get("pudding", 0))
            puddings.sort(reverse = True)
            for player in range(game["count"]):
                my_pudding = game["total_desserts"][player].get("pudding", 0)
                result = 0
                if my_pudding == puddings[0]:
                    result = 6
                elif my_pudding == puddings[-1] and game["count"] > 2:
                    result = -6
                game["dessert_score"].append(result)
            return
        for player in range(game["count"]):
            score = 0
            for k,v in game["total_desserts"][player].items():
                score += self.compute_score(k, v)
            game["dessert_score"].append(score)
    def score_soysauce(self, key, val, idx, chosen):
        colors = []
        max_color = 0
        for ch in chosen:
            type_set = set()
            for card in ch:
                type_set.add(card["name"])
            colors.append(len(type_set))
            max_color = max(max_color, len(type_set))
        if colors[idx] == max_color:
            return val * 4
        return 0

    def score_tea(self, key, val, idx, chosen):
        type_count = defaultdict(int)
        for card in chosen[idx]:
            type_count[card["name"]] += 1
        return val * max(type_count.values())

    def score_onigiri(self, key, val, idx, chosen):
        ch = chosen[idx]
        counts = [0] * 4
        for food in ch:
            if key == food["name"]:
                counts[food["shape"]] += 1
        counts.sort()
        now = 0
        total = 0
        vals = [16, 9, 4, 1]
        for i, count in enumerate(counts):
            if count > now:
                total += (count - now) * vals[i]
                now = count
        return total

    def score_uramaki(self, key, val, idx, chosen):
        if val < 10:
            return 0
        scores = [8, 5, 2]
        makies = [0] * len(chosen)
        total = 0
        for i in range(len(chosen[0])):
            if len(scores) == 0:
                break
            for j in range(len(chosen)):
                if chosen[j][i]["name"] == key:
                    makies[j] += chosen[j][i]["count"]
            sort_makies = filter(lambda v:v>=10, makies)
            sort_makies.sort(reverse = True)
            added = False
            for v in sort_makies:
                if not added and makies[idx] == v:
                    added = True
                    total += scores[0]
                scores = scores[1:]
                if len(scores) == 0:
                    break
            for i in range(len(makies)):
                if makies[i] >= 10:
                    makies[i] = 0
        return total

    def score_maki(self, key, val, idx, chosen):
        user_makis = [0] * len(chosen)
        totals = []
        for ch in chosen:
            total = 0
            for card in ch:
                if card["type"] == "Maki":
                    total += len(self.card_keys(card))
            totals.append(total)
        totals.sort(reverse = True)
        if key == "maki":
            if val == totals[0]:
                return 6
            if len(chosen) < 6 and val == totals[1]:
                return 3
            if val == totals[1]:
                return 4
            if len(chosen)>=6 and val == totals[2]:
                return 2
        if key == "temaki":
            if val == totals[0]:
                return 4
            if val == totals[-1] and len(chosen)>2:
                return -4
        return 0

    def score_edamame(self, key, val, idx, chosen):
        enemies = -1
        for foods in chosen:
            for food in foods:
                if food["name"] == key:
                    enemies += 1
                    break
        return val * enemies

    def next_round(self, game):
        game["turn"] = 0
        game_round = game["round"]
        if game_round == 3:
            game["status"] = "Finished"
            game["round"] = 4
            self.compute_dessert(game)
            return
        chosen = game["chosen"][game_round]
        to_choose = [7,5,3]
        if game["count"]<6:
            to_choose = [5,3,2]
        cards = game["rest_cards"] + game["rest_desserts"][:to_choose[game_round]]
        game["rest_desserts"] = game["rest_desserts"][to_choose[game_round]:]
        for player in range(game["count"]):
            for card in chosen[player]:
                if card["type"] != "Dessert":
                    new_card  = copy.deepcopy(card)
                    if "extra" in new_card:
                        new_card.pop("extra")
                    new_card.pop("idx")
                    cards.append(new_card)
        random.shuffle(cards)
        for i in range(game["count"]):
            game["player_cards"][i] = cards[i*game["cpp"]:(i+1)*game["cpp"]]
        game["rest_cards"] = cards[game["count"]*game["cpp"]:]
        game["round"] += 1

    def compute_score(self, key, val):
        if key in ["squid nigiri", "miso soup"]:
            return val*3
        elif key == "squid nigiri:w":
            return val*9
        elif key == "salmon nigiri":
            return val*2
        elif key == "salmon nigiri:w":
            return val*6
        elif key == "egg nigiri":
            return val
        elif key == "egg nigiri:w":
            return val*3
        elif key == "eel":
            return [0, -3, 7][min(val, 2)]
        elif key == "tofu":
            return [0, 2, 6, 0][min(val, 3)]
        elif key == "tempura":
            return val / 2 * 5
        elif key == "sashimi":
            return val / 3 * 10
        elif key == "dumpling":
            return [0, 1, 3, 6, 10, 15][min(val, 5)]
        elif key == "green tea ice cream":
            return (val / 4) * 12
        elif key in ["fruit:o", "fruit:w", "fruit:p"]:
            return [-2, 0, 1, 3, 6, 10][min(val, 5)]
        return 0

    def card_keys(self, food):
        if food["name"] == "nigiri":
            if food.get("extra",{}).get("wasabi"):
                return ["%s:w" % food["sub_name"]]
            return [food["sub_name"]]
        if food["name"] in ["maki", "uramaki"]:
            return food["count"] * [food["name"]]
        if food["name"] == "fruit":
            return map(lambda c:"fruit:"+c,list(food["fruit"]))
        return [food["name"]]

    def count_food_round(self, game):
        chosen = game["chosen"][game["round"]]
        game["total_foods"][game["round"]] = []
        for player in range(game["count"]):
            player_foods = defaultdict(int)
            for key in ["maki", "temaki"]:
                if key in game["cards_type"]:
                    player_foods[key] = 0
            for i in range(game["cpp"]):
                card = chosen[player][i]
                card_keys = self.card_keys(card)
                if card["name"] == "miso soup":
                    for j in range(game["count"]):
                        if chosen[j][i]["name"] == card["name"] and j != player:
                            card_keys = ["miso soup:discarded"]
                if card["type"] != "Dessert":
                    for card_key in card_keys:
                        player_foods[card_key] += 1
                else:
                    for card_key in card_keys:
                        game["total_desserts"][player][card_key] += 1
            game["total_foods"][game["round"]].append(player_foods)
        game["food_counted"][game["round"]] = True

    def game_info(self, game):
        result = {}
        for key, val in game.items():
            if key in ["rest_cards", "rest_desserts"]:
                continue
            result[key] = val
        return result

if __name__ == "__main__":
    sushi = SushiGoParty()
    game = sushi.create({"count":2})
    #for k,v in game.items():
     #   print k,v
    for i in range(game["count"]):
        game["chosen"][1][i] = game["player_cards"][i]
    game["turn"] = game["cpp"]
    for ch in game["chosen"][1]:
        print "Food:"
        print "\n".join(map(str,ch))

    sushi.update_score(game,{})
    sushi.compute_dessert(game)
    print game["score"]
    print game["total_desserts"]
    print game["dessert_score"]
