var RegisterHandler = function () {

}

RegisterHandler.prototype.listenSendCaptchaEvent = function () {
    var callback = function (event) {
        // 原生的JS对象: this => jQuery对象
        var $this = $(this);
        // 阻止默认的点击事件
        event.preventDefault()
        var email = $("input[name='email']").val();
        var reg = /^\w+((.\w+)|(-\w+))@[A-Za-z0-9]+((.|-)[A-Za-z0-9]+).[A-Za-z0-9]+$/;
        if (!email || !reg.test(email)) {
            alert('请输入正确格式的邮箱！');
            return;
        }
        zlajax.get({
            url: '/email/captcha?email=' + email, success: function (result) {
                if (result['code'] == 200) {
                    console.log('验证码生成成功！');
                    
                    // 只显示验证码已发送的提示
                    alert(result['message']);
                    
                    $this.off("click");
                    // 添加禁用状态
                    $this.attr("disabled", "disabled");
                    // 开始倒计时
                    var countdown = 6;
                    var interval = setInterval(function () {
                        if (countdown > 0) {
                            $this.text(countdown);
                        } else {
                            $this.text("发送验证码");
                            $this.attr("disabled", false);
                            $this.on("click", callback);
                            // 清理定时器
                            clearInterval(interval);
                        }
                        countdown--;

                    }, 1000);
                } else {
                    var message = result['message'];
                    alert(message);
                }
            }
        })
    }
    $("#email-captcha-btn").on("click", callback);
}

RegisterHandler.prototype.listenGraphCaptchaEvent = function () {
    $("#captcha-img").on("click", function () {

        var $this = $(this);
        var src = $this.attr("src");

        // 方法一
        // 添加时间戳或随机数作为查询参数
        // var newSrc = src.split('?')[0] + "?t=" + new Date().getTime();
        // $this.attr("src", newSrc);
        // 方法二
        // 防止一些老的浏览器 在两次相同url的情况下 不会重新发送请求 导致图片验证码无法更新
        let new_src = zlparam.setParam(src, "sign", Math.random());
        $this.attr("src", new_src);
        console.log("点击验证码生成！")
    });
}

RegisterHandler.prototype.listenSubmitEvent = function () {
    $("#submit-btn").on("click", function (event) {
        event.preventDefault();
        var email = $("input[name='email']").val();
        var email_captcha = $("input[name='email-captcha']").val();
        var username = $("input[name='username']").val();
        var password = $("input[name='password']").val();
        var repeat_password=$("input[name='repeat-password']").val();
        var graph_captcha = $("input[name='graph-captcha']").val();
        // 如果是商业项目,一定要先验证这些数据是否正确
        zlajax.post({
            url: '/register/',
            data:{
                "email": email,
                "email_captcha": email_captcha,
                "username": username,
                "password": password,
                "repeat_password": repeat_password,
                "graph_captcha": graph_captcha
            },
            success: function (result) {
                if(result['code'] == 200) {
                    window.location="/login";
                }else{
                    alert(result['message']);
                }
            }
        });

    });
}

RegisterHandler.prototype.run = function () {
    this.listenSendCaptchaEvent();
    this.listenGraphCaptchaEvent();
    this.listenSubmitEvent();
}

$(function () {
    var handler = new RegisterHandler();
    handler.run()
});
