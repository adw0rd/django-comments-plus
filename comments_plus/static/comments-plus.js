$(document).ready(function(){
    var form = $('#comments-plus-form');
    var fields_error_css = {'border': '1px solid red'};
    var fields_reset_css = {'border': ''};

    // Reset a fields border
    form.find('input, textarea, select').focus(function(){
        $(this).css(fields_reset_css);
    });

    form.submit(function(){
        var data = form.serialize();
        $.post('/comments/post/', data, 'json').success(
            function(response){
                if (response.errors) {
                    var errors = response.errors;
                    var errors_area = form.find('.errors');
                    errors_area.html("");
                    for (error_name in errors) {
                        form.find('input[type!="hidden"], textarea, select').each(function(){
                            var elem = $(this);
                            if (elem.attr('name') == error_name) {
                                elem.css(fields_error_css);
                            }
                        });
                        errors_area.append('<li>Ошибка в поле "' + error_name + '", ' + errors[error_name] + '</li>');
                    }
                } else {
                    if (response.next) {
                        next = response.next;
                    } else {
                        next = form.find('input[name="next"]').val();
                    }
                    location.href = next;
                    location.reload();
                    form.find('input[type!="hidden"], textarea, select').val('');
                }
            }
        );
        return false;
    });
});