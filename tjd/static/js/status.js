/**
 * Created by xuhe on 15/12/3.
 */

var StatusLabel = {
    1: "正在验证采集链接...",
    2: "正在采集的商品连接为",
    3: "传送数据至ActNeed服务器并解析...",
    4: "当前采集任务被暂停",
    5: "本次采集已完成",
    6: "当前采集任务被终止",
    1000: "用户未登录",
    1001: "采集链接输入不正确，请重新输入",
    1002: "商品信息获取失败，请稍候重试",
    1003: "服务器内部错误，请联系管理员",
    1004: "申请ActNeed授权失败，原因是采集量已达上限，请充值继续使用",
    1005: "采集被限制，被采集平台需要您进行用户身份验证，请前往登录",
    1006: "用户不一致，您可能在当前浏览器使用了新的ActNeed帐号登录",
    1007: "获取商品信息超时，请查看网络设置，若网络无问题，请刷新重试或联系管理员",
    1008: "请求服务器超时，请查看网络设置，若网络无问题，请刷新重试或联系管理员",
    10000: "处理中，请稍候...",
    10001: "请暂停当前任务再终止",
    display: function(jdom, status_code, exc, params){
        console.log(status_code);
        exc == undefined && (exc = true);
        console.log(StatusLabel[status_code]);
        var label = params ? StatusLabel[status_code] + params: StatusLabel[status_code];
        jdom.css("color", exc ? "#eb3c00" : "#399").text(label);
    }
};
