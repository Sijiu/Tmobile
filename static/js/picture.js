    /**
 * Created by GF on 2015/12/11.
 */
$(function(){
    var $node_name = "";
    var used_space = 0;
    var btn_status, condition_info=[];
    var is_close_status = true;
    function is_default(treeId, treeNode){
        return treeNode.id!= "no-group" && treeId!="search-tree" && treeId!="move-tree"
    }
    function zTreeOnMouseUp() {
        $("#photoBankGroupList").find(".groupTitle").removeClass("activeGroup");
    }
    function zTreeOnClick(event, treeId, treeNode) {
        btn_status = "group";
        var treeObj = $.fn.zTree.getZTreeObj("tree");
//        console.log(treeObj.transformToArray(treeObj.getNodes()));
        var t_id = treeNode["tId"];
        if(treeId=="tree"){
            $("#photoBankGroupList").find(".groupTitle").removeClass("activeGroup");
            var page_n = $(".footer-stat").find("button").attr("data-name") || 50;
            Picture.show_pic_ajax(t_id,page_n,1);
            if(Picture.getCookie("group")!=t_id){
                location.href = location.href.split("#")[0] + "#1";
            }
            document.cookie = "page_n="+page_n;
            document.cookie = "group="+t_id;
            Picture.clean_all_check();
            Picture.local_upload();
        }else if(treeId=="move-tree"){
            if(!Picture.detect_count()){
                return 0
            }
            var pic_id = Picture.get_pic_id();
            var new_id = "tree_"+t_id.split("_")[1];
            $.ajax({
                url: "/picture/group/move",
                type: "POST",
                data: {
                    "pic_id": JSON.stringify(pic_id),
                    "new_id": new_id
                },
                dataType: "JSON",
                success:function(data){
                    if(data.status==1){
                        var treeObj = $.fn.zTree.getZTreeObj("tree");
                        var node = treeObj.getNodeByTId(new_id);
                        treeObj.selectNode(node);
                        var pictures = data["pictures"],
                            col_map = data["col_map"],
                            page_total = data["page_total"],
                            page_n = data["page_n"],
                            pages = data["pages"],
                            c_page = data["c_page"];
                        Picture.render_pic(pictures,col_map,page_total,page_n,pages,c_page);
                    }else{
                        Inform.enable();
                        Inform.show("移动失败");
                    }
                    Picture.clean_all_check();
                }
            })
        }else if(treeId=="search-tree"){
            $(".search-key").text(treeNode["name"]).attr("data-id",t_id);
        }
    }
    function zTreeOnRemove(event, treeId, treeNode) {
        var group_value = [treeNode.parentTId+";"+treeNode.tId+";"+treeNode.name],
            children_node = treeNode.children;
        var group_id = [treeNode.tId];
        if(children_node){
            for(var i=0;i<children_node.length;i++){
                group_id.push(children_node[i].tId);
                group_value.push(children_node[i].parentTId+";"+children_node[i].tId+";"+children_node[i].name)
            }
        }
        $.ajax({
            url: "/picture/group/del",
            type: "POST",
            data: {
                group_id: JSON.stringify(group_id),
                group_value: JSON.stringify(group_value)
            },
            dataType: "JSON",
            success: function(data){
                data.status == 1 || alert("请求失败");
            }
        })
    }
    function zTreeBeforeRename(event, treeNode, newName, isCancel) {
        $node_name = treeNode.name;
        return newName!=""
    }
    function zTreeOnRename(event, treeId, treeNode, isCancel){
        var group_value = treeNode.parentTId+";"+treeNode.tId+";"+$node_name,
            new_value = treeNode.parentTId+";"+treeNode.tId+";"+treeNode.name;
        $.ajax({
            url: "/picture/group/rename",
            type: "POST",
            data: {
                group_value: group_value,
                new_value: new_value
            },
            success: function(data){
                data.status == 1 || alert("请求失败");
            }
        })
    }
//    function addHoverDom(treeId, treeNode) {
//        var sObj = $("#" + treeNode.tId + "_span");
//        if (treeNode.editNameFlag || $("#addBtn_"+treeNode.tId).length>0) return;
//        var editStr = "<span class='button add' id='addBtn_" + treeNode.tId
//				+ "' title='新建分组' onfocus='this.blur();'></span>";
//        if(treeNode.tId!="tree_1"&&treeNode.level!=1) sObj.append(editStr);
//        var btn = $("#diyBtn_"+treeNode.id);
//        if (btn) btn.bind("click", function(){
//
//        });
//    }
//    function removeHoverDom(treeId, treeNode) {
//        $("#addBtn_"+treeNode.tId).unbind().remove();
//    }
    var zTreeObj, zTreeObj_s,
        setting = {
            view: {
                selectedMulti: false,
//                addHoverDom: addHoverDom,
//		        removeHoverDom: removeHoverDom,
                fontCss : {fontSize:"16px"}
            },
            edit:{
                enable: true,
                showRenameBtn: is_default,
		        renameTitle: "重命名",
                showRemoveBtn: is_default,
                removeTitle: "删除分组"
            },
            drag:{
                isMove: false,
                isCopy: false
            },
            callback:{
                onMouseUp: zTreeOnMouseUp,
                onClick: zTreeOnClick,
                onRemove: zTreeOnRemove,
                beforeRename: zTreeBeforeRename,
                onRename: zTreeOnRename
            },
            data:{
                simpleData: {
                    enable: true,
                    idKey: "id",
                    pIdKey: "pId",
                    rootPId: null
                }
            }
        },
        zTreeNodes = [{"name":"未分组图片", open:false, isParent:false, "id":"no-group"}];
    if(pic_group.length!=0){
        for(var i=0;i<pic_group.length;i++){
            var $nodes = pic_group[i].split(";");
            zTreeNodes.push({id:$nodes[1],pId:$nodes[0],name:$nodes[2]});
        }
//        console.log(zTreeNodes)
    }


    var Picture = {
        init:function(){
            Inform.init();
//            console.log(pic_group)
            // 初始化树插件
            zTreeObj = $.fn.zTree.init($("#tree"), setting, zTreeNodes);
            //// 初始化上传插件
            //$("#upload-input").fileinput();
            //// 初始化切图插件
            //$('.container > img').cropper({
            //      aspectRatio: 16 / 9,
            //      crop: function(data) {
            //        // Output the result data for cropping image.
            //      }
            //    });

            // 初始化日历插件
            $("#end-time").datetimepicker(
                {
                    format: 'YYYY-MM-DD',
                    defaultDate:{
                        Default: true
                    }
                }
            );
            $("#start-time").datetimepicker(
                {
                    format: 'YYYY-MM-DD',
                    defaultDate:{
                        Default: true
                    }
                }
            );
            $("#photoList").on("mouseenter",".picture",function(){
                $(this).find(".operate-btns").show();
            }).on("mouseleave",".picture",function(){
                var $this = $(this);
                //$this.find("input").prop("checked") ||
                $this.find(".operate-btns").hide();
            }).on("click",".picture",function(){
                $(this).find("input[type=checkbox]").trigger("click");
            }).on("click",".photo-checkbox",Picture.check_pic).on("click",".pic-delete",Picture.del_pic)
                .on("click", ".pic-edit",Picture.edit_pic).on("click", ".copy_link",Picture.copy_link);
            $("#all-pick").change(Picture.check_all_pic);
            $("#del-multi-pic").click(Picture.del_multi_pic);
            $("#new-group").click(Picture.add_group_node);
            $("#search-option").click(Picture.dropdown_render);
            $("#move-select").click(Picture.dropdown_render);
            $("#btnShowAllGroup").click(Picture.check_all_group);
            $(".groupTitle").on("click",Picture.group_active).on("click",Picture.show_group_pic);
            $("#search-pic").click(Picture.search_pic);
//            $("#btnShowAllGroup").trigger("click");
            $("#pic-filter").click(Picture.filter_pic);
            $("#photoArea").on("click",".goto-page",Picture.goto_page)
                .on("click",".pic-every-page",Picture.goto_page);
            $(window).scroll(Picture.scroll_listener);
            $(".to-top").click(function(e){
                e.preventDefault();
                $("body,html").animate({scrollTop:0},300);
            });
            $("#search-in-all").click(function(){
                $(".search-key").text("所有分组").attr("data-id","all_group");
            });
            $("#add-watermark").click(Picture.show_mark_modal);
            $(".ex-block").click(function(){
                $(this).addClass("on").siblings(".ex-block").removeClass("on");
            });
            $("#add-mark-btn").click(Picture.add_mark);
            Picture.check_used_space(1000);
            $("#upload-net-btn").click(function(){
                var picture_urls = [];
                var $this = $(this);
                $this.button("loading");
                $("#upload-net").modal("hide").find(".url").each(function(k, v){
                    var picture_url = $(v).val();
                    if(picture_url && picture_url != ""){
                        picture_urls.push(picture_url);
                        $(v).val("");
                    }
                });
                Inform.disable();
                Inform.show("", true, "正在抓取图片...");
                var treeObj = $.fn.zTree.getZTreeObj("tree");
                var nodes = treeObj.getSelectedNodes();
                var group_id = nodes.length==0 ? "tree_1" : nodes[0].tId;
                $.ajax({
                    url: "/picture/upload/net",
                    type: "POST",
                    data: {
                        group_id: group_id,
                        picture_urls: JSON.stringify(picture_urls)
                    },
                    dataType: "json",
                    success: function(data){
                        $this.button("reset");
                        if(data.status == 1){
                            Inform.enable();
                            Inform.show(data.message);
                            if(group_id=="tree_1"){
                                var treeObj = $.fn.zTree.getZTreeObj("tree");
                                var node = treeObj.getNodeByTId("tree_1");
                                treeObj.selectNode(node);
                                $(".groupTitle").removeClass("activeGroup")
                            }
                            var pictures = data["pictures"],
                                col_map = data["col_map"],
                                page_total = data["page_total"],
                                page_n = data["page_n"],
                                pages = data["pages"],
                                c_page = data["c_page"];
                            Picture.render_pic(pictures,col_map,page_total,page_n,pages,c_page);
                        }else{
                            Inform.show("操作失败");
                        }

                    },
                    error: function(){
                        Inform.enable();
                        Inform.show("操作失败");
                    }

                });
            });
            var local_up = $("#upload").Huploadify({
                auto: false,
                fileTypeExts: '*.jpg;*.png;*.gif',
                multi: true,
                fileObjName: 'Filedata',
                fileSizeLimit: 9999,
                formData:{group_id: "tree_1"},
                showUploadedPercent: false,
                showUploadedSize: false,
                removeTimeout: 500,
                buttonClass: 'btn btn-primary',
                uploader: '/picture/upload/local',
                onUploadStart:function(){
                    $(".uploadify-button").prop("disabled",true);
                },
                onInit:function(){
                    console.log('初始化');
                },
                onUploadSuccess:function(data){
                    var data_treeObj = $.fn.zTree.getZTreeObj("tree");
                    var data_node = data_treeObj.getNodeByTId("tree_1");
                    data_treeObj.selectNode(data_node);
                    var cur_node = $(".curSelectedNode");
                    if(cur_node.length!=0){
                        cur_node.trigger('click');
                    }else{
                        $("#tree_1_a").trigger('click');
                    }
                },
                onDelete:function(file){
                    console.log('删除的文件：'+file);
                    console.log(file);
                },
                onSelect: function(){
                    $("#ensure-up").prop("disabled",false);
                },
                onUploadComplete: function(){
                    $("#ensure-up").prop("disabled",true);
                }
            });
            $("#ensure-up").click(function(){
                local_up.upload('*');
                local_up.destroy();
            });

            // 刷新
            if(location.hash!=""){
                var i_page_n = Picture.getCookie("page_n") || 50,
                i_c_page = parseInt(location.hash.split("#")[1]),
                i_group_id = Picture.getCookie("group") || "all_group";
                if(i_group_id=="all_group"){
                    $("#btnShowAllGroup").trigger("click");
                }else if(i_group_id=="tree_0"){
                    $("#recycleBox").trigger("click");
                }else{
                    $("#"+i_group_id+"_a").trigger('click');
                }
                Picture.show_pic_ajax(i_group_id,i_page_n,i_c_page);
            }else{
                $("#btnShowAllGroup").trigger("click");
            }

        },
        //本地上传图片
        local_upload: function(){
            var treeObj = $.fn.zTree.getZTreeObj("tree");
            var nodes = treeObj.getSelectedNodes();
            var group_id = nodes.length==0 ? "tree_1" : nodes[0].tId;
            var local_up = $("#upload").html("").Huploadify({
                auto: false,
                fileTypeExts: '*.jpg;*.png;*.gif',
                multi: true,
                fileObjName: 'Filedata',
                fileSizeLimit: 9999,
                formData:{group_id: group_id},
                showUploadedPercent: false,//是否实时显示上传的百分比，如20%
                showUploadedSize: false,
                removeTimeout: 500,
                buttonText: '选择文件',
                buttonClass: 'btn btn-primary',
                uploader: '/picture/upload/local',
                onUploadStart:function(){
                    $(".uploadify-button").prop("disabled",true);
                },
                onInit:function(){
                    console.log('初始化');
                   },
                onUploadSuccess:function(data){
                    var data_treeObj = $.fn.zTree.getZTreeObj("tree");
                    var data_node = data_treeObj.getNodeByTId(group_id);
                    data_treeObj.selectNode(data_node);
//                    $("#"+group_id+"_a").click();
                    var cur_node = $(".curSelectedNode");
                    if(cur_node.length!=0){
                        cur_node.trigger('click');
                    }else{
                        $("#tree_1_a").trigger('click');
                    }
                },
                onDelete:function(file){
                    console.log('删除的文件：'+file);
                    console.log(file);
                },
                onUploadError: function () {
                    Inform.enable();
                    Inform.show("上传失败，请稍后再试。");
                },
                onSelect: function(){
                    $("#ensure-up").prop("disabled",false);
                },
                onUploadComplete: function(){
                    $("#ensure-up").prop("disabled",true);
                }
            });
            $("#ensure-up").click(function(){
                local_up.upload('*');
//                local_up.destroy();
            });
        },
        check_used_space:function(max_space){
            var used_space = parseFloat($("#used_space").val());
            var percent = used_space/max_space;

            var percent_div = $(".percent-status");
            percent_div.css("width",percent*100+"%");
            if(percent>0){
                if(percent<0.5){
                    percent_div.css("background-color","#5fb129");
                }else if(percent>=0.5&&percent<0.8){
                    percent_div.css("background-color","#f0ad4e");
                }else{
                    percent_div.css("background-color","#d9534f");
                }
            }
        },
        clean_all_check:function(){
            var $dom = $("#all-pick");
            $dom.prop("checked") && $dom.trigger("click");
            $("#has-select").text(0);
        },
        check_all_pic:function(){
            var is_check = $(this).prop("checked");
            $("#photoArea").find(".photo-checkbox").filter(":visible").each(function(k,v){
                var kv = $(v);
                kv.prop("checked",is_check);
                is_check ? kv.closest(".operate-btns").show() : kv.closest(".operate-btns").hide();
                is_check ? kv.closest(".picture").addClass("pic-checked") : kv.closest(".picture").removeClass("pic-checked");
            });
            Picture.show_count();
        },
        get_length:function(){
            var count = 0;
            $("#photoArea").find(".photo-checkbox").each(function(k, v){
                if($(v).is(":checked")){
                    count += 1;
                }
            });
            return count;
        },
        get_pic_id:function(){
            var pic_id = [];
            $("#photoArea").find(".photo-checkbox").filter(":visible").each(function(k, v){
                var kv = $(v);
                if(kv.is(":checked")){
                   pic_id.push(kv.closest(".photo-operate").attr("data-id"));
                }
            });
            return pic_id;
        },
        show_count:function(){
            var count = Picture.get_length();
            $("#has-select").text(count);
        },
        detect_count:function(){
            var count = Picture.get_length();
            if(count <= 0){
                Inform.show("请至少选择一张图片");
                return false;
            }
            return true;
        },
        del_execute:function(pic_id){
            var del_ensure = confirm("确定删除吗");
            var del_type;
            if($(".activeGroup").attr("id")=="recycleBox" && btn_status!="search" && btn_status!="search-filter"){
                del_type = "complete";
            }else{
                del_type = "temp";
            }
            if(del_ensure) {
                $.ajax({
                    url: "/picture/delete",
                    type: "POST",
                    data: {
                        "pic_id": JSON.stringify(pic_id),
                        "del_type": del_type
                    },
                    dataType: "JSON",
                    success:function(data){
                        if(data.status==1){
                            $("#btnShowAllGroup").trigger("click");
                        }else{
                            Inform.enable();
                            Inform.show("删除失败");
                        }

                    }
                });
            }
        },
        del_pic:function(e){
            var pic_id = [];
            pic_id.push($(this).closest(".photo-operate").attr("data-id"));
            Picture.del_execute(pic_id);
            e.stopPropagation();
        },
        edit_pic: function (e) {
            var $this = $(this);
            var data_id = $this.closest(".photo-operate").attr("data-id"),
                data_name = $this.closest(".picture").find(".pic-name").text();
            //图片裁剪，需要模态框
            var edit_modal = $("#edit-pic-modal"),
                //this_img = $(this).closest('div[class="picture"]').find("img");
                this_img = $('div[data-id="'+data_id+'"]').closest(".picture").find("img");
            if(this_img.attr("src")!=""){
                //var pic_link =  location.href.indexOf("local")==-1 ? 'https://www.actneed.com/image/'+$("#user_id").val()+'/'+ data_id +'.jpg' : 'http://localhost:9000/image/'+$("#user_id").val()+'/'+ data_id +'.jpg';
                var pic_link = '/image/'+$("#user_id").val()+'/'+ data_id +'.jpg';
                $("#edit-img-content").empty();
                $("#edit-img-content").html("<div class='img-container'>"//class='thumbnail img-container'
                            +"<img src='" + pic_link + "' class='image img-responsive'>"
                            +"</div>");
                edit_modal.modal("show");

                var $image = $('.img-container > img'),
                    $dataX = $('#dataX'),
                    $dataY = $('#dataY'),
                    $dataHeight = $('#dataHeight'),
                    $dataWidth = $('#dataWidth'),
                    $dataRotate = $('#dataRotate'),
                    options = {
                      aspectRatio: NaN,
                      preview: '.img-preview',
                      zoomable: false,
                      crop: function (data) {
                        $dataX.val(Math.round(data.x));
                        $dataY.val(Math.round(data.y));
                        $dataHeight.val(Math.round(data.height));
                        $dataWidth.val(Math.round(data.width));
                        $dataRotate.val(Math.round(data.rotate));
                      }
                    };
                $image.cropper(options);

                // Methods
                $("#edit-pic-modal").find('[data-method="getCroppedCanvas"]').unbind().on('click', function () {
                    var $this2 = $(this);
                    $this2.button("loading");
                    var data = $this2.data(),
                        $target,
                        result;
                    if (data.method) {
                        data = $.extend({}, data); // Clone a new one
                        if (typeof data.target !== 'undefined') {
                            $target = $(data.target);
                            if(typeof data.option === 'undefined') {
                                try {
                                    data.option = JSON.parse($target.val());
                                }catch (e) {
                                    console.log(e.message+"one");
                                }
                            }
                        }
                    var $new_image = $('.img-container > img');
                    var result = $new_image.cropper(data.method, data.option);
                    var res = result.toDataURL("image/png").split(",");
                    if (data.method === 'getCroppedCanvas') {
                        $.ajax({
                            "type": "POST",
                            "url": "/picture/upload/base",
                            "dataType": "json",
                            "data": {
                                "filedata": res[res.length - 1],
                                "data_id": data_id,
                                "data_name": data_name
                            },
                            "success": function (data) {
                                 $this2.button("reset");
                                if (data.status == 1) {
                                    edit_modal.modal("hide");
                                    this_img.attr("src", data.url);
                                    this_img.closest(".picture").find(".photo-operate").attr("data-id", data.id);
                                    this_img.closest(".picture").find(".pic-info").find("span").eq(0).html("尺寸：" + data.size);
                                    this_img.closest(".picture").find(".pic-info").find("span").eq(1).html("大小：" + data.length);
                                }
                            }
                        })
                    }

                    if ($.isPlainObject(result) && $target) {
                      try {
                        $target.val(JSON.stringify(result));
                      } catch (e) {
                        console.log(e.message + "two");
                      }
                    }
                  }
                });
                $("#edit-pic-modal").on('keydown', function (e) {
                      switch (e.which) {
                        case 37:
                          e.preventDefault();
                          $image.cropper('move', -1, 0);
                          break;

                        case 38:
                          e.preventDefault();
                          $image.cropper('move', 0, -1);
                          break;

                        case 39:
                          e.preventDefault();
                          $image.cropper('move', 1, 0);
                          break;

                        case 40:
                          e.preventDefault();
                          $image.cropper('move', 0, 1);
                          break;
                      }
                });
            }else{
                return 0;
            }

            e.stopPropagation();
        },
        copy_link: function(e){
            var url = $(this).closest(".picture").find(".image").attr("src");
              if ( window.clipboardData ) {
                $('.copy_btn').click(function() {
                    window.clipboardData.setData("Text", url);
                    Inform.show("已将图片链接复制到剪贴板!");
                });
            } else {
                $(".copy_btn").zclip({
                    path:'/static/flash/ZeroClipboard.swf',
                    copy: function(){return url;},
                    afterCopy:function(){ Inform.show("已将图片链接复制到剪贴板!"); }
                });
            }

            e.stopPropagation();
        },
        del_multi_pic:function(){
            if(!Picture.detect_count()){
                return 0
            }
            var pic_id = Picture.get_pic_id();
            Picture.del_execute(pic_id);
        },

        check_pic:function(e){
            var $this = $(this);
            var is_check = $this.prop("checked");
            var check_status = true;
            is_check ? $this.siblings(".operate-btns").show() : $this.siblings(".operate-btns").hide();
            is_check ? $this.closest(".picture").addClass("pic-checked") : $this.closest(".picture").removeClass("pic-checked");
            $("#photoArea").find(".photo-checkbox").each(function(k,v){
                var kv = $(v);
                if(!kv.prop("checked")){
                    check_status = false;
                    return false;
                }
            });
            $("#all-pick").prop("checked",check_status);
            Picture.show_count();
            e.stopPropagation();
        },
        show_pic_details:function(){

        },
        goto_page:function(){
            var treeObj = $.fn.zTree.getZTreeObj("tree");
            var nodes = treeObj.getSelectedNodes();
            var group_id = "";
            if(nodes.length==0){
                group_id = $(".activeGroup").prop("id")=="recycleBox" ? "tree_0" : "all_group"
            }else{
                group_id = nodes[0].tId;
            }
            var $this = $(this);
            var page_n, c_page;
            if($this.attr("class")=="pic-every-page"){
                page_n = $this.text();
                c_page = 1;
            }else{
                page_n = $this.closest(".footer-stat").find("button").attr("data-name");
                c_page = $(this).attr("data-name");
            }
            if(btn_status=="group"){
                Picture.show_pic_ajax(group_id,page_n,c_page);
            }else if(btn_status=="group-filter"||btn_status=="search-filter"){
                Picture.filter_pic(page_n,c_page);
            }else if(btn_status=="search"){
                Picture.search_pic(page_n,c_page)
            }
            location.href = location.href.split("#")[0] + "#" + c_page;
            document.cookie = "page_n="+page_n;
            document.cookie = "group="+group_id;
        },
        show_pic_ajax:function(group_id, page_n, c_page){
            $(".loading-tip").show().siblings().hide();
            $.ajax({
                url: "/picture/group/pic",
                type: "POST",
                data: {
                    group_id: group_id.toString(),
                    page_n: Number(page_n),
                    c_page: Number(c_page)
                },
                success: function(data){
                    $(".loading-tip").hide();
                    if(data.status == 1){
                        if(data["pictures"].length==0){
                            $("#no-pic-tip").show().siblings().hide();
                        }else{
                            var pictures = data["pictures"],
                                col_map = data["col_map"],
                                page_total = data["page_total"],
                                page_n = data["page_n"],
                                pages = data["pages"],
                                c_page = data["c_page"];
                            Picture.render_pic(pictures,col_map,page_total,page_n,pages,c_page);
                        }
                    }else{
                        Inform.show("操作失败");
                    }
                },
                error: function(){
                    Inform.enable();
                    Inform.show("操作失败");
                }

            });
        },
        show_group_pic:function(){
            var $this = $(this);
            var group_id = "all_group";
            var page_n = $(".footer-stat").find("button").attr("data-name") || 50;
            if($this.prop("id")=="btnShowAllGroup"){
                Picture.show_pic_ajax("all_group",page_n,1)
            }else if($this.prop("id")=="recycleBox"){
                group_id = "tree_0";
                Picture.show_pic_ajax(group_id,page_n,1)
            }
            if(Picture.getCookie("group")!=group_id){
                location.href = location.href.split("#")[0] + "#1";
            }
            document.cookie = "page_n="+page_n;
            document.cookie = "group="+group_id;
            Picture.clean_all_check();
        },
        add_group_node:function(e){
            e.stopPropagation();
            var $this = $(this);
            var treeObj = $.fn.zTree.getZTreeObj("tree");
            var nodes = treeObj.getSelectedNodes();
            var newNode = {},
                $node = "";
            if(nodes.length>0){
//                console.log(nodes);
                if(nodes[0].id=="no-group"){
                    $("#dis_tip").show();
                    setTimeout(function(){$("#dis_tip").fadeOut(1000)},1500);
                }else if(nodes[0].level==1){
                    $("#dis_tip2").show();
                    setTimeout(function(){$("#dis_tip2").fadeOut(1000)},1500);
                }else{
                    newNode = {name:"新建子文件夹"};
                    $node = treeObj.addNodes(nodes[0],-1, newNode);
                }
            }else{
                newNode = {name:"新建文件夹", isParent:true};
                $node = treeObj.addNodes(null, newNode);
            }
            if($node) {
                var node_name = $node[0]["name"],
                    node_pid = $node[0]["parentTId"],
                    node_id = $node[0]["tId"];
                var group_value = node_pid + ";" + node_id + ";" + node_name;
                $.ajax({
                    url: "/picture/group/add",
                    type: "POST",
                    data: {
                        group_value: group_value
                    },
                    success: function (data) {
                        if(data.status==1){
                            Picture.clean_all_check();
                        }else{
                            Inform.enable();
                            Inform.show("添加失败，请刷新页面后重试。")
                        }
                    }
                })
            }
        },
        dropdown_render:function(){
            var $this = $(this);
            var $ul = $this.attr("id") == "move-select" ? $this.siblings("ul") : $this.siblings("ul").find(".ztree");
            var treeObj = $.fn.zTree.getZTreeObj("tree");
            zTreeObj_s  = $.fn.zTree.init($ul, setting, treeObj.getNodes());
            zTreeObj_s.expandAll(true);
        },
        check_all_group:function(){
            var treeObj = $.fn.zTree.getZTreeObj("tree");
                treeObj.cancelSelectedNode();
        },
        group_active:function(){
            btn_status = "group";
            Picture.check_all_group(); // cancel tree node selected
            var $this = $(this);
            $this.addClass("activeGroup").closest("#photoBankGroupList").find(".groupTitle").not($this).removeClass("activeGroup");
        },
        choose_option:function(){

        },
        empty_pic_area:function(){
            var pic_area = $("#photoList");
            pic_area.empty();
            pic_area.siblings(".footer-stat").remove();
        },
        render_pic:function(pictures,col_map,page_total,page_n,pages,c_page){
            Picture.empty_pic_area();
            var pic_area = $("#photoList");
            pic_area.show().siblings().hide();
            for(i=0; i<pictures.length; i++){
                var add_div = Picture.create_pic(pictures[i]);
                pic_area.append(add_div)
            }
            var page_str = '<div class="row footer-stat">'+
                        '<ul class="nav pull-right">'+
                        '<li><ul class="pagination page-bar">{0}{1}{2}</ul></li>'+
                        '<li class="btn-group page-n-ctrl">'+
                        '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false" data-name='+page_n+'>'+
                        '每页显示'+page_n+'个 <span class="caret"></span>'+
                        '</button>'+
                        '<ul class="dropdown-menu" role="menu">'+
                        '<li><a href="javascript:void(0)" class="pic-every-page">30</a></li>'+
                        '<li><a href="javascript:void(0)" class="pic-every-page">50</a></li>'+
                        '<li><a href="javascript:void(0)" class="pic-every-page">100</a></li>'+
                        '</ul>'+
                        '</li>'+
                        '<li style="line-height:36px;">共'+page_total+'页</li>'+
                        '</ul></div>';
            var p_str = "",
                n_str = "",
                m_str = "";
            if(c_page==1){
                p_str = '<li class="disabled">'+
                        '<a href="javascript:void(0)" aria-label="Previous">'+
                        '<span aria-hidden="true">&laquo;</span>'+
                        '</a>'+
                        '</li>';
            }else{
                p_str = '<li>'+
                        '<a href="javascript:void(0)" aria-label="Previous" class="goto-page" data-name='+(c_page-1)+'>'+
                        '<span aria-hidden="true">&laquo;</span>'+
                        '</a>'+
                        '</li>';
            }
            if(c_page >= page_total){
                n_str = '<li class="disabled">'+
                        '<a href="javascript:void(0)" aria-label="Previous">'+
                        '<span aria-hidden="true">&raquo;</span>'+
                        '</a>'+
                        '</li>';
            }else{
                n_str = '<li>'+
                        '<a href="javascript:void(0)" aria-label="Next" class="goto-page" data-name='+(c_page+1)+'>'+
                        '<span aria-hidden="true">&raquo;</span>'+
                        '</a>'+
                        '</li>';
            }
            for(var page=0;page<pages.length;page++){
                if(pages[page]==c_page){
                    m_str += '<li class="active" data-name='+pages[page]+'>'+
                            '<a href="javascript:void(0)">'+pages[page]+''+
                            '</a>'+
                            '</li>';
                }else{
                    m_str += '<li>'+
                            '<a href="javascript:void(0)" class="goto-page" data-name='+pages[page]+'>'+pages[page]+''+
                            '</a>'+
                            '</li>';
                }
            }
            page_str = page_str.format(p_str,m_str,n_str);
            pic_area.after(page_str);
        },
        create_pic:function(picture){
            var operate_div,operate_str,img_div, img, info_div, title_div, block;
            block = $("<div/>").attr("class", "picture");
            img = $("<img/>").attr({
                "class": "image",
                "title": picture.Name,
                "src": picture.Link
            });
            operate_str = '<label><input type="checkbox" class="photo-checkbox"></label>'+
                '<span class="operate-btns" style="display: none;">'+
                '<a class="pic-delete" href="javascript:void(0)" title="删除">'+
                '<span class="glyphicon glyphicon-remove"></span></a>'+
                '<a class="pic-edit" href="javascript:void(0)" title="编辑图片">'+
                '<span class="glyphicon glyphicon-edit"></span></a>'+
                '<a class="copy_link" href="javascript:void(0)" title="复制图片链接">'+
                '<span class="glyphicon glyphicon-copy"></span></a></span>';
            img_div = $("<div/>").attr("class", "img-content");
            operate_div = $("<div/>").attr({
                "class": "photo-operate",
                "data-id": picture.Id
            }).append(operate_str);
            img_div.append(img);
            info_div = $("<div/>").attr("class", "pic-info").html("<span>尺寸：{0}</span> <span>大小：{1}</span>".format(picture.Size, picture.Length));
            title_div = $("<div/>").attr("class", "pic-name").text(picture.Name);
            block.append(operate_div,img_div,title_div,info_div);
            return block
        },
        search_pic:function(){
            var $this = $(this);
            var tree_index = $(".search-key").attr("data-id");
            var group_id = tree_index == "all_group" ? "all_group" : "tree_"+tree_index.split("_")[1],
                pic_title = $("#search-input").val().trim();
            var start_time = "",
                end_time = "";
            if(btn_status=="filter"){
                start_time = condition_info["start_time"];
                end_time = condition_info["end_time"];
            }
            btn_status = "search";
            condition_info["group_id"] = group_id;
            condition_info["pic_title"] = pic_title;
            var page_n = Number($(".pic-every-page").text()),
                c_page = 1;
            console.log(arguments[0]);
            if(arguments&&arguments.length>1){
                page_n = arguments[0];
                c_page = arguments[1];
            }
            if(pic_title){
                $("#search-input").prop("placeholder","图片名称");
                $(".loading-tip").show().siblings().hide();
                $.ajax({
                    url: "/picture/search",
                    type: "POST",
                    data: {
                        "group_id": group_id,
                        "pic_title": pic_title,
                        "page_n": page_n,
                        "c_page": c_page
                    },
                    success:function(data){
                        $(".loading-tip").hide();
                        if(data["pictures"].length!=0){
                            var pictures = data["pictures"],
                                col_map = data["col_map"],
                                page_total = data["page_total"],
                                page_n = data["page_n"],
                                pages = data["pages"],
                                c_page = data["c_page"];
                            Picture.render_pic(pictures,col_map,page_total,page_n,pages,c_page);
                        }else{
                            Picture.empty_pic_area();
                            $("#no-search-tip").show().siblings().hide();
                        }
                    }
                })
            }else{
                $("#search-input").prop("placeholder","请输入图片名称")
            }
        },
        filter_pic:function(){
//            var quote_status = $("#select-status").val(),
            var start_time = $("#start-time").val(),
                end_time = $("#end-time").val();
            var treeObj = $.fn.zTree.getZTreeObj("tree");
            var nodes = treeObj.getSelectedNodes();
            var group_id = nodes.length==0 ? "all_group" : nodes[0].tId;
            var pic_title = "";
            if(btn_status=="search"||btn_status=="search-filter"){
                group_id = condition_info["group_id"];
                pic_title = condition_info["pic_title"];
                btn_status = "search-filter";
            }else{
                btn_status = "group-filter";
            }
            condition_info["start_time"] = start_time;
            condition_info["end_time"] = end_time;
            var page_n = Number($(".pic-every-page").text()),
                c_page = 1;
            if(arguments&&arguments.length>1){
                page_n = arguments[0];
                c_page = arguments[1];
            }
            $(".loading-tip").show().siblings().hide();
            $.ajax({
                url: "/picture/filter",
                type: "POST",
                data: {
                    "group_id": group_id,
//                    "quote_status": quote_status,
                    "start_time": start_time,
                    "end_time": end_time,
                    "pic_title": pic_title,
                    "page_n": page_n,
                    "c_page": c_page
                },
                success:function(data){
                    $(".loading-tip").hide();
                    if(data["pictures"].length!=0){
                        var pictures = data["pictures"],
                            col_map = data["col_map"],
                            page_total = data["page_total"],
                            page_n = data["page_n"],
                            pages = data["pages"],
                            c_page = data["c_page"];
                        Picture.render_pic(pictures,col_map,page_total,page_n,pages,c_page);
                    }else{
                        Picture.empty_pic_area();
                        $("#no-search-tip").show().siblings().hide();
                    }
                }
            })
        },
        show_mark_modal:function(){
            if(!Picture.detect_count()){
                return 0
            }
            $("#add-mark").modal("show");
        },
        add_mark:function(){
            var pos_list = ["mt", "mc", "mb"];
            var mark_cont = $("#mark-cont").val().trim();
            if(mark_cont.length > 20){
                Inform.show("水印长度不能超过20个字符");
                return 0;
            }else if(mark_cont.length==0){
                Inform.show("请输入水印文字");
                return 0;
            }
            var position = pos_list[$(".ex-block").filter(".on").index()];
            var data_list = Picture.get_pic_id();
            console.log(position+"++++"+data_list+"------"+mark_cont);
            $("#add-mark").modal("hide");
            $.ajax({
                url:"/picture/watermark",
                type:"POST",
                data: {
                    mark_txt: mark_cont,
                    main_image: JSON.stringify(data_list),
                    position: position || "mb"
                },
                dataType: "json",
                success: function(data){
                    Inform.enable("", true);
                    if(data.status == 1){
                        Inform.show("成功为图片添加水印");
                        var cur_node = $(".curSelectedNode");
                        if(cur_node.length!=0){
                            cur_node.trigger('click');
                        }else{
                            $(".activeGroup").trigger('click');
                        }
                    }else{
                        Inform.show("添加水印失败");
                    }
                },
                error: function(){
                    Inform.enable();
                    Inform.show("添加水印失败");
                }
            })

        },
        scroll_listener: function(){
            var to_top = $(window).scrollTop();
            if(to_top>$(window).height()*0.5){
                $(".to-top").fadeIn(300);
            }else{
                $(".to-top").fadeOut(300);
            }
        },
        getCookie:function(name)
        {
            var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
            if(arr=document.cookie.match(reg))
            return unescape(arr[2]);
            else
            return null;
        }
    };
    Picture.init();
});