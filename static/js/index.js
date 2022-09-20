// 全局变量：用户的id
var userid = $('#userId').text()
// 全局变量：原图片上传之后的文件名
var FILENAME;
// 全局变量：当前转换风格之后的文件名，用于下载文件
var DOWN_FILENAME



/**
 * 监听选择文件框的状态，有改变之后就进行上传文件
 */
$('body').on('change','#upLoad',function () {

    console.log("userid==",userid)

    // var oldimg = $('#oldimg').attr("src")
    // console.log("oldimg=",oldimg)

    var formData = new FormData();
    var name = $($(this)).val();
    var files = $($(this))[0].files[0];
    formData.append("file",files)
    console.log(files)
    formData.append("name",name)
    console.log("name==",name)
    formData.append("userId",userid)

    // 如果选择文件不为空
    if (files != undefined){
        console.log("选择文件完成，开始提交")

        // 每次选择图片之后，镜像和迁移的选择框返回初始状态
        $("#jingxiang").val('original');
        $("#transfer").val('original');
        // 并将迁移的模型图不显示
        $('#models_img').attr("src","");
        $('#models_img').hide()

        // 每次选择图片之前先清除图片框的css样式
        $("#oldimg").removeClass("imageHeight","imageWidth");
        $("#newimg").removeClass("imageHeight","imageWidth");

        // 每次选择新图片时单选框选择原图
        $("#original").prop("checked","checked");

        //初始化FileReader对象
        var reader = new FileReader();
        // 读取图片文件
        reader.readAsDataURL(files);
        reader.onload = function (e){
            // 初始化JavaScript图片对象
            var image = new Image();
            // FileReader获得Base64字符串
            image.src = e.target.result;
            image.onload = function (){
                // 获得图片宽高
                var width = image.width;
                var height = image.height;

                if (width>=600 || height>=500){
                    if (width>=height+100){
                        $("#oldimg").addClass("imageWidth");
                        $("#newimg").addClass("imageWidth");
                    }else {
                        $("#oldimg").addClass("imageHeight")
                        $("#newimg").addClass("imageHeight")
                    }
                }

                // 将图片的宽高添加到请求数据中
                formData.append("width",width);
                formData.append("height",height);
                console.log("width=",width,"\theight=",height);
            }
        }


        // 开始发送ajax请求上传图片
        $.ajax({
            url:'/upload',
            type:'POST',
            data:formData,
            processData: false,  // 告诉jQuery不要去处理发送的数据
            contentType: false,  // 告诉jQuery不要去设置Content-Type请求头
            dataType:'json',
            success:function (res){
                // 拼接图片的完成请求路径。路径+文件名
                var imgSrc = res.data.fileUrl+res.data.fileName;
                FILENAME = res.data.fileName;
                DOWN_FILENAME = res.data.fileName;
                console.log(imgSrc);
                // document.getElementById('imgg').src = imgSrc;
                $('#oldimg').attr("src",imgSrc)
                $('#newimg').attr("src",imgSrc)

                $('#down').attr("href",imgSrc);
            },
            error:function (res){
                alert("文件上传失败，请检查文件格式和大小")
            }
        });
    }
    else {
        alert("没有选择文件")
    }
})

/**
 * 监听镜像的下拉框
 */
$('#jingxiang').change(function () {
    if (FILENAME == undefined) {
        alert("请先上传图片")
    } else {
        var data = {
            "user_id": userid,
            "fileName": FILENAME
        }
        // 每次转换之后，迁移的选择框返回初始状态
        $("#transfer").val('original');
        // 并将迁移的模型图不显示
        $('#models_img').hide()
        $('#models_img').attr("src","");
        var opt = $('#jingxiang').val();
        // 请求接口
        $.ajax({
            // 拼接请求的url
            url: '/' + opt,
            type: 'POST',
            // 参数为data
            data: data,
            dataType: 'json',
            success: function (res) {
                DOWN_FILENAME = res.data.fileName;
                var imgSrc = res.data.fileUrl + res.data.fileName;
                console.log(imgSrc);
                // document.getElementById('imgg').src = imgSrc;
                $('#newimg').attr("src", imgSrc);
                // 将图片地址添加到“下载文件”的标签链接中
                $('#down').attr("href", imgSrc);
            },
            error: function (res) {
                alert("转换失败，请重试")
            }
        })
    }
})

/**
 * 监听迁移的下拉框
 */
$('#transfer').change(function () {
    if (FILENAME == undefined) {
        alert("请先上传图片")
    } else {
        var data = {
            "user_id": userid,
            "fileName": FILENAME
        }
        var style = $('#transfer').val();
        data['style'] = style
        console.log("data===",data)

        // 请求接口
        $.ajax({
            // 拼接请求的url
            url: '/transfer' ,
            type: 'POST',
            // 参数为data
            data: data,
            dataType: 'json',
            success: function (res) {
                DOWN_FILENAME = res.data.fileName;
                var imgSrc = res.data.fileUrl + res.data.fileName;
                console.log(imgSrc);
                // 转换成功之后，把风格的模型图象显示出来
                $('#models_img').attr("src",res.data.modelsImg);
                $('#models_img').show();
                // document.getElementById('imgg').src = imgSrc;
                $('#newimg').attr("src", imgSrc);
                // 将图片地址添加到“下载文件”的标签链接中
                $('#down').attr("href", imgSrc);

            },
            error: function (res) {
                alert("转换失败，请重试")
            }
        })
    }
})

/**
 * 选择转换风格之后，开始请求后台进行转换
 * @param e 当前选中的单选框标签
 */
function changeStyle(e) {
    // 判断目前有无图片
    if (FILENAME == undefined) {
        alert("请先上传图片")
    } else {
        // 封装请求消息
        var data = {
            "user_id": userid,
            "fileName": FILENAME
        }
        // 获取单选框的值，也就是转换的类型，与后台的请求接口相对应
        var style = e.value;
        // 因为彩色字符换支持自定义字符，所以进行判读，如果是彩色字符就添加请求参数
        if (style == "strimgColor"){
            var str = $('#strimgColorIn').val();
            if (str.length > 8){
                alert("字符超出长度，最长8个字符");
                return;
            }
            else {
                data['str'] = $('#strimgColorIn').val();
                console.log("data==",data)
            }
        }
        // 请求接口
        $.ajax({
            // 拼接请求的url
            url: '/' + style,
            type: 'POST',
            // 参数为data
            data: data,
            dataType: 'json',
            success: function (res) {
                DOWN_FILENAME = res.data.fileName;
                var imgSrc = res.data.fileUrl + res.data.fileName;
                console.log(imgSrc);
                // document.getElementById('imgg').src = imgSrc;
                $('#newimg').attr("src", imgSrc);
                // 将图片地址添加到“下载文件”的标签链接中
                $('#down').attr("href", imgSrc);
                // 每次转换图片之后，镜像和图像迁移的选择框返回初始状态
                $("#jingxiang").val('original');
                $("#transfer").val('original');
                // 并将迁移的模型图不显示
                $('#models_img').hide()
                $('#models_img').attr("src","")
            },
            error: function (res) {
                alert("转换失败，请重试")
            }
        })
    }
}

/**
 * 根据id请求个人信息
 */
function setUser(){
    $.ajax({
        url:"/getById",
        type:'POST',
        data:{id:userid},
        dataType:'json',
        success: function (res){
            console.log(res)
        },
        error: function (res){

        }
    })
}

/**
 * 点击修改头像的上传文件
 */
function changeAva(){
    // 模拟点击input:file按钮
    $('#changetouxiang').click();
}

/**
 * 修改头像的选择文件，并回显
 */
$("#changetouxiang").change(function (e){

    console.log("e.target=111=",e.target)

    var formData = new FormData();
    var name = e.target.files[0].name;
    var files = e.target.files[0];
    formData.append("file",files)
    console.log("files=111=",files)
    formData.append("name",name)
    console.log("name=111=",name)
    formData.append("userId",userid)

    console.log("formData=111=",formData)

    if (files != undefined) {

        // 开始发送ajax请求上传图片
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,  // 告诉jQuery不要去处理发送的数据
            contentType: false,  // 告诉jQuery不要去设置Content-Type请求头
            dataType: 'json',
            success: function (res) {
                // 拼接图片的完成请求路径。路径+文件名
                var imgSrc = res.data.fileUrl + res.data.fileName;
                // 将上传的头像图片回显
                $('#touxiang').attr("src", imgSrc);
            },
            error: function (res) {
                alert("文件上传失败，请检查文件格式和大小")
            }
        });
    }else {
        alert("没有选择文件");
    }
})

/**
 * 修改个人信息
 */
function update(){
    id = userid;
    username = $('#user_name').val();
    avatarUrl = $('#touxiang').attr("src");
    email = $('#email').val();
    password = $('#password').val();
    repassword = $('#re_password').val();
    var data = {
        "id":id,
        "username":username,
        "avatarUrl":avatarUrl,
        "email":email,
        "password":password,
        "repassword":repassword
    }
    $.ajax({
        url:"/update",
        type:"POST",
        data:data,
        dataType: 'json',
        success:function (res){
            console.log("res.data====",res)
            if (res.status == 200){
                // alert("修改成功");
                // console.log("res.data.username==",res.data.username);
                // console.log("res.data.avatarUrl==",res.data.avatarUrl);
                $('#right-name').text(res.data.username);
                $('#right-touxiang').attr("src",res.data.avatarUrl);
                alert(res.msg)
            }else {
                alert(res.msg);
            }

        },
        error:function (res){
            alert("修改失败")
        }
    })
}