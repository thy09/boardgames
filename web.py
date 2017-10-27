#! encoding=utf-8

# Creation Date: 2017-10-20 10:02:56
# Created By: Heyi Tang

from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask import g
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms

import game_manager

import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = 'thyplayboardgame'
sockio = SocketIO(app)
manager = game_manager.GameManager()

@sockio.on("connect", namespace = "/sock")
def connect():
    pass
@sockio.on("join", namespace="/sock")
def join(msg):
    roomid = str(msg["id"])
    join_room(roomid)

@sockio.on("action", namespace = "/sock")
def sockio_action(msg):
    args = msg["args"]
    id = args.get("id", 0)
    game = manager.game(id)
    if not game:
        return
    result = manager.do_action_sockio(game, args)
    if result is not None:
        emit("action", {"data": result}, room = str(game["id"]))

@app.before_request
def before_request():
    uid = request.cookies.get("UID")
    if not uid or not manager.exist_user(uid):
        uid = manager.new_user()
    manager.update_user(uid)
    g.uid = uid

@app.after_request
def after_request(resp):
    uid = request.cookies.get("UID")
    if uid != g.uid:
        resp.set_cookie("UID", g.uid)
    return resp

@app.route("/")
def index():
    return redirect(url_for(".create"))

@app.route("/create")
def create():
    count = int(request.args.get("count", 8))
    if count<2:
        return "INVALID_PLAYER_COUNT"
    args = {}
    for k in request.args.keys():
        args[k] = request.args[k]
    game_type = request.args.get("type", "werewords")
    id = manager.create(game_type, args)
    game = manager.game(id)
    return redirect(url_for(".play", id = id, type = game["type"].lower()))

@app.route("/play")
def play():
    id = request.args.get("id", 0)
    game = manager.game(id)
    if game is None:
        return redirect(url_for(".create", type = request.args.get("type", "werewords")))
    return render_template(game["tpl"], game = game)

@app.route("/status")
def status():
    id = request.args.get("id", 0)
    game = manager.game_info(id)
    if not game:
        return jsonify({"status":"INVALID_ID"})
    data = {"game":game, "status":"success"}
    if "occupied" in game:
        for idx, uid in enumerate(game["occupied"]):
            if uid == g.uid:
                data["my_idx"] = idx
            if not manager.exist_user(uid):
                game["occupied"][idx] = None
    return jsonify(data)

@app.route("/action", methods = ["POST"])
def action():
    id = request.args.get("id", 0)
    game = manager.game(id)
    if not game:
        return jsonify({"status":"INVALID_ID"})
    data = request.get_json()
    result = manager.do_action(game, data)
    return jsonify(result)

@app.route("/sit")
def sit():
    id = request.args.get("id")
    idx = request.args.get("idx")
    if manager.user_sit(id, idx, g.uid):
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"OCCUPIED"})

@app.route("/show_users")
def show_users():
    result = {}
    for k,v in manager.users.items():
        result[k] = str(v)
    return jsonify(result)

if __name__ == "__main__":
    app.debug = True
    sockio.run(app, port = 29999)
    #app.run(host = "0.0.0.0", port = 29999)
