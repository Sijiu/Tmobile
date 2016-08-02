/**
 * Created by Administrator on 2016/7/21.
 */
(function($){
    $.fn.searchCategory = function(ops){
        var defaults = {
                category_div : "#category-search",
                max_layers : 7,
                select_cate_url : '',
                select_type: "POST",
                search_cate_url : '',
                search_type: "POST",
                data: {"parent_id": 0}
            };
        var options = $.extend(defaults, ops),
            c_level = 0,
            category_group = [],
            category_name = [],
            category_id  = "",
            category_div = $(options.category_div),
            allSearch = '<div class="plug-search-div">' +
                            '<input type="text" class="plug-search-input all-input-search" value="" placeholder="请输入英文产品关键词,如：mp3">' +
                            '<span class="glyphicon glyphicon-search search-icon"></span>' +
                        '</div>',
            cate_select_wrap = '<div class="cate-select-wrap">'+
                                    '<div class="cate-search-result cate-list" style="display: none;">'+
                                        '<div class="cate-search-panel">'+
                                            '为您匹配到<span class="cate-search-total">0</span>个类目'+
                                            '<a class="cancel-cate-search" href="javascript:;">返回类目</a>'+
                                        '</div>'+
                                        '<ul class="cate-search-ul cate-list-ul">'+
                                        '</ul>'+
                                       '<div class="status"><span></span></div>'+
                                    '</div>'+
                                '</div>',
            cate_list_select = '<div class="cate-list-select"></div>',
            cate_lists = '',
            last_null_div = '<div class="last-null-div" ></div>',
            cate_list_first = '<div class="cate-list" >' +
                            '<div class="cate-filter-wrap">' +
                                '<span class="glyphicon glyphicon-search search-icon cate-search"></span>'+
                                '<input class="plug-search-input cate-filter" type="text" placeholder="请输入名称/拼音首字母">' +
                            '</div>' +
                        '</div>',
            cate_list = '<div class="cate-list" style="display: none;">' +
                            '<div class="cate-filter-wrap">' +
                                '<span class="glyphicon glyphicon-search search-icon cate-search"></span>'+
                                '<input class="plug-search-input cate-filter" type="text" placeholder="请输入名称/拼音首字母">' +
                            '</div>' +
                        '</div>',
            selected_cate_banner = '<div class="selected-cate-banner clearfix">' +
                                        '<span class="cate-tip"><strong>您当前选择的类目：</strong></span>' +
                                        '<span class="selected-cate-displayer cate-content"></span>' +
                                   '</div>';

//        var data ={
//    "categories":
//    [{
//        "leaf": 0,
//        "name": "\u670d\u88c5/\u670d\u9970\u914d\u4ef6",
//        "pin": "3",
//        "py": "fz/fzpj",
//        "level": 1,
//        "tag": "",
//        "query": "",
//        "id": 724328
//    }, {
//        "leaf": 0,
//        "name": "\u6c7d\u8f66\u3001\u6469\u6258\u8f66",
//        "pin": "34",
//        "py": "qc、mtc",
//        "level": 1,
//        "tag": "",
//        "query": "",
//        "id": 724572
//    }, {
//        "leaf": 0,
//        "name": "\u7f8e\u5bb9\u5065\u5eb7",
//        "pin": "66",
//        "py": "mrjk",
//        "level": 1,
//        "tag": "",
//        "query": "",
//        "id": 725005
//    }, {
//        "leaf": 0,
//        "name": "\u7535\u8111\u548c\u529e\u516c",
//        "pin": "7",
//        "py": "dnbg",
//        "level": 1,
//        "tag": "",
//        "query": "",
//        "id": 725279
//    }, {"leaf": 0, "name": "\u5efa\u7b51", "pin": "13", "py": "jz", "level": 1, "tag": "", "query": "", "id": 725526}, {
//        "leaf": 0,
//        "py": "xfdz",
//        "name": "\u6d88\u8d39\u7535\u5b50",
//        "pin": "44",
//        "level": 1,
//        "tag": "",
//        "query": "",
//        "id": 725773
//    }]
//};
        var CategoryObj = {
            init: function(){

            },
            select_cate_sub: function(data, level){
                $.ajax({
                    "url": options.select_cate_url,
                    "type":  options.select_type,
                    "dataType": "json",
                    "data": data,
                    "success": function(data){
                        if(data.status || data.categories){
                            CategoryObj.render_category(data.categories, level);
                            category_div.find("li a").click(CategoryObj.choose_category);
                            var cate_select_wrap = category_div.find(".cate-select-wrap");
                                cate_select_wrap.animate({scrollLeft:1000},900);

                            CategoryObj.search_key_up();
                        }else{
                           console.log(data.message);
                        }
                    },
                    "error": function(){
                        console.log("请求失败.");
                    }
                })
            },
            render_category:function(cate, level){
                var cate_ul ="", cate_li = "";
                for(var i=0; i< cate.length; i++){
                    var leaf = cate[i].leaf ? "": "plug-has-leaf",
                        spell = cate[i].py ? cate[i].py: cate[i].name;
                    var cate_a = $("<a>",{"class":leaf, "data-id": cate[i].id, "data-isleaf": cate[i].leaf, "data-py":spell,
                                    "data-level": cate[i].level, "data-en": cate[i].name, "title": cate[i].name,
                                    "data-cn": cate[i].cn}).text(cate[i].name);
                        cate_li += '<li>'+cate_a.prop("outerHTML")+'</li>';
                }
                cate_ul = '<ul class="cate-list-ul">'+ cate_li +'</ul>';
                if (level >0)category_div.find(".cate-list-select").find(".cate-list").eq(level).show();
                category_div.find(".cate-list-select").find(".cate-list").eq(level).append(cate_ul);
                //CategoryObj.search_key_up();
            },
            choose_category:function(){
                var cate = $(this);
                var is_leaf = cate.attr("data-leaf") == "1";
                var level = cate.attr("data-level");
                var name = cate.text();
                var html_str = "";
                var pop_times, temp_level;
                level = parseInt(level);
                if(is_leaf){
                    if(c_level < level){
                        category_group.push(name);
                    }else{
                        pop_times = c_level - level + 1;
                        temp_level = level;
                        while(pop_times > 0){
                            category_group.pop();
                            temp_level += 1;
                            $(".category[data-level=" + temp_level + "]").remove();
                            pop_times -= 1;
                        }
                        category_group.push(name);
                    }
                    c_level = level;
                    cate.closest("ul").find("a").removeClass("selected");
                    cate.addClass("selected");
                    category_div.find(".selected-cate-displayer").text(category_group.join(" > "));
                }else{
                    if(!cate.hasClass("selected")){
                        if(c_level < level){
                            category_group.push(name);
                        }else{
                            pop_times = c_level - level + 1;
                            temp_level = level;
                            while(pop_times > 0){
                                category_group.pop();
                                temp_level += 1;
                                $(".category[data-level=" + temp_level + "]").remove();
                                pop_times -= 1;
                            }
                            category_group.push(name);
                        }
                        c_level = level;
                        var category_dom = $("<ul/>").attr({ "class": "category loading-cate", "data-level": level + 1
                                                            }).appendTo(".category-area");
                        cate.closest("ul").find("a").removeClass("selected");
                        cate.addClass("selected");
                        options.data.parent_id = cate.attr("data-id");
                        category_div.find(".selected-cate-displayer").text(category_group.join(" > "));
                        console.log("level=="+level);
                        category_div.find(".cate-list-select").find(".cate-list:gt("+(level-1)+")").find(".cate-filter").val("");
                        if(cate.data("isleaf")){
                            category_name = category_group;
                            category_id = cate.data("id");
                            category_div.find(".cate-list-select").find(".cate-list:gt("+(level-1)+")").hide().find("ul").remove();
                        }else{
                            category_name = category_group;
                            category_id = cate.data("id");
                            CategoryObj.select_cate_sub(options.data, level);
                            category_div.find(".cate-list-select").find(".cate-list:gt("+(level)+")").hide();
                            category_div.find(".cate-list-select").find(".cate-list:gt("+(level-1)+")").find("ul").remove();
                        }
                    }
                }
            },
            all_search: function(){
                if (event.keyCode == 13) {
                    var search_text = category_div.find(".all-input-search").val();
                    if ($.trim(search_text)) {
                        category_div.find(".cate-search-result").show();
                        CategoryObj.clear_cate_displayer();
                        category_div.find(".cate-list-select").hide();
                        options.data["name"] = $.trim(search_text);
                        var search_ul = category_div.find(".cate-search-ul"),
                            load_img = '<li class="like-a"><img src="/static/image/spinner.gif" style="width:32px;height:32px;" align="center"></li>',
                            cate_search_total = category_div.find(".cate-search-total");
                        cate_search_total.text(0);
                        search_ul.html(load_img);
                        $.ajax({
                            "url": options.search_cate_url,
                            "type": options.search_type,
                            "dataType": "json",
                            "data": options.data,
                            "success": function (data) {
                                if (data.status) {
                                    var search_li = '',
                                        search_result = data.json.categories,
                                        search_total = search_result.length;
                                    for (var i = 0; i < search_total; i++) {
                                        search_li += '<li><a data-id=' + search_result[i].id + ' data-level="1" title="' + search_result[i].full_name
                                            + '">' + search_result[i].full_name + '</a></li>';
                                    }
                                    cate_search_total.text(search_total);
                                    search_ul.html(search_li);
                                    search_ul.find("li a").click(CategoryObj.choose_category);
                                } else {
                                    var error_li = '<li class="like-a">' + data.message + '</li>';
                                    search_ul.html(error_li);
                                }
                            }
                        })
                    }
                }
            },
            init_search_panel: function(){
                CategoryObj.clear_cate_displayer();
                category_div.find(".cate-search-result").hide();
                category_div.find(".cate-list-select").show();
            },
            clear_html: function(obj){
                obj.find("a").each(function(n,o){
                    o.innerHTML = o.text;
                })
            },
            search_key_up: function(){
                $(".cate-filter").keyup(function(){
                    var _this = $(this);
                    _this.closest(".cate-list").find("li").show();
                    var this_list = _this.closest(".cate-list").find("ul");
                    CategoryObj.clear_html(this_list);
                    var en_cn = "en";
                    var search_str_A = $.trim(_this.val()).toUpperCase();
                    var str_len = search_str_A.length;
                    if(str_len){
                        this_list.find("a").each(function(n,ob){
                            var obj = $(ob),
                                sear_tag =obj.attr("title").toUpperCase(),
                                index = sear_tag.indexOf(search_str_A);
                            if(index<0 && obj.attr("title") !== obj.attr("data-py")){
                                sear_tag =obj.attr("data-py").toUpperCase();
                                index = sear_tag.indexOf(search_str_A);
                            }
                            if (index == -1){
                                obj.closest("li").hide();
                            }else{
                                var start_html = obj.text();
                                var replace_str = start_html.substring(index,index+str_len);
                                var tar_html = start_html.replace(replace_str,"<span style='color:red'>"+replace_str+"</span>");
                                obj.html(tar_html);
                            }
                        })
                    }
                })
            },
            clear_cate_displayer: function(){
                category_div.find(".selected-cate-displayer").text("");
            }
        };
        this.each(function(){
            for(var i=0; i<options.max_layers-1; i++) cate_lists += cate_list;
            category_div.append(allSearch + cate_select_wrap + selected_cate_banner);
            category_div.find(".cate-select-wrap").append(cate_list_select);
            category_div.find(".cate-list-select").append(cate_list_first + cate_lists + last_null_div);
            //CategoryObj.render_category(data.categories, 0);
            CategoryObj.select_cate_sub(options.data, 0);
            category_div.find(".all-input-search").keyup(CategoryObj.all_search);
            category_div.find(".cancel-cate-search").click(CategoryObj.init_search_panel);
            CategoryObj.init();
        });
    }
})(jQuery);