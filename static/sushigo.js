var rules = '每次选一个寿司然后回转然后计分！';

var socks = null;
var names = {"egg nigiri":"鸡蛋手握", "salmon nigiri": "三文鱼手握", "squid nigiri":"鱿鱼手握",
                "maki": "寿司卷", "uramaki": "里卷", "temaki": "手卷",
                "dumpling": "煎饺", "edamame" : "青豆", "eel":"鳗鱼寿司", "onigiri":"饭团",
                "miso soup": "味增汤", "sashimi": "刺身", "tempura": "天妇罗", "tofu":"豆腐",
                "chopsticks":"筷子", "wasabi": "芥末", "soy sauce":"酱油", "tea": "茶",
                "green tea ice cream": "抹茶冰淇淋", "pudding":"布丁",
                "fruit:o":"橘子", "fruit:w":"西瓜","fruit:p":"菠萝"
            }
var check_wasabi = function(game, idx, args){
    var chosen = game.chosen[game.round][game.my_idx];
    console.log(chosen);
    for (var i in chosen){
        console.log(chosen[i]);
        if (chosen[i].name == "wasabi" && (!(chosen[i].extra && chosen[i].extra.used))){
            if (!confirm("是否使用芥末?")){
                return true;
            }
            args["wasabi"] = i;
            return true
        }
    }
    return true;
}
var card_actions = {
    "nigiri": check_wasabi,
}
var new_game = function(cards_type){
    if (!confirm("确定新建游戏？？")){
        return;
    }
    var count = parseInt($("#count").val());
    var url = "./create?type=sushigoparty";
    var args = {}
    $(".newgame select").each(function(idx, elm){
        args[$(elm).attr("id")] = elm.value;
    })
    if (cards_type){
        args["cards_type"] = cards_type;
    }
    for (var k in args){
        url += "&" + k + "=" + args[k];
    }
    console.log(args);
    console.log(url);
    window.location.href = url;
}
var card_name = function(card){
    var card_name = card.name;
    if (card.type == "Nigiri"){
        card_name = names[card.sub_name];
        if (card.extra && card.extra.wasabi){
            card_name += "蘸芥末";
        }
        return card_name;
    }
    if (card.name == "maki" || card.name== "uramaki"){
        return names[card.name] +"*"+card.count;
    }
    if (card.name == "fruit"){
        fruit_names = {"w":"西瓜", "p":"菠萝", "o":"橘子"}
        return fruit_names[card.fruit[0]] + fruit_names[card.fruit[1]];
    }
    if (names[card_name]){
        card_name = names[card_name];
    }
    if (card.name == "onigiri"){
        var shapes = ["三角", "长", "圆", "方"]
        return card_name +":"+shapes[card.shape];
    }
    return card_name;
}
var simple_name = function(card){
    if (card.name == "maki" || card.name == "uramaki"){
        return card.count;
    }   
    if (card.name == "fruit"){
        fruit_names = {"w":"瓜", "p":"菠", "o":"橘"}
        return fruit_names[card.fruit[0]] + fruit_names[card.fruit[1]];
    }
    if (card.name == 'nigiri' && card.extra && card.extra.wasabi){
        return "芥末";
    }
    return "-";
}
var emit_timer = null;
var emit_action = function (game, type, args){
    if (args == undefined){
        args = {};
    }
    args["id"] = game.id;
    args["uid"] = game.uid;
    args["player"] = game.my_idx;
    args["type"] = type;
    console.log(args);
    $("#popout").removeClass("hidden").addClass("loading");
    emit_timer = setTimeout(function(){window.location.reload();},3000);
    sock.emit("action",{"args": args});
}
var show_foods = function(game, idx){
    $(".players .foods").remove();
    $(".players .play").remove();
    $(".players").append($("<p>请选择您的食物!</p>").addClass("play"));
    var cards = $("<div></div>").addClass("foods");
    var divs = [];
    for (var i in game.player_cards[idx]){
        var card = game.player_cards[idx][i];
        var card_div = get_card_div(card);
        (function(idx, div, card){
            div.click(function(){
                if (!confirm("确定选择 "+div.attr("name")+" 吗?")){
                    return;
                }
                var args = {"card_idx": idx, "turn": game["turn"]};
                console.log(card.name);
                if (card_actions[card.name]){
                    var func = card_actions[card.name];
                    console.log(func);
                    var ok = func(game, idx, args);
                    if (!ok){
                        return;
                    }
                }
                emit_action(game, "choose_card", args);
                cards.append($("#choice .food").removeClass("chosen"));
                cards.append($(".foods .clear"))
                $("#choice").append(div.addClass("chosen"));
            })
        })(i, card_div, card);
        if (game.chosen[game.round][idx].length > game.turn && game.chosen[game.round][idx][game.turn].idx == i){
            card_div.addClass("chosen");
        }
        divs.push(card_div);
    }
    divs.sort(function(v1,v2){return v1.attr("name") < v2.attr("name");});
    for (var i in divs){
        cards.append(divs[i]);
    }
    cards.append($("<div></div>").addClass("clear"));
    $(".players").append($("<div></div>").attr("id","choice"));
    $(".players").append(cards);
    $("#choice").append(cards.find(".chosen"));           
}
var get_card_div = function(card, in_order){
    var card_div = $("<div></div>").addClass("action food").attr("name", card_name(card));
    var name = card.name;
    if (card.sub_name){
        name = card.sub_name;
    }
    if (card.name == "onigiri"){
        name = card.name + card.shape;
    }
    if (card.name == "uramaki" || card.name == "maki"){
        name = card.name + card.count;
    }
    if (card.name == "fruit"){
        name = card.name + card.fruit;
    }
    var div = $("<div></div>").addClass("card");
    div.attr("style","background: url('/static/sushigo/cards/"+name+".png');background-size: cover;");
    card_div.append(div);
    name = card_name(card);
    if (in_order){
        name = simple_name(card);
    }
    card_div.append($("<p></p>").text(name));
    return card_div;
}
var get_cards_div = function(cards, in_order){
    var div = $("<div></div>");
    var turn = game.turn;
    if (cards.length == game.cpp){
        turn = game.cpp;
    }
    for (var i =0;i<turn;i++){
        div.append(get_card_div(cards[i], in_order));
    }
    div.append($("<div></div>").addClass("clear"));
    return div;
}
var show_my_order = function(game, idx){
    $(".my_order").html(one_order(game, idx, "您"));
}
var dessert_desc = function(desserts){
    var result = [];
    for (k in desserts){
        var count = desserts[k];
        if (count == 0){
            continue;
        }
        if (names[k]){
            k = names[k];
        }
        result.push(k+"*"+count);
    }
    return result.join(',');
}
var show_orders = function(game){
    $(".orders > div").remove();
    for (var i in game.chosen[game.round]){
        if (i == game.my_idx){
            continue;
        }
        $(".orders").append(one_order(game, i));
    }
}
var one_order = function(game, i, name){
    var chosen = game.chosen[game.round][i];
    var div = $("<div></div>").attr("id", "order"+i);
    var myname = "玩家"+i;
    if (name){
        myname = name;
    }
    div.append($("<p>"+myname+"的当前菜单:</p>"));
    div.append(get_cards_div(chosen, true));
    div.append($("<p>"+myname+"屯的小吃:"+dessert_desc(game.total_desserts[i])));
    return div;
}
var show_history = function(game){
    if (game.round < 2 || $(".history p").length > 0){
        return;
    }
    for (var i=0;i<game.count;i++){
        var history = [];
        var total = 0;
        for (var j=1;j<game.round;j++){
            total += game.score[j][i];
            history.push(game.score[j][i]);
        }
        if (game.status == "Finished"){
            total += game.dessert_score[i];
            history.push(game.dessert_score[i]);
        }
        $(".history").append($("<p></p>").text("玩家"+i+"的得分:"+history.join(",")+",总共"+total));
        for (var j=1;j<game.round;j++){
            console.log(game.chosen[j][i]);
            var div = get_cards_div(game.chosen[j][i],true);
            $(".history").append(div);
            console.log(div);
        }
    }
}
var get_my_role = function(game, idx){
    var players = game.players;
    $(".players").html("");
    $(".sit").addClass("hidden");
    var score = 0;
    for (var i=1;i<game.round;i++){
        score += game.score[i][game.my_idx];
    }
    if (game.dessert_score != undefined){
        score += game.dessert_score[idx];
    }
    $(".player_info").html("");
    $(".player_info").append($("<div></div>").text("您的编号是"+idx+"号"));
    $(".player_info").append($("<div></div>").attr("id","score").text("您的分数是"+score+"分"));
    show_history(game);
    if (game.status == "Finished"){
        $("#score").text("您的最终得分是"+score+"分");
        return ;
    }
    if (game.player_cards[idx].length == 0){
        var div = $("<div></div>").addClass("btn action compute").text("开始计算分数");
        div.click(function(){
            emit_action(game, "update_score", {});
        });
        $(".players").append(div);
    }else{
        show_foods(game, idx);
    }
    show_my_order(game, idx);
    show_orders(game);
}
var add_players = function(game){
    var players = game.players;
    for (var i in players){
        if (i == game.count){
            break;
        }
        var player = players[i];
        var div = $("<div></div>").addClass("player").attr("id", i).html("<p>" + i + "号</p>");
        $(".players").append(div);
    }
    $(".players").append("<div style='clear:both'></div>");
    $(".players .player").each(function(idx, elm){
        if (game.occupied[idx]){
            $(elm).addClass("occupied");
            return;
        }
        $(elm).click(function(){
            var idx = parseInt($(elm).attr("id"));
            if (!confirm("确定选择"+idx+"号？")){
                return;
            }
            $.get("/sit"+location.search+"&idx="+idx,"", function(res){
                if (res.status != "success"){
                    if (res.status == "OCCUPIED"){
                        alert(idx+"号已经被别人选啦!");
                        $(elm).addClass("occupied");
                        $(elm).unbind("click");
                    }else{
                        alert(res.status);
                    }
                    return;
                }
                $(".players div").remove();
                game.my_idx = idx;
                get_my_role(game, idx);
            });
        });
    });
}
var game = null;
var all_chosen = function(result){
    var hint = "";
    for (var i in result){
        hint += "\n玩家"+i+"选择了"+card_name(result[i]);
        var idx = result[i].idx;
        var chosen = game.chosen[game.round][i];
        if (result[i].name == "nigiri" && result[i].extra && result[i].extra.wasabi){
            for (var j in chosen){
                if (chosen[j].name == "wasabi" && !(chosen[j].extra && chosen[j].extra.used)){
                    chosen[j].extra = {"used":true};
                    break;
                }
            }
        }
        chosen.push(result[i]);
        game.player_cards[i] = game.player_cards[i].slice(0, idx).concat(game.player_cards[i].slice(idx+1));
    }
    alert(hint);
    game.player_cards.push(game.player_cards.shift());
    game["turn"] += 1;
    get_my_role(game, game.my_idx);
}
var do_actions = function(msg){
    $("#popout").removeClass("loading").addClass("hidden");
    clearTimeout(emit_timer);
    if (msg.data.type == "all_chosen"){
        all_chosen(msg.data.result);
    }
    if (msg.data.type == "score"){
        window.location.reload();
    }
    if (msg.data.type == "notify"){
        alert(msg.data.text);
        if (msg.data.text == "INVALID_TURN"){
            window.location.reload();
        }
    }
}
var update_tiles = function(tiles){
    for (var i in tiles){
        var tile = tiles[i];
        var tile_div = $("<div class='tile'></div>");
        tile_div.append($("<img></img>").attr("src", "/static/sushigo/tiles/"+tile+".png"));
        $(".tiles").prepend(tile_div);
    }
}
$(document).ready(function(){
    $(".rules").html(rules);
    sock = io.connect("http://" + document.domain + ":" + location.port + "/sock");
    $.get("/status"+location.search,"",function(data){
        game = data.game;
        game.my_idx = data.my_idx;
        game.uid = data.uid;
        console.log(data);
        update_tiles(game.cards_type);
        sock.emit("join",{"id":game.id, "uid": game.uid});
        sock.on("action", do_actions);
        $("title").text("寿司狗:"+game.id);
        if (data.my_idx === undefined){
            add_players(game);
        }else{
            get_my_role(game, data.my_idx);
        }
        var max_count = 10;
        for (var i=2;i<=max_count;i++){
            $("#count").append($("<option value='"+i+"'>"+i+"</option>"));
        }
        $("#count").val(game.count);
        var default_types = ["random"];
        for (var i in default_types){
            $("#cards_type").append($("<option></option>").attr("value",default_types[i]).text(default_types[i]));
        }
        var my_type = game.cards_type.join("-");
        $("#cards_type").append($("<option></option>").attr("value",my_type).text(my_type));
        $("#cards_type").val(my_type);
        var h = document.body.clientWidth/30;
        $(".word").css("font-size",h);
        $(".word p").css("height",h);
        $(".hint").append("<p>分享此页面给朋友们即可开始玩耍！</p>");
    });
});
