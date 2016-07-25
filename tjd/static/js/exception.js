/**
 * Created by xuhe on 15/12/3.
 */

var Exception = {
    us: _,
    1000: function(){
        location.reload();
    },
    1005: function(message, params){
        var exception = {
            msg: message,
            op: "前往登录",
            url: params.url
        };
        return '<div class="modal"><div class="modal-center">'
             + '<div class="modal-header">抓取报错</div>'
             + '<div class="modal-text">' + exception.msg + '</div>'
             + '<div class="modal-op"><a class="btn red" href="'
             + exception.url + '" target="_blank">'
             + exception.op +'</a></div></div></div>'
    },
    10000: function(message, params){
        console.log(params);
        return '<div class="modal"><div class="modal-center">'
             + '<div class="modal-header">系统提示</div>'
             + '<div class="modal-load"></div>'
             + '<div class="modal-text">' + message + '</div>'
             + '</div></div>';
    },
    10001: function(message, params){
        console.log(params);
        return '<div class="modal"><div class="modal-center">'
            + '<div class="modal-header">系统提示</div>'
            + '<div class="modal-text">' + message + '</div>'
            + '<div class="modal-op"><a class="btn small blue" href="#" '
            + 'id="close-me">关闭</a></div></div></div>'
    },
    handle: function(cover, exc_code, params){
        console.log("执行exception handler");
        var content = Exception[exc_code](StatusLabel[exc_code], params);
        cover.html(content);
        exc_code == 10001 && $("#close-me").click(function(){$("#inform").html("")});
    },
    clear: function(cover){
        cover.html("");
    }
};