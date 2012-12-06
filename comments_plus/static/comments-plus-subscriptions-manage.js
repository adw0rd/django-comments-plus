$(document).ready(function(){
    $('.unsubscribe-button').on('click', function(){
        var _this = $(this);
        $.get(_this.attr('href'), {'json': true}, function(response){
            if (response.status == "success") {
                _this.parent().parent().hide('slow');
            }
        }, 'json');
        return false;
    });
});