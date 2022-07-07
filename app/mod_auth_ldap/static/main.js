(function($){
    var _$box, _baseURL;

    function _addNewServer() {
        var $a, _href;
        _href = _baseURL + '/server/new'
        $a = $('<a style="display:none;"></a>');
        $a.attr('href', _href);
        $('body').append($a);
        $a.get(0).click();
    }

    _$box = $('#page-content-marker').parent().parent(); // на шаг выше для захвата колонки левой навигации
    _baseURL = _$box.find('#js-base-url').val();

    _$box.find('button').button();
    $('#reg-new-server').on('click', _addNewServer);
})(jQuery);