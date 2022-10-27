$(function(){
    var _$box, _base_url;

    function runInstallation(){
        var _url,_data;
        _url = _base_url + '/run';
        _data = {};
        $.post(_url, _data, function(answ){
            if(answ){
                _$box.find('#results-informer').html(answ);
            }
            _$box.find('button').button('enable');
        }, 'html');
    }

    function runUnInstallation(){
        var _url,_data;
        _url = _base_url + '/uninstall';
        _data = {};
        $.post(_url, _data, function(answ){
            if(answ){
                _$box.find('#results-informer').html(answ);
            }
            _$box.find('button').button('enable');
        }, 'html');
    }

    function clickInstallerBtn(){
        var $btn, _act;
        // this - button in first cell of edit row
        $btn = $(this);
        _act = $btn.attr('act');
        $btn.button('disable');
        switch(_act) {
            case "run":
                runInstallation();
                break;
            case "uninstall":
                runUnInstallation();
                break;
        }
    }

    _$box = $('#page-content-marker').parent().parent();
    _base_url = _$box.find('#js-base-url').val();
    _$box.find('button').button();
    _$box.find('button').on('click', clickInstallerBtn);
});