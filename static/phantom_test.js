/**
 * Created by Administrator on 2016/5/20.
 */

var page = require('webpage').create();
page.onResourseRequested = function(request){
    console.log('Request ==' + JSON.stringify(request, undefined, 4));
};
page.onResourseReceived = function(response){
    console.log('Receive ==' + JSON.stringify(response, undefined, 4));
};
//page.open('http://blog.csdn.net/monsion/article/details/7981366', function (status) {
//    console.log("Status: " + status);
//    if (status === "success") {
//        page.render('asd.png');
//        console.log("Status: " + status);
//    }
//    phantom.exit();
//});
page.open('http://blog.csdn.net/monsion/article/details/7981366');
page.onResourseReceived();
page.onResourseRequested();

