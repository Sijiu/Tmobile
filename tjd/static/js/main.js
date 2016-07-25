/**
 * Created by xuhe on 15/12/3.
 */


$(document).ready(function(){
    var version = 1.1,
        status = false,
        cover = $("#cover"),
        inform = $("#inform"),
        current_feed = {},
        current_user = "",
        terminal = false,
        label = $(".status-label"),
        crawl_btn = $("#crawl-btn"),
        counter = {
            success: $("#success-stat"),
            error: $("#error-stat"),
            total: $("#total-stat")
        };
    $("#start-url").attr({
        placeholder: "输入您要采集的单品、分组或店铺链接，支持Wish, eBay, 速卖通, Amazon, Etsy, 1688, 淘宝, 天猫, 京东等平台"
    });
    function init_crawl_btn(){
        console.log("初始化采集按钮");
        var feed_area = $("#start-url");
        start_auth(feed_area.val(), function(result){
            StatusLabel.display(label, result ? 2 : 1001, !result);
            if(result){
                result.other = JSON.stringify(result.other);
                feed_area.attr("disabled", true);
                start_crawl(result);
            }
        });
    }
    function crawl_item(feed){
        if(!status){return StatusLabel.display(label, 4, false)}
        if(terminal){return terminal_crawl(0)}
        Crawl.get_html(label, feed.url, 0, function(data){
            feed.html = data.html; feed.mobile = current_user;
            Crawl.post_html(label, feed, 0, function(data2){
                data2.success ? data2.complete ? complete_crawl(data2):
                continue_crawl(data2) : handle_crawl_exception(data2)
            });
        });
    }
    function continue_crawl(data){
        counter["success"].text(data["snu"]);
        counter["error"].text(data["enu"]);
        counter["total"].text(data["snu"] + data["enu"]);
        crawl_item(current_feed = data["feed"]);
    }
    function complete_crawl(data){
        counter["success"].text(data["snu"]);
        counter["error"].text(data["enu"]);
        counter["total"].text(data["snu"] + data["enu"]);
        current_feed = {};
        $("#terminal").unbind();
        $("#start-url").val("").attr("disabled", false);
        set_status(false);
        crawl_btn.unbind().click(init_crawl_btn);
    }
    function handle_crawl_exception(data){
        Exception.handle(inform, data.exception, data.params);
        set_status(false);
    }
    function set_terminal(){
        Exception.handle(inform, 10001);
    }
    function terminal_crawl(tt){
        var self = $(this);
        Exception.handle(inform, 10000);
        $.ajax({
            url: "http://rouge.actneed.com/crawl/terminal/",
            type: "POST",
            dataType: "json",
            data: {mobile: current_user},
            timeout: 30000,
            success: function(data){
                if(data.success){
                    self.unbind();
                    $("#start-url").val("").attr("disabled", false);
                    set_status(false);
                    crawl_btn.unbind().click(init_crawl_btn);
                    current_feed = {};
                    StatusLabel.display(label, 6, false);
                    Exception.clear(inform);
                }else{
                    StatusLabel.display(label, 1003, true);
                    Exception.handle(data.exception, data.params);
                }
            },
            complete: function(XMLHttpRequest, status){
                if(status == 'timeout') {
                    tt < 3 ? terminal_crawl(tt+1) : StatusLabel.display(label, 1008, true);
                }else if(status == 'error'){
                    alert("服务器报错！请联系管理员")
                }
            }
        });
    }
    function stop_crawl(){
        set_status(false);
        console.log("has stopped");
    }
    function start_crawl(feed){
        set_status(true);
        terminal = false;
        $("#terminal").click(function(){
            status ?  set_terminal() : terminal_crawl(0);
        });
        crawl_item(feed.url ? feed : current_feed);
    }
    function set_status(stat) {
        var self = crawl_btn;
        if (status == stat) {
            return console.log("禁止改变状态");
        }
        if (!status) {
            self.addClass("disable").text("正在开始...");
            status = stat;
            crawl_btn.unbind().click(stop_crawl);
            setTimeout(function () {
                self.attr("class", "crawl-btn btn orange").text("暂停采集");
            }, 200);
            return console.log("当前状态：采集开始")
        } else {
            self.addClass("disable").text("正在停止...");
            status = stat;
            crawl_btn.unbind().click(start_crawl);
            setTimeout(function () {
                self.attr("class", "crawl-btn btn green").text("继续采集");
            }, 200);
            return console.log("当前状态：采集暂停")
       }
    }
    function check_version(){
        $.ajax({
            url: "http://rouge.actneed.com/crawl/version/",
            type: "POST",
            data: {version: version, mobile: current_user},
            dataType: "json",
            success: function(data) {
                if(!data.latest){
                    $("#latest-version").text(data.version);
                    $(".version").animate({height: "40px"}, 200);
                    $(".close-x").click(function(){
                        $(".version").animate({height: 0}, 200);
                    });
                }
            }
        });
    }
    function start_auth(start_url, callback){
        StatusLabel.display(label, 1, false);
        $.ajax({
            url: "http://rouge.actneed.com/crawl/validate/",
            type: "POST",
            data: {start_url: start_url, mobile: current_user},
            dataType: "json",
            success: function(data) {
                callback(data.success ? data.json : false);
            },
            complete: function(XMLHttpRequest, status){
                if(status == 'timeout') {
                    StatusLabel.display(label, 1008, false);
                }else if(status == 'error'){
                    StatusLabel.display(label, 1003, false);
                }
            }
        });
    }
    function init_status(t, tt){
        chrome.cookies.get({url: 'https://www.actneed.com', name: 'msid'}, function(cookie){
            if(!cookie){
                cover.find("#loading").css({"display": "none"});
                cover.find("#login").css({"display": "block"});
                return setTimeout(function(){init_status(t+1, tt)}, t <= 100 ? 1000: 100000);
            }
            chrome.cookies.set({
                url: 'http://rouge.actneed.com',
                name: 'msid',
                value: cookie.value
            });
            $.ajax({
                url: "http://rouge.actneed.com/crawl/init/",
                type: "GET",
                dataType: "json",
                timeout: 30000,
                success: function(data){
                    if(data.success){
                        current_user = data["mobile"];
                        $(".personal").text(current_user);
                        cover.css("opacity", 0);
                        if(data.status){
                            current_feed = data["feed"];
                            start_crawl(current_feed);
                            $("#start-url").attr("disabled", true).val(data["start_url"]);
                        }else{
                            crawl_btn.click(init_crawl_btn);
                        }
                        setTimeout(function(){
                            cover.css({"display": "none"});
                        }, 1000);
                        check_version();
                        counter["success"].text(data["snu"]);
                        counter["error"].text(data["enu"]);
                        counter["total"].text(data["snu"] + data["enu"]);
                    }else{
                        cover.find("#loading").css({"display": "none"});
                        cover.find("#login").css({"display": "block"});
                        setTimeout(function(){init_status(t+1, tt)}, t <= 100 ? 1000: 100000);
                    }
                },
                complete: function(XMLHttpRequest, status){
                    if(status == 'timeout') {
                        tt < 3 ? init_status(t, tt+1) : alert("请求服务器超时，请检查网络连接");
                    }else if(status == 'error'){
                        alert("服务器报错！请联系管理员");
                    }
                }
            });
        });
    }
    init_status(0, 0);
});