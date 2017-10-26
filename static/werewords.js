var rules = '<h2>游戏规则</h2>' + 
        '<h3>基本配置</h3>' + 
        '<p>每一盘游戏会有n+1个角色，市长/预言家各1个，其余是狼人和村民</p>' + 
        '<p>市长会被分配到若干可选词汇，它在其中挑选一个作为题目</p>' + 
        '<p>狼人和预言家知道词汇是什么，村民不知道</p>' + 
        '<h3>游戏目标</h3>' + 
        '<p>好人方胜利条件: 猜出词汇且预言家不被狼人发现，或没猜出词汇但指认出了狼人。</p>' + 
        '<h3>游戏流程</h3>' + 
        '<p>首先市长亮出自己的身份，同时他查看多余的身份，那个身份则是他的隐藏身份。</p>' + 
        '<p>若没有人被分配到市长，则随机选择一个市长，他本来的身份即他的隐藏身份。</p>' + 
        '<p>市长根据自己隐藏身份的阵营，从可选词汇列表中选出一个词汇作为谜题。</p>' + 
        '<p>预言家和狼人分别查看市长选出的词汇。</p>' +
        '<p>白天环节开始，市长不允许说话，其他人依次向市长提出一个是/否的问题，</p>' +
        '<p>市长可以回答 是/否/不知道/较接近</p>' +
        '<p>如果回答是/否则需要消耗“是否次数”</p>' +
        '<p>其他人提问前可以自由讨论，但是市长除了回答问题之外禁止任何发言</p>' +
        '<h3>游戏结算</h3>' + 
        '<p>限定时间(一般设为4分钟)到或某个问题之后"是否次数"被耗尽，则进行猜词。</p>' + 
        '<p>1. 猜测正确，狼人亮出身份并指认预言家(15秒内决定)，若指认成功，狼人获胜，否则好人获胜。</p>' + 
        '<p>2. 猜测错误，则大家用最后1分钟时间讨论谁是狼人，然后立即投票。若指认成功，则好人获胜，否则狼人获胜。</p>';


var names = {"wolf":"狼人", "seer":"预言家", "mayor":"市长", "villager":"村民", "minion":"爪牙", "beholder":"观察者",
"candidates":"待选词语"};
var vars = {"wolf": 1, "minion":0, "beholder":0, "candidates":5};
var new_game = function(){
    if (!confirm("确定新建游戏？？")){
        return;
    }
    var count = parseInt($("#count").val());
    var url = "./create?count="+count;
    for (role in vars){
        url += "&"+role+"="+$("#"+role).val();
    }
    console.log(url);
    window.location.href = url;
}
var get_my_role = function(game, idx){
    var players = game.players;
    var div = $("<div class='p'></div>").text("编号"+idx+"的身份是:" + names[game.players[idx]]);     
    $(".players").prepend(div);
    if (players[idx] == "mayor"){
        $(".players").append($("<p></p>").text("暗中身份是"+names[game.players[game.count]]));
        if (game.word !== undefined){
            $(".players").append($("<p>目标词汇为 "+ game.word +"</p>"));
            return;
        }
        var choose_div = $("<div class='choose'></div>");
        choose_div.append($("<h3>待选词语如下，请点击需要的词语</h3>"));
        for (var j in game.words){
            var div = $("<div class='btn action'></div>").text(game.words[j]);
            (function(div, idx){
                div.click(function(){
                    var data = {"type": "choose_word", "idx": idx};
                    var url = "/action"+location.search;
                    postJson(url, data, function(res){
                        if (res.status == "success"){
                            $(".choose").remove();
                            $(".players").append($("<p>目标词汇为 "+ res.word +"</p>"));
                        }
                    });
                });
            })(div, j)
            choose_div.append(div);
        }
        $(".players").append(choose_div);
    }
    if (players[idx] == "wolf" || players[idx] == "seer"){
        if (game.word !== undefined){
            $(".players").append($("<p>目标词汇为 "+ game.word +"</p>"));
        }else{
            var div = $("<div class='btn action'></div>").text("查看目标词汇");
            div.click(function(){
                var data = {"type":"view_word"};
                var url = "/action"+location.search;
                postJson(url, data, function(res){
                    if (res.status == "success"){
                        div.remove();
                        $(".players").append($("<p>目标词汇为 "+ res.word +"</p>"));
                    }
                    if (res.status == "to_choose"){
                        alert("等待市长选择词汇");
                    }
                });
            });
            $(".players").append(div);
        }
    }
    if (players[idx] == "beholder"){
        for (var i in players){
            if (players[i] == "seer"){
                $(".players").append($("<p>"+i+"号玩家为预言家</p>"));
            }
        }
    }
    if (players[idx] == "minion" || players[idx] == "wolf"){
        for (var i in players){
            if (players[i] == "wolf" && i != idx){
                if (i != game.count){
                    $(".players").append($("<p>"+i+"号玩家为狼人</p>"));
                }else
                {
                    $(".players").append($("<p>市长为狼人</p>"));                   
                }
            }
        }
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
            });
        });
    });
}
$(document).ready(function(){
    $(".rules").html(rules);
    $.get("/status"+location.search,"",function(data){
        var game = data.game;
        console.log(data);
        $("title").text("Werewords:"+game.id);
        if (data.my_idx === undefined){
            add_players(game);
        }else{
            get_my_role(game, data.my_idx);
        }
        var max_count = 30;
        var max_scene = 50;
        for (var i=2;i<=max_count;i++){
            $("#count").append($("<option value='"+i+"'>"+i+"</option>"));
        }
        $("#count").val(game.count);
        for (var role in vars){
            var div = $("<div></div>");
            div.append($("<label></label>").text(names[role]+"数量:"));
            var sel = $("<select></select>").attr("id", role);
            for (var i=0;i<=max_count;i++){
                sel.append($("<option value='"+i+"'>"+i+"</option>"));
            }
            div.append(sel);
            sel.val(game[role]);
            $(".newgame").append(div);
        }
        var h = document.body.clientWidth/30;
        $(".word").css("font-size",h);
        $(".word p").css("height",h);
        $(".hint").append("<p>分享此页面给朋友们即可开始玩耍！</p>");
    });
});
