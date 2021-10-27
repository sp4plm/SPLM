$(function(){
    var _$box, _base_url, _$frm;

    function _removeSectionParam() {
        var _$btn, _$pbox, _name, _val,
            has_name=false, has_val=false, _to_delete=false;
        _$btn = $(this);
        _$pbox = _$btn.parent().parent();
        _name = _$pbox.find('.param-name input').val();
        _val = _$pbox.find('.param-value input').val();
//        if(confirm('Вы действительно хотите удалить параметр "' + _name + '"?')) {
//            _$pbox.remove();
//        }
        has_name = ('' !== _name);
        has_val = ('' !== _val);
        _to_delete = (has_name || has_val);
        if(_to_delete){
            _to_delete = confirm('Вы действительно хотите удалить параметр "' + _name + '"?')
        }else{
            _to_delete = true;
        }
        if(_to_delete) {
            _$pbox.remove();
        }
    }

    function _addSectionParam() {
        var sect_tpl, _$btn, _$tpl;
        _$btn = $(this);
        sect_tpl = _getParamTpl();
        if('' != sect_tpl){
            _$tpl = $(sect_tpl);
            _$btn.parent().parent().find('.section-data').append(_$tpl);
            _$tpl.find('button').button();
            _$tpl.find('.del-section-param').on('click', _removeSectionParam);
        }
    }

    function _getSectionTpl(){
        var _html, url;
        url = _base_url + '/configs/section/tpl'
        _html = '';
        $.ajax({
            async: false,
            url: url,
            success: function (answ) {
                if (answ) {
                    _html = answ;
                }
            }
        });
        return _html;
    }

    function _getParamTpl(){
        var _html, url;
        url = _base_url + '/configs/param/tpl'
        _html = '';
        $.ajax({
            async: false,
            url: url,
            success: function (answ) {
                if (answ) {
                    _html = answ;
                }
            }
        });
        return _html;
    }

    function _removeSection() {
        var _$btn, _$pbox, _name;
        _$btn = $(this);
        _$pbox = _$btn.parent().parent();
        _name = _$pbox.find('.section-name input').val();
        if(confirm('Вы действительно хотите удалить секцию "' + _name + '"?')) {
            _$pbox.remove();
        }
    }

    function _addConfigSection() {
        var sect_tpl, _$tpl;
        sect_tpl = _getSectionTpl();
        if('' != sect_tpl){
            _$tpl = $(sect_tpl);
            _$frm.append(_$tpl);
            _$tpl.find('button').button();
            _$tpl.find('.add-section-param').on('click', _addSectionParam);
            _$tpl.find('.del-section').on('click', _removeSection);
        }
    }

    function getData4Save() {
        var data, secNum=1, secPref='Section';
        data = {};
        data['ConfigName'] = '';
        data['ConfigName'] = _$frm.find('input[name="ConfigName"]').val(); // новое имя (доступно для редактирования)
        data['ConfigOrigin'] = '';
        data['ConfigOrigin'] = _$frm.find('input[name="ConfigOrigin"]').val(); // основное имя (недоступно для редактирования)
        // теперь по ключу Content будем хранить содержание
        data['ConfContent'] = {}
        _$frm.find('.section-box').each(function(){
            var _$curBox, secName;
            _$curBox = $(this);
            secName = _$curBox.find('.section-name input').val();
            if('' == secName) {
                secName = secPref + secNum;
                secNum++;
            }
            data['ConfContent'][secName] = _getSectionParams(_$curBox.find('.section-data:first'));
        });
        return data;
    }

    function _getSectionParams(_$root) {
        var params = {}, parPref = 'Param', parNum=1;
        _$root.find('.section-param').each(function(){
            var paramKey, paramVal;
            paramKey = $(this).find('.param-name .value-editor').val();
            if ('' == paramKey) {
                paramKey = parPref + parNum;
                parNam++;
            }
            paramVal = $(this).find('.param-value .value-editor').val();
            paramVal = _getParamValue($(this).find('.param-value:first'))
            params[paramKey] = paramVal;
        });
        return params;
    }

    function _getParamValue(_$vbox) {
        var val;
        if(0 == _$vbox.find('.multiple-value').length) {
            val = _$vbox.find('.value-editor').val();
        } else {
            val = {};
            _$vbox.find('.multival-data').each(function(){
                var k, v;
                k = $(this).find('.multival-key').val();
                v = $(this).find('.multival-data').val();
                val[k]=v;
            });
        }
        return val;
    }

    function normalizeValue(val) {
        var newVal;
        newVal = val;
        if('{' === val[0]) {

        }
        return newVal;
    }

    function _saveConfig() {
        var sendData, url;
        sendData = getData4Save();
        url = _base_url + '/configs/' + sendData['ConfigOrigin'] + '/save'
        $.post(url, sendData, function(answ){
            if(answ){
                if(typeof void null!=typeof answ['State'] && 200 == answ['State']){
                    alert('Конфигурационный файл успешно сохранен!');
                }
                if(typeof void null!=typeof answ['Msg'] && '' != answ['Msg']){
                    alert(answ['Msg']);
                }
            }else{
                alert('Неизвестная ошибка при сохранении конфигурационного фала');
            }
        }, 'json');
        // alert('Запущен процес сохранения конфигурационного файла!');
    }

    _$box = $('#page-content-marker').parent().parent();
    // уберем высоту блока - заменим ее на auto
    $('#page-content-marker').parent().css('height','auto');
    _$box.css('height','auto');
    _$box.parent().css('height','auto');
    _base_url = _$box.find('#js-base-url').val();
    _$box.find('button').button();
    _$frm = _$box.find('form[name="ConfigEditorFrm"]');
    _$box.find('button[name="AddSection"]').on('click', _addConfigSection);
    _$box.find('button[name="SaveConfig"]').on('click', _saveConfig);
});