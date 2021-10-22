$(function(){
    $('#SearchIn').click(function(){
        $(this).val((($(this).is(':checked'))? 1:0));
    });
})