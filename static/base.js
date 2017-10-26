function postJson(url, param, action){
    $.ajax({url: url, 
                type: "post",
                data:JSON.stringify(param),
                dataType:"json",
                contentType:"application/json",
                success: action,
    })
}