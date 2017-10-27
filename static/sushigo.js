var rules = '每次选一个寿司然后回转然后计分！';

var socks = null;
var id2card = {};

var new_game = function(){
    if (!confirm("确定新建游戏？？")){
        return;
    }
    var count = parseInt($("#count").val());
    var url = "./create?type=sushigoparty&count="+count;
    console.log(url);
    window.location.href = url;
}
var card_name = function(card){
    var card_name = card.name;
    if (card.type == "Nigiri"){
        card_name = card.sub_name;
    }
    if (card.name == "maki" || card.name == "uramaki"){
        card_name = card.name + ":" + card.count;
    }
    if (card.name == "fruit"){
        fruit_names = {"w":"Watermelon", "p":"Pineapple", "o":"Orange"}
        card_name = card.name + ":" + fruit_names[card.fruit[0]] + " "+fruit_names[card.fruit[1]];
    }
    return card_name;
}
var show_foods = function(game, idx){
    $(".players .foods").remove();
    var cards = $("<div></div>").addClass("foods");
    var divs = [];
    for (var i in game.player_cards[idx]){
        var card = game.player_cards[idx][i];
        var card_div = $("<div></div>").addClass("action food").attr("name", card_name(card));
        var name = card.name;
        if (card.sub_name){
            name = card.sub_name;
        }
        var img = $("<img></img>").attr("src","/static/sushigo/cards/"+name+".png");
        card_div.append(img);
        (function(idx, div){
            div.click(function(){
                if (!confirm("确定选择 "+div.attr("name")+" 吗?")){
                    return;
                }
                var data = {
                    "type": "choose_card",
                    "player":game.my_idx,
                    "card_idx": idx,
                    "id": game.id};
                console.log(data);
                sock.emit("action", {"args": data});
            })
        })(i, card_div);
        card_div.append($("<p></p>").text(card_name(card)));
        divs.push(card_div);
    }
    divs.sort(function(v1,v2){return v1.attr("name") < v2.attr("name");});
    for (var i in divs){
        cards.append(divs[i]);
    }
    cards.append($("<div style='clear:both'></div>"));
    $(".players").append(cards);
    $("")
}
var get_my_role = function(game, idx){
    var players = game.players;
    $(".players").html("");
    $(".sit").addClass("hidden");
    var score = 0;
    for (var i=1;i<game.round;i++){
        score += game.score[i][game.my_idx];
        console.log(score);
    }
    if (game.dessert_score != undefined){
        score += game.dessert_score[idx];
    }
    $(".players").append($("<div></div>").text("您的编号是"+idx+"号"));
    $(".players").append($("<div></div>").attr("id","score").text("您的分数是"+score+"分"));
    if (game.status == "Finished"){
        $("#score").text("您的最终得分是"+score+"分");
        return ;
    }
    if (game.player_cards[idx].length == 0){
        var div = $("<div></div>").addClass("btn action compute").text("开始计算分数");
        div.click(function(){
            var data = {
                "type": "update_score",
                "id": game.id,
            }
            sock.emit("action", {"args":data});
        });
        $(".players").append(div);
        return;
    }else{
        show_foods(game, idx);
    }
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
                get_my_role(game, idx);
                game.my_idx = idx;
            });
        });
    });
}
var game = null;
var all_chosen = function(result){
    var hint = "";
    for (var i in result){
        hint += "\n玩家"+i+"选择了"+card_name(game.player_cards[i][result[i]]);
        game.player_cards[i] = game.player_cards[i].slice(0, result[i]).concat(game.player_cards[i].slice(result[i]+1));
    }
    alert(hint);
    game.player_cards.push(game.player_cards.shift());
    get_my_role(game, game.my_idx);
}
var do_actions = function(msg){
    console.log(msg);
    if (msg.data.type == "all_chosen"){
        all_chosen(msg.data.result);
    }
    if (msg.data.type == "score"){
        window.location.reload();
        //alert("回合"+msg.data.round+"的分数为"+msg.data.score[game.my_idx]);
        //game.round = msg.data.round + 1;
        //get_my_role(game, game.my_idx);
    }
}
var update_tiles = function(tiles){
    console.log(tiles);
    for (var i in tiles){
        var tile = tiles[i];
        var tile_div = $("<div class='tile'></div>");
        tile_div.append($("<img></img>").attr("src", "/static/sushigo/tiles/"+tile+".png"));
        $(".tiles").prepend(tile_div);
        console.log(tile_div);
    }
}
$(document).ready(function(){
    $(".rules").html(rules);
    sock = io.connect("http://" + document.domain + ":" + location.port + "/sock");
    $.get("/status"+location.search,"",function(data){
        game = data.game;
        game.my_idx = data.my_idx;
        console.log(data);
        update_tiles(game.cards_type);
        for (var i in game.player_cards){
            for (var j in game.player_cards[i]){
                id2card[game.player_cards[i][j].id] = game.player_cards[i][j];
            }
        }
        sock.emit("join",{"id":game.id});
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
        var h = document.body.clientWidth/30;
        $(".word").css("font-size",h);
        $(".word p").css("height",h);
        $(".hint").append("<p>分享此页面给朋友们即可开始玩耍！</p>");
    });
});
