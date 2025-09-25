var LoginHandler = function () {
}

LoginHandler.prototype.listenSubmitEvent = function () {
    $("#submit-btn").on("click", function (event) {
        event.preventDefault();
        var email = $("input[name='email']").val();
        var password = $("input[name='password']").val();
        var remember_me = $("input[name='remember_me']").prop("checked");
        zlajax.post({
            url: '/login', data: {
                email, password, remember_me: remember_me ? 1 : 0
            }, success: function (result) {
                if (result['code'] == 200) {
                    var token = result['data']['token'];
                    var user = result['data']['user'];
                    localStorage.setItem('JWT_TOKEN_KEY', token); // 用于将一个名为 JWT_TOKEN_KEY 的键值对存储到浏览器的 localStorage 中
                    localStorage.setItem("USER_KEY",JSON.stringify(user) );
                    console.log(user);
                    window.location = "/";
                } else {
                    alert(result['message']);
                }
            }
        })
    });
}

LoginHandler.prototype.run = function () {
    this.listenSubmitEvent();
}

$(function () {
    var handler = new LoginHandler();
    handler.run();
});