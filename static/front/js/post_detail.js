$(function () {
    // 初始化代码高亮
    hljs.highlightAll();
    $("#comment-btn").on("click", function (event) {
        event.preventDefault();
        var $this = $(this);
        // 获取评论的内容
        var user_id = $this.attr('data-user-id');
        if(!user_id || user_id =="") {
            // 如果没有用户 跳转到登录界面
            window.location = "/login";
            return;
        }
        var content = $("#comment-textarea").val();
        var post_id = $this.attr('data-post-id');
        zlajax.post({
            url:"/comment",
            data:{content,post_id},
            success:function(result){
                if(result['code']==200){
                    window.location.reload();//强制重新加载当前页面。
                }else{
                    alert(result['message'] || "请登录后评论！");
                }
            }
        })
    });
});
