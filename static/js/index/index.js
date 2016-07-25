/**
 * Created by Plain on 2016/7/22.
 */
$(function(){
    var a = 0;
    var Index = {
        init: function(){
            console.log("a");
            $("#first-category").searchCategory({
                category_div: "#first-category"
            })
        }
    };
    Index.init();
});
