/**
 * Created by xuhe on 15/12/3.
 */
var Crawl = {
    get_html: function(label, url, try_times, callback){
        if(url.indexOf("https://www.wish.com/api/merchant") == 0){
            return Crawl.get_json(label, url, try_times, callback);
        }
        if(url.indexOf("gp/aag/ajax/searchResultsJson") > 0){
            return Crawl.get_json2(label, url, try_times, callback);
        }
        StatusLabel.display(label, 2, false, url);
        $.ajax({
            url: url,
            type: "GET",
            timeout: 30000,
            data: {},
            success: function(data){
                typeof(data) == "object" && (data = JSON.stringify(data));
                callback({html: data});
            },
            complete: function(XMLHttpRequest, status){
                if(status == 'timeout') {
                    StatusLabel.display(label, 1007, true);
                    try_times >= 3 ? callback({html: ""}) :
                    setTimeout(function(){
                        Crawl.get_html(label, url, try_times + 1, callback)
                    }, 5000);
                }else if(status == 'error'){
                    StatusLabel.display(label, 1002, true);
                    try_times >= 3 ? callback({html: ""}) :
                    setTimeout(function(){
                        Crawl.get_html(label, url, try_times + 1, callback)
                    }, 5000);
                }else if(status == 'parsererror'){
                    var data = XMLHttpRequest.responseText;
                    callback({html: data});
                }
            }
        });
    },
    get_json: function(label, url, try_times, callback){
        StatusLabel.display(label, 2, false, url);
        var params_list = url.split("?")[1].split("&");
        var data = {};
        for(var i=0; i<params_list.length; i++){
            var p = params_list[i].split("=");
            p[0] == "last_cids" ? (data[p[0]] = p[1].split(",")) : (data[p[0]] = p[1]);
        }
        chrome.cookies.get({url: "https://www.wish.com", name: "_xsrf"}, function(cookie){
            $.ajax({
                url: url.split("?")[0],
                type: "POST",
                timeout: 30000,
                data: data,
                headers: {
                    "X-XSRFToken": cookie.value
                },
                success: function(data){
                    typeof(data) == "object" && (data = JSON.stringify(data));
                    callback({html: data});
                },
                complete: function(XMLHttpRequest, status){
                    if(status == 'timeout') {
                        StatusLabel.display(label, 1007, true);
                        try_times >= 3 ? callback({html: ""}) :
                            setTimeout(function(){
                                Crawl.get_html(label, url, try_times + 1, callback)
                            }, 5000);
                    }else if(status == 'error'){
                        StatusLabel.display(label, 1002, true);
                        try_times >= 3 ? callback({html: ""}) :
                            setTimeout(function(){
                                Crawl.get_html(label, url, try_times + 1, callback)
                            }, 5000);
                    }else if(status == 'parsererror'){
                        var data = XMLHttpRequest.responseText;
                        callback({html: data});
                    }
                }
            });
        });
    },
    get_json2: function(label, url, try_times, callback){
        StatusLabel.display(label, 2, false, url);
        var params_list = url.split("?")[1].split("&");
        var data = {};
        for(var i=0; i<params_list.length; i++){
            var p = params_list[i].split("=");
            data[p[0]] = p[1];
        }
        $.ajax({
            url: url.split("?")[0],
            type: "POST",
            timeout: 30000,
            data: data,
            success: function(data){
                if(typeof(data) == "object"){
                    data = {ac_shop_url: url, codes: data};
                    data = JSON.stringify(data);
                }
                callback({html: data});
            },
            complete: function(XMLHttpRequest, status){
                if(status == 'timeout') {
                    StatusLabel.display(label, 1007, true);
                    try_times >= 3 ? callback({html: ""}) :
                        setTimeout(function(){
                            Crawl.get_html(label, url, try_times + 1, callback)
                        }, 5000);
                }else if(status == 'error'){
                    StatusLabel.display(label, 1002, true);
                    try_times >= 3 ? callback({html: ""}) :
                        setTimeout(function(){
                            Crawl.get_html(label, url, try_times + 1, callback)
                        }, 5000);
                }else if(status == 'parsererror'){
                    var data = XMLHttpRequest.responseText;
                    callback({html: data});
                }
            }
        });
    },
    post_html: function(label, params, try_times, callback){
        StatusLabel.display(label, 3, false);
        $.ajax({
            url: "http://rouge.actneed.com/crawl/post/",
            type: "POST",
            timeout: 30000,
            data: params,
            dataType: "json",
            success: function(data){
                console.log(data);
                data.complete && StatusLabel.display(label, 5, false);
                callback(data);
            },
            complete: function(XMLHttpRequest, status){
                if(status == 'timeout') {
                    StatusLabel.display(label, 1008, true);
                    try_times >= 3 ? callback({"success": false}) :
                    Crawl.post_html(label, html, try_times + 1, callback)
                }else if(status == 'error'){
                    StatusLabel.display(label, 1003, true);
                    callback({success: false});
                }
            }
        });
    }
};