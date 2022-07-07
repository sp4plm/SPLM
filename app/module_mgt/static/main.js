if(typeof void null!=typeof jQuery){
    (function($){
        var _$box, _baseURL, _jsdata, _$grid, $jqTbl,
            dialog,
            _tbID = 'modules-register-box'
            _tID = 'modules-list-reg';


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
            if(typeof void null!=typeof dialog){
                dialog.close();
            }
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

        function _clickTableToolbar($btn) {
            var act, msg;
            act = $btn.attr('action');
            switch(act) {
                case 'install':

                    break;
              }
        }

        function cookRowToolbar(){
            var tb = '';
            // форму редактироваНия оставляем только для данных, для назначения карты
            tb += '<span class="ui-corner-all toolbar-btn" action="disable"><span class="ui-icon ui-icon-pencil"></span></span>';
            tb += '<span class="ui-corner-all toolbar-btn" action="drop_data"><span class="ui-icon ui-icon-pencil"></span></span>';
            tb += '<span class="ui-corner-all toolbar-btn" action="drop_conf"><span class="ui-icon ui-icon-pencil"></span></span>';
            tb += '<span class="ui-corner-all toolbar-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></span>';
            return tb;
        }

        function custRToolbar(cellvalue, options, rowObject){
            return cookRowToolbar();
        }

        function custModLink(cellvalue, options, rowObject){
            var _a;
            _a = String(cellvalue)
            return _a;
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
                case 'disable':

                    break;
                case 'drop_data':

                    break;
                case 'drop_conf':

                    break;
                case 'remove':
                    // удаляем файл/директорию
                    if ('Да' == row.IsDefault) {
                        alert('Нельзя удалить встроенный модуль!');
                        break;
                    }
                    msg = 'Вы действительно хотите удалить модуль - ' + row.Name +'?';
                    if(confirm(msg)){
                        //_removeModule(row);
                    }
                    break;
            }
        }

        function _cookToolbar(){
            var $tb = _getGridToolBarEl(),
                lbl1 = 'Установить';
            // кнопка "загрузить файл(ы)"
            $tb.append('<span class="ui-corner-all toolbar-btn" action="install"><span class="text">'+lbl1+'</span></span>');

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


        if(0 < $('#'+_tbID).length){
            _jsdata = JSON.parse($('#'+_tbID).find('.json-source:first').html());
            // если передали имя переменой
            if (typeof "z" === typeof _jsdata) {
                _jsdata = window[_jsdata];
            }
            if (typeof void null != typeof _jsdata['colModel']){
                // считаем что таблица получилась
                _jsdata['pager'] =  _tID+'-pager';

                $jqTbl = $('<table></table>');
                $('#'+_tbID).append($jqTbl);
                $('#'+_tbID).append('<div id="' + _jsdata['pager'] + '"></div>');
                $jqTbl.attr('id', _tID);

                //  делаем ссылку на модуль
                _jsdata['colModel'][0]['formatter'] = custModLink;
                // Навесить события на тулбаре в каждой строке
                /*
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
                */

                _$grid = $jqTbl.jqGrid(_jsdata);
                // добавляем поиск по колонкам
                $jqTbl.jqGrid('filterToolbar',{searchOperators : true});
                // добавляем пагинатор
                $jqTbl.jqGrid('navGrid','#' + _jsdata['pager'],{edit:false,add:false,del:false});
                //_cookToolbar();
            }

        }
        _$box.find('iframe[name="FMIFrameHelper"]').on('load', function(){
            _FMIFrameHelperLoaded({iframe:$(this)});
        });
    })(jQuery);
}else{
    alert('module_mgt/main.js say: jQuery is not loaded');
}