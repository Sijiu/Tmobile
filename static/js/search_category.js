/**
 * Created by Administrator on 2016/7/21.
 */
(function($){
    $.fn.searchCategory = function(ops){
        var defaults = {
                category_div : "#category-search",
                max_layers : 4,
                select_cate_url : '',
                search_cate_url : '',
                type: "POST",
                data: {"parent_id": 0}
            };
        var options = $.extend(defaults, ops),
            c_level = 0,
            category_group = [],
            category_id  = "",
            category_div = $(options.category_div),
            allSearch = '<div class="form-group search-div">' +
                            '<input type="text" class="form-control" id="all-input-search" value="" placeholder="请输入英文产品关键词,如：mp3">' +
                            '<span class="glyphicon glyphicon-search form-control-feedback"></span>' +
                        '</div>',
            cate_select_wrap = '<div class="cate-select-wrap">'+
                                    '<div id="cate-search-result" class="cate-list" style="display: none;">'+
                                        '<div class="cate-search-panel">'+
                                            '为您匹配到<span id="cate-search-total">0</span>个类目'+
                                            '<a class="cancel-cate-search" href="javascript:;">返回类目</a>'+
                                        '</div>'+
                                        '<ul class="cate-search-ul" class="cate-list-ul"></ul>'+
                                       '<div class="status"><span></span></div>'+
                                    '</div>'+
                                '</div>',
            cate_list_select = '<div class="cate-list-select"></div>',
            cate_lists = "",
            cate_list_first = '<div class="cate-list" >' +
                            '<div class="cate-filter-wrap">' +
                                '<span class="glyphicon glyphicon-search form-control-feedback cate-search"></span>'+
                                '<input class="form-control cate-filter" type="text" placeholder="请输入名称/拼音首字母">' +
                            '</div>' +
                        '</div>',
            cate_list = '<div class="cate-list" style="display: none;">' +
                            '<div class="cate-filter-wrap">' +
                                '<span class="glyphicon glyphicon-search form-control-feedback cate-search"></span>'+
                                '<input class="form-control cate-filter" type="text" placeholder="请输入名称/拼音首字母">' +
                            '</div>' +
                        '</div>',
            selected_cate_banner = '<div class="selected-cate-banner clearfix">' +
                                        '<span class="cate-tip"><strong>您当前选择的类目：</strong></span>' +
                                        '<span class="selected-cate-displayer cate-content"></span>' +
                                   '</div>';
        var data = {
    "categories":
    [{"leaf": 0, "name": "Laptops", "pin": "54>55", "level": 2, "tag": "", "query": "", "id": 817499}, {
        "leaf": 0,
        "name": "Desktops Computers",
        "pin": "54>61",
        "level": 2,
        "tag": "",
        "query": "",
        "id": 817500
    }, {
        "leaf": 0,
        "name": "Computer Accessories",
        "pin": "54>78",
        "level": 2,
        "tag": "",
        "query": "",
        "id": 817501
    }, {"leaf": 1, "name": "Scanners2", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},
        {"leaf": 1, "name": "Scanner3s", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},
        {"leaf": 1, "name": "Scanners4", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},
        {"leaf": 1, "name": "Scanners5", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},
        {"leaf": 1, "name": "Scanners6", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},
        {"leaf": 1, "name": "Scanners7", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},
        {"leaf": 1, "name": "Scanners78", "pin": "54>141", "level": 2, "tag": "", "query": "", "id": 817502},{
        "leaf": 0,
        "name": "Computer Components",
        "pin": "54>107",
        "level": 2,
        "tag": "",
        "query": "",
        "id": 817503
    }, {
        "leaf": 0,
        "name": "Network Components",
        "pin": "54>121",
        "level": 2,
        "tag": "",
        "query": "",
        "id": 817504
    }, {
        "leaf": 0,
        "name": "Printers & Accessories",
        "pin": "54>131",
        "level": 2,
        "tag": "",
        "query": "",
        "id": 817505
    }, {"leaf": 0, "name": "Software", "pin": "54>142", "level": 2, "tag": "", "query": "", "id": 817506}, {
        "leaf": 0,
        "name": "Storage",
        "pin": "54>6220",
        "level": 2,
        "tag": "",
        "query": "",
        "id": 817507
    }]
};
        var CategoryObj = {
            init: function(){
                CategoryObj.build_category_area();
            },
            build_category_area: function(){

            },
            select_cate_sub: function(data, level){
                $.ajax({
                    "url": options.select_cate_url,
                    "type":  options.type,
                    "dataType": "json",
                    "data": data,
                    "success": function(data){
                        if(data.status || data.categories){
                            CategoryObj.render_category(data.categories, level);
                            category_div.find("li a").click(CategoryObj.choose_category);
                            CategoryObj.search_key_up();
                        }else{
                            //Inform.disable();
                            //Inform.show(data.message);
                        }
                    },
                    "error": function(){

                    }
                })
            },
            render_category:function(cate, level){
                var cate_ul ="", cate_li = "";
                for(var i=0; i< cate.length; i++){
                    var leaf = cate[i].leaf ? "": "has-leaf";
                    var cate_a = $("<a>",{"class":leaf, "data-id": cate[i].id, "data-isleaf": cate[i].leaf, "data-filterindex":
                                    cate[i].filterindex, "data-level": cate[i].level, "data-cn": "", "data-en": cate[i].name, "title": cate[i].name,
                                    "data-cn": cate[i].cn}).text(cate[i].name);
                        cate_li += '<li>'+cate_a.prop("outerHTML")+'</li>';
                }
                cate_ul = '<ul class="">'+ cate_li +'</ul>';
                if (level >0) category_div.find(".cate-list-select").find(".cate-list").eq(level).css("display","");
                category_div.find(".cate-list-select").find(".cate-list").eq(level).append(cate_ul);
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
                    category_uid = cate.attr("data-id");
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
                        console.log(level);
                        category_div.find(".cate-list-select").find(".cate-list:gt("+(level-1)+")").hide().find("ul").remove();
                        category_div.find(".cate-list-select").find(".cate-list:gt("+(level-1)+")").find(".cate-filter").val("");
                        if(cate.data("isleaf")){

                        }else{
                            CategoryObj.select_cate_sub(options.data, level);
                        }
                    }
                }
            },
            all_search: function(){
                var search_text = category_div.find(".all-input-search").val();
                $("#cate-search-result").show();
                CategoryObj.clear_cate_displayer();
                category_div.find(".cate-list-select").hide();
                $.ajax({
                    "url": options.select_cate_url,
                    "type": options.type,
                    "dataType": "json",
                    "data": data,
                    "success": function(data){
                    }
                })
            },
            init_search_panel: function(){
                CategoryObj.clear_cate_displayer();
                $("#cate-search-result").hide();
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
                    for (var j=0;j<str_len;j++){
                        if(/[\u4e00-\u9fa5A-Za-z]/.test(search_str_A[j])){
                            if(/[\u4e00-\u9fa5]/.test(search_str_A[j])){
                                en_cn = "cn";
                                break
                            }
                        }
                    }
                    if(str_len){
                        this_list.find("a").each(function(n,ob){
                            var obj = $(ob);
                            var sear_tag =obj.attr("data-"+en_cn).toUpperCase();
                            var index = sear_tag.indexOf(search_str_A);
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
            category_div.find(".cate-list-select").append(cate_list_first + cate_lists);
            //CategoryObj.render_category(data.categories)
            CategoryObj.select_cate_sub(options.data, 0);
            category_div.find("#all-input-search").keyup(CategoryObj.all_search);
            category_div.find(".cancel-cate-search").click(CategoryObj.init_search_panel);
            CategoryObj.init();
        });
        var returnObj = {
            get_category_name: function(){
                return category_group;
            },
            get_category_id: function(){
                return category_group;
            }
        };
        return returnObj;
    }
})(jQuery);
