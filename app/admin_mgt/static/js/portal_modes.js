$(function(){
    var _$box, _base_url, _$tbl;

    function stopPortalMode() {
        var _$tr, _name, _$a, _href;
        _$tr = $(this).parent().parent();
        _name = _$tr.find('.mode-name').html();
        _$a = $('<a style="display:none;"></a>');
        _href = _base_url + '/drop/' + _name;
        _$a.attr('href', _href);
        $('body').append(_$a);
        _$a[0].click();
    };

    _$box = $('#page-content-marker').parent();
    _base_url = _$box.find('#js-base-url').val();
    _$box.find('button').button();
    _$tbl = _$box.find('#portal-modes-list');

    //  теперь надо подписаться на событие сброса режима
    _$tbl.find('.row-toolbar > button').each(function(){
        $(this).on('click', stopPortalMode);
    });
});