(function(win,undefined){
    var _clsTextEditVars;

    _clsTextEditVars = function(_eventBus) {
        var _this = this;

        _this._box = null;

        _this.getVarsListBox = function() { return $('#vars-list-box'); };

        _this.clearVars = function(){
            var _$listBox;
            //  получить контейнер
            _$listBox = _this.getVarsListBox();

            _$listBox.find('.text-var').each(function(){
                $(this).remove();
            });
        };

        _this.addVar = function(_name, _val){
            var _$listBox, _$vt;
            _$listBox = _this.getVarsListBox();
            _$vt = __getVarTemplate();
            _$vt.find('.data-row .remove-btn').click(_this.remVar);
            if (typeof void null !== typeof _name && null !== _name) {
                _$vt.find('.data-row .textvar-name').val(_name);
            }
            if (typeof void null !== typeof _val && null !== _val) {
                _$vt.find('.data-row .textvar-value').val(_val);
            }
            _$listBox.append(_$vt);
        };

        _this.remVar = function(_click_trgt){
            var $btn, _$v;
            if (typeof void null != _click_trgt.target && null != _click_trgt.target) {
                $btn = $(_click_trgt.target);  // для jquery 3.6.0 при событии click
            } else {
                $btn = $(_click_trgt);  // для старого jquery 1.12.4 при событии click
            }
            _$v = $btn.parents('.text-var:first');
            _$v.remove();
        };

        _this.loadVars = function(_vars, _vals) {
            var ix, cnt, _use_vals, _n, _v;
            _this.clearVars(); // очищаем блок
            if (typeof [] != typeof _vars) { return; }
            cnt = _vars.length;
            if(0 == cnt) { return; }
            _use_vals = false;
            if(typeof [] == typeof _vals && 0 < _vals.length) {
                _use_vals = true;
            }
            for(ix=0;ix<cnt;ix++){
                _v = '';
                _n = _vars[ix];
                if(_use_vals && ix < _vals.length) {
                    _v = _vals[ix]
                }
                _this.addVar(_n, _v);
            }
        };

        _this.getVars = function() {
            var _$listBox, _vars;
            //  получить контейнер
            _$listBox = _this.getVarsListBox();
            _vars = {};
            _$listBox.find('.text-var').each(function(){
                var _n, _v;
                _n = $(this).find('.data-row .textvar-name').val();
                _v = $(this).find('.data-row .textvar-value').val();
                _vars[_n] = _v;
            });
            return _vars;
        };

        function __getVarTemplate() {
            var _t, _$vb, _$labelsRow, _$dataRow;

            _$vb = $('<div class="text-var"></div>');
            _$vb.html('<table><tbody></tbody></table>');
            // строка описания
            _$labelsRow = $('<tr class="labels-row"></tr>');
            _$labelsRow.append('<td></td>');
            _$labelsRow.append('<td>&nbsp;&nbsp;&nbsp;Имя</td>');
            _$labelsRow.append('<td>Значениe</td>');
            _$vb.find('tbody').append(_$labelsRow);
            // сктрока элементов для ввода данных
            _$dataRow = $('<tr class="data-row"></tr>');
            _$dataRow.append('<td><span class="ui-state-default ui-corner-all remove-btn" title="Удалить"><span class="ui-icon ui-icon-trash"></span></span>&nbsp;</td>');
            _$dataRow.append('<td>#{<input class="ui-widget ui-state-default ui-corner-all textvar-name" value="" />}</td>');
            _$dataRow.append('<td>:&nbsp;<input class="ui-widget ui-state-default ui-corner-all textvar-value" value="" /></td>');
            _$vb.find('tbody').append(_$dataRow);

            _t = _$vb;
            return _t;
        }

        function _getAddVarDialogTmpl(){
            var t = '',
            selectFiles = 'Выберите архив (zip) с темой',
            maxFileSizeLbl = 'Максимальный размер файла',
            maxFileSize = '2M',
            maxFilesUploadLbl = 'Максимальное количество файлов',
            maxFilesUpload = '20',
            upload = 'Загрузить';
            t += '<form name="FMFilesForm" onsubmit="return false;" action="" target="'+_cookFilesUploadIframe()+'" method="post" enctype="multipart/form-data">';
            t += '<label>'+selectFiles+':</label>&nbsp;';
            t += '<input type="file" multiple="false" name="File" value="" />';
//            t += '<br /><span>'+maxFileSizeLbl+': '+maxFileSize+'</span>';
            t += '<br /><button name="Upload">'+ upload+'</button>';
            t += '</form>';
            return t;
        }

        _this._box = $('#page-content-marker').parent();
        // $('#vars-toolbar .action-btn').button();

    };

    if ('object' === typeof win && 'object' === typeof win.document) {
        win['_clsTextEditVars'] = _clsTextEditVars;
    }
}(window));