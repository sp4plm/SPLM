if(typeof void null!=typeof jQuery){
    (function($){
        var _$box, _baseURL, _jsdata, _$grid, $jqTbl,
            dialog,
            _tID = 'themes-list-reg';


        function _FMIFrameHelperLoaded(p){
            var answer, answer_json;
            answer_json = {};
            if(typeof void null != typeof p){
                if(typeof void null != typeof p.iframe ){
                    answer = p.iframe.get(0).contentDocument.body.innerHTML;
                    if('' != answer) {
                        try {
                            answer_json = JSON.parse(answer);
                        }catch{
                            answer_json = {};
                            answer_json['Msg'] = 'Не удалось преобразовать в объект ответ сервера!';
                        }
                    }
                }
            }
            _reload();
            dialog.close();
            if(typeof void null!=typeof answer_json.Msg) {
                if('' != answer_json.Msg){
                    alert(answer_json.Msg);
                }
            }
        }


        function _cookFilesUploadIframe(){
            var name = 'FMIFrameHelper', $frm, _to;
            if(0===_$box.find('iframe[name="'+name+'"]').length){
                $frm = $('<iframe name="FMIFrameHelper" style="display:none;width:0px;height:0px;"></iframe>');
                _$box.append($frm);
                $frm.attr('name', name);
                _to = setTimeout(function(){
                    _$box.find('iframe[name="'+name+'"]').on('load', function(){
                        _FMIFrameHelperLoaded({iframe:$(this)});
                    });
                    clearTimeout(_to);
                }, 1000);
            }
            return name;
        }

        function _getFilesDialogTmpl(){
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

        function _getThemeDialogTmpl() {
            var t = '',
            nameFile = '',
            actBtnLbl = 'Сохранить';
            t += '<form name="FMFileForm" onsubmit="return false;" action="" target="'+_cookFilesUploadIframe()+'" method="post" >';
            t += '<label>'+ nameFile+'&nbsp;<b class="file-name-select-map"></b>:</label>&nbsp;';
            t += '<input type="hidden" name="ThemeName" value="" /><br /><br />';
            t += '<input type="checkbox" value="1" name="ActivateTheme" id="activate-theme" />&nbsp;&nbsp;';
            t += '<label for="activate-theme">Сделать активной?</label><br />';
            t += '<br /><button name="SetActive">'+ actBtnLbl+'</button>';
            t += '</form>';
            return t;
        }

        function _uploadFiles($form){
            var url = _baseURL+'/theme/upload';
            // сперва надо добавить информацию о директории
            $form.attr('onsubmit','');
            $form.removeAttr('onsubmit');
            $form.attr('action',url);
            $form.trigger('submit');
        }

        function _clickTableToolbar($btn) {
            var act, msg;
            act = $btn.attr('action');
            switch(act) {
                case 'addfiles':
                    // открываем окно для загрузки файла(ов)
                    dialog.open(_getFilesDialogTmpl(),function($box){
                        _$lastOpenDlg = $box;
                        $box.find('button[name="Upload"]').click(function(){
                            _uploadFiles($(this).parent());
                        });
                    });
                    break;
                case 'resetDefaults':
                    _resetDefaults();
                    break;
              }
        }

        function cookRowToolbar(){
            var tb = '';
            // форму редактироваНия оставляем только для данных, для назначения карты
            tb += '<span class="ui-corner-all toolbar-btn" action="edit"><span class="ui-icon ui-icon-pencil"></span></span>';
            tb += '<span class="ui-corner-all toolbar-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></span>';
            return tb;
        }

        function custRToolbar(cellvalue, options, rowObject){
            return cookRowToolbar();
        }

        function _gridRowToolbarEvCatcher(p){
    //       p=> {action:'', rowID:'' }
            var type,row, url, filename, msg;
            //alert('called gridRowToolbarEvCatcher');
            row = _getRowData(p.rowID);
            row['rowID'] = p.rowID;
            type = row['Type']; // f - is a file, d - is a directory
            //alert('gridRowToolbarEvCatcher -> ' + p.action);
            switch(p.action){
                case 'open':
                   // будем формировать архивный файл и отдавать на скачивание
                   _downloadTheme(row);
                    break;
                case 'edit':
                    dialog.open(_getThemeDialogTmpl(),function($box){
                        $box.find('input[name="ThemeName"]').val(row.Name);
                        $box.find('b.file-name-select-map').html(row.Name);
                        if ('Да' == row.Enabled) {
                            $box.find('input[name="ActivateTheme"]').prop('checked', true);
                        }
                        $box.find('button[name="SetActive"]').click(function(){ _setActiveTheme($(this).parent(),row); });
                    });

                    break;
                case 'remove':
                    // удаляем файл/директорию
                    if ('Да' == row.Enabled) {
                        alert('Нельзя удалить, используемую порталом, тему!');
                        break;
                    }
                    msg = 'Вы действительно хотите удалить тему- ' + row.Name +'?';
                    if(confirm(msg)){
                        _removeTheme(row);
                    }
                    break;
            }
        }

        function _setActiveTheme($form,data){
            var url = _baseURL+'/theme/set';
            // сперва надо добавить информацию о директории
            $form.attr('onsubmit','');
            $form.removeAttr('onsubmit');
            $form.attr('action',url);
            $form.trigger('submit');
        }

        function _downloadTheme(rowData) {}

        function _removeTheme(rowData) {
            var url = _baseURL + '/theme/remove';
            $.post(url,{'ThemeName':rowData.Name},function(rfA){
                if(rfA.State==200){
                    _delRow(rowData.rowID);
                }else{
                    alert(rfA.Msg);
                }
            },'json');
        }

        function _resetDefaults() {
            var url = _baseURL + '/reset';
            $.get(url, {},function(rfA){
                alert(rfA.Msg);
                _reload();
            },'json');
        }

        function _cookToolbar(){
            var $tb = _getGridToolBarEl(),
                lbl1 = 'Загрузить',
                lbl2 = 'Обновить преднастроенные темы';
            // кнопка "загрузить файл(ы)"
            $tb.append('<span class="ui-corner-all toolbar-btn" action="addfiles"><span class="text">'+lbl1+'</span></span>');
            $tb.append('<span class="ui-corner-all toolbar-btn" action="resetDefaults"><span class="text">'+lbl2+'</span></span>');

            $tb.find('.toolbar-btn').click(function(){
                _clickTableToolbar($(this));
            });
        }

        function _getGridToolBarEl(){
            return $('#t_'+_tID);
        }

        function _clearData(){
            if(typeof void null!==typeof _$grid && null!==_$grid){
                _$grid.clearGridData();
            }
        }

        function _getRowData(rID){
            if(typeof void null!=typeof rID && null!==rID){
                return _$grid.getRowData(rID);
            }else{
                return _$grid.getRowData();
            }
        }

        function _delRow(rID){
            var t;
            if(typeof void null!=typeof rID && null!==rID){
                _$grid.delRowData(rID);
                // надо проверить если строка была последней, но надо перезагрузить таблицу
                t = _getRowData();
                if(0===t.length){
                    _reload();
                }
            }else{
                _clearData();
            }
        }

        function _reload(){
            if(typeof void null!==typeof _$grid && null!==_$grid){
                _$grid.trigger('reloadGrid');
            }
        }

        _$box = $('#page-content-marker').parent();
        _baseURL = _$box.find('#js-base-url').val();

        dialog = new _jqDialog({'id':'themes-dlg','parent': _$box});
        dialog.init();

        if(0 < $('#themes-register-box').length){
            _jsdata = JSON.parse($('#themes-register-box').find('.json-source:first').html());
            // если передали имя переменой
            if (typeof "z" === typeof _jsdata) {
                _jsdata = window[_jsdata];
            }
            if (typeof void null != typeof _jsdata['colModel']){
                // считаем что таблица получилась
                _jsdata['pager'] =  _tID+'-pager';

                $jqTbl = $('<table></table>');
                $('#themes-register-box').append($jqTbl);
                $('#themes-register-box').append('<div id="' + _jsdata['pager'] + '"></div>');
                $jqTbl.attr('id', _tID);

                // Навесить события на тулбаре в каждой строке
                _jsdata['colModel'][0]['formatter'] = custRToolbar;
                _jsdata['loadComplete'] = function(){
                    $jqTbl.find('tr .toolbar-btn').click(function(){
                        var rowID, act;
                        rowID = $(this).parent().parent().attr('id');
                        act = $(this).attr('action');
                        //alert('called action -> ' + act);
                        _gridRowToolbarEvCatcher({'rowID': rowID, 'action': act});
                    });
                };

                _$grid = $jqTbl.jqGrid(_jsdata);
                // добавляем поиск по колонкам
                $jqTbl.jqGrid('filterToolbar',{searchOperators : false});
                // добавляем пагинатор
                $jqTbl.jqGrid('navGrid','#' + _jsdata['pager'],{edit:false,add:false,del:false});
                _cookToolbar();
            }

        }
        _$box.find('iframe[name="FMIFrameHelper"]').on('load', function(){
            _FMIFrameHelperLoaded({iframe:$(this)});
        });
    })(jQuery);
}else{
    alert('themes_mgt/main.js say: jQuery is not loaded');
}