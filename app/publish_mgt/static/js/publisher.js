if(typeof void null!=typeof jQuery){
    (function($){
        var _$grid,
            cfgObj, $jqTbl, dialog, _$box,
            _tasksDlgClose = [],
            _workDir = '',
            _media_path = '',
            _baseURL = '/publisher',
            _gridID = 'list-operational-data',
            _data_files = [],
            _ttl_files = [],
            _current_xi =-1,
            _current_xi1 =-1,
            _useOnto='',
            _useUnitsOnto='',
            _threadsNum = 10,
            _procsFilesStart=false,
            _procsFilesDone=false,
            _uploadResultsStart=false,
            _uploadResultsDone=false,
            _count_proc_files=0,
            _wait_proc_int=0,
            _$lastOpenDlg = null,
            _files2convert=null,
            _publishProcProxy=null,
            _convertedFiles=0,
            _existedFiles=[],
            _existedFilesIdx = 0,
            _$existedFilesBox=null,
            _useMaster = false;
        
        _$box = $('.maincontent:first');

        function getGridToolBarEl(){
            return $('#t_'+_gridID);
        }

        function execDlgTasks()
        {
            var cnt, idx, _f;
            cnt = _tasksDlgClose.length;
            idx = 0;
            if (0 < cnt) {
                _f = function(){};
                for(idx=0;idx<cnt;idx++) {
                    if (typeof _f == typeof _tasksDlgClose[idx]) {
                        _tasksDlgClose[idx]();
                    }
                }
                for(idx=0;idx<cnt;idx++) {
                    _tasksDlgClose[idx] = null;
                }
                _tasksDlgClose = [];
            }
        }

        function clickTableToolbar($btn) {
            var act, msg;
            act = $btn.attr('action');
            switch(act) {
                case 'groupDelete':
                    msg = 'Вы действительно хотите удалить выделенные строки?';
                    if(confirm(msg)){
                        deleteSelectedItems();
                    }
                    break;
                case 'addfiles':
                    // открываем окно для загрузки файла(ов)
                    dialog.open(getFilesDialogTmpl(),function($box){
                        _$lastOpenDlg = $box;
                        $box.find('button[name="Upload"]').click(function(){
                            uploadFiles($(this).parent());
                        });
                    });
                    break;
              }
        }

        function cookToolbar(){
            var $tb = getGridToolBarEl(),
                lbl2 = 'Загрузить файлы',
                lbl3 = 'Удалить';
            $tb.append('<span class="ui-corner-all toolbar-btn" action="groupDelete" disabled="true"><span class="text">'+lbl3+'</span></span>');
            $tb.append('<span class="toolbar-delim"></span>');
            // кнопка "загрузить файл(ы)"
            if ('backups' != _workDir) {
                $tb.append('<span class="ui-corner-all toolbar-btn" action="addfiles"><span class="text">'+lbl2+'</span></span>');
            }

            $tb.find('.toolbar-btn').click(function(){ 
                clickTableToolbar($(this));
            });
            // блокируем кнопку группового удаления
            $tb.find('toolbar-btn[action="groupDelete"]').prop('disabled', true);
        }

        function cookRowToolbar(){
            var tb = '';
            tb += '<input type="checkbox" class="toolbar-row-selector" name="RowSelector[]" />';
            tb += '<span class="toolbar-delim"></span>';
            tb += '<span class="ui-corner-all toolbar-btn" action="open"><span class="ui-icon ui-icon-folder-open"></span></span>';
            // форму редактироваНия оставляем только для данных, для назначения карты
            if ('backups' == _workDir) {
                tb += '<span class="ui-corner-all toolbar-btn" action="rollback"><span class="ui-icon ui-icon-arrowreturnthick-1-w"></span></span>';
            }
            tb += '<span class="ui-corner-all toolbar-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></span>';
            return tb;
        }
        
        function custRToolbar(cellvalue, options, rowObject){
            return cookRowToolbar();
        }

        function uploadFiles($form){
            var url = _baseURL+'/loadFiles';
            if(''!==_workDir){
                url += '/'+_workDir;
            }
            // сперва надо добавить информацию о директории
            $form.attr('onsubmit','');
            $form.removeAttr('onsubmit');
            $form.attr('action',url);
            $form.trigger('submit');
        }

        function downloadFile(data) {
            var $a, href, filename, sendDir,
                 url = _baseURL + '/downloadFile';
            
            sendDir = _workDir;
            filename = data.Name;

            if(''!==sendDir){
                url += '/'+sendDir;
            }
            href = url + '?file=' + filename;

            $a = $('<a></a>');
            $a.html(filename);
            $a.css("display", "none");
            $('body').append($a);
            $a.attr('target', "_blank");
            $a.attr('href', href);
            //$a.trigger('click');
            $a[0].click();
            $a.remove();
        }

        function removeFile(data){
            var url = _baseURL + '/removeFile';
            if(''!==_workDir){
                url += '/'+_workDir;
            }

            if ('media' == _workDir) {
                url += '?base='+workDir4url(_media_path);
            }
            $.post(url,{file:data.Name},function(rfA){
                if(rfA.State==200){
                    delRow(data.rowID);
                }else{
                    alert(rfA.Msg);
                }
            },'json');
        }

        function clearData(){
            if(typeof void null!==typeof _$grid && null!==_$grid){
                _$grid.clearGridData();
            }
        }

        function getRowData(rID){
            if(typeof void null!=typeof rID && null!==rID){
                return _$grid.getRowData(rID);
            }else{
                return _$grid.getRowData();
            }
        }

        function delRow(rID){
            var t;
            if(typeof void null!=typeof rID && null!==rID){
                _$grid.delRowData(rID);
                // надо проверить если строка была последней, но надо перезагрузить таблицу
                t = getRowData();
                if(0===t.length){
                    reload();
                }
            }else{
                clearData();
            }
        }

        function reload(){
            if(typeof void null!==typeof _$grid && null!==_$grid){
                _$grid.trigger('reloadGrid');
            }
        }

        function getSelectedRows(){
            var rows = [];
            _$grid.find('tr input.toolbar-row-selector:checked').each(function(){
                var row = {},rID = $(this).parent().parent().attr('id');
                row = getRowData(rID);
                rows.push(row);
            });
            return rows;
        }

        function deleteSelectedItems(){
            var url = _baseURL + '/removeSelection',
                selRows = getSelectedRows(),
                cnt=selRows.length,kx=0,
                data = {items:[]};
            if(''!==_workDir){
                url += '/'+_workDir;
            }
            if ('media' == _workDir) {
                data['base'] = _media_path;
            }
            for(kx=0;kx<cnt;kx++){
                data.items.push(selRows[kx].Name);
            }
            $.post(url,data,function(riA){
                if(riA.State==200){
                    reload();
                }else{
                    alert(riA.Msg);
                }
            },'json');
        }

        dialog = function(k){
            var _cls = function(p){
                var _1this = this,
                _$dlg=null,
                _$parent;
                _1this.id = '';
                _1this.id = p.id;
                
                _1this.build = function(){
                    if(0==_$parent.find('#'+_1this.id).length){
                        _$dlg = $('<div></div>');
                        _$dlg.attr('id',_1this.id);
                        //                    _$dlg.hide();
                        _$parent.append(_$dlg);
                    }
                    _$dlg = _$dlg.dialog({
                        title:'',
                        autoOpen: false,
                        modal: false,
                        open:function(){ 
                            //_EvMan.fire('FMDialogOpen',{content:$(this),_skey:_selfCode}); 
                        },
                        beforeClose:function(){ 
                            //_EvMan.fire('FMDialogBeforeClose',{content:$(this),_skey:_selfCode}); 
                        },
                        close:function(){ 
                            //_EvMan.fire('FMDialogClose',{content:$(this),_skey:_selfCode});
                        }
                    });
                };
                _1this.destroy = function(){
                    if(typeof void null!=typeof _$dlg && null!==_$dlg){
                        _$dlg.dialog('destroy');
                    }
                };
                _1this.clearContent=function(){
                    if(typeof void null!=typeof _$dlg && null!==_$dlg){
                        _$dlg.html('');
                    }
                };
                _1this.open = function(tmpl,cB){
                    if(_$dlg.dialog('isOpen')){
                        //_1this.close();
                    }
                    _1this.clearContent();
                    _$dlg.html(tmpl);
                    if(typeof function(){} === typeof cB){
                        cB(_$dlg);
                    }
                    _$dlg.dialog('open');
                };
                _1this.close = function(){
                    if(_$dlg.dialog('isOpen')){
                        _$dlg.dialog('close');
                    }
                    execDlgTasks();
                };
                _1this.init = function(){
                    _$parent = _$box;
                    _1this.build();
                };
                
                function _c(){
                    _1this.id = p.id;
                }
                _c();
            };
            return new _cls(k);
        }({id:'pf-dialog'});
        /* uiDialog для работы с формами в диалогах */
        
        
        function cookFilesUploadIframe(){
            var name = 'FMIFrameHelper', $frm, _to;
            if(0===_$box.find('iframe[name="'+name+'"]').length){
                $frm = $('<iframe name="FMIFrameHelper" style="display:none;width:0px;height:0px;"></iframe>');
                _$box.append($frm);
                $frm.attr('name', name);
                _to = setTimeout(function(){
                    _$box.find('iframe[name="'+name+'"]').on('load', function(){
                        FMIFrameHelperLoaded({iframe:$(this)});
                    });
                    clearTimeout(_to);
                }, 1000);
            }
            return name;
        }

        function FMIFrameHelperLoaded(p){
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
            reload();
            dialog.close();
            if(typeof void null!=typeof answer_json.Msg) {
                if('' != answer_json.Msg){
                    alert(answer_json.Msg);
                }
            }
            if(typeof void null!=typeof answer_json.Existed) {
                if(typeof [] == typeof answer_json.Existed){
                    // запускаем процедуру процедуру по обработке созданных файлов
                    processExistedFiles(answer_json.Existed);
                }
            }
        }

        function processExistedFiles(fileList) {
            var cnt, ix, $td, $tr, num;
            _existedFiles = [];
            _existedFiles = fileList
            cnt = _existedFiles.length;
            if (0 < cnt) {
                _$existedFilesBox = null;
                _existedFilesIdx = -1; // при увеличении станет первым индексом
                // запускаем диалог об разруливании созданных файлов
                dialog.open(getExistedFilesDialogTmpl(_useMaster),function($box){
                    _$existedFilesBox = $box;
                    $box.find('#existed-total').html(cnt);
                    // инициализируем события на кнопках
                    $box.find('#existed-accept').on('click', saveNewFile);
                    $box.find('#existed-reject').on('click', saveExistFile);
                    if(!_useMaster) {
                        // требуется заполнить таблицу именами файлов дубликатов
                        for(ix=0;ix<cnt;ix++){
                            $td = $('<td colspan="2"></td>');
                            $tr = $('<tr></tr>');
                            $tr.append($td);
                            $box.find('#existed-files-table tbody').append($tr);
                            num = ix+1
                            $td.html(num.toString() + '.&nbsp;' + _existedFiles[ix][0])
                        }
                    }
                });
                if(_useMaster) {
                    processExistFile();
                }
            }
        }

        function processExistFile(){
            var current,cnt;
            cnt = _existedFiles.length;
            _existedFilesIdx++;
            if (_existedFilesIdx < cnt) {
                current = _existedFiles[_existedFilesIdx];
                _$existedFilesBox.find('#current-exist-id').val(_existedFilesIdx);
                _$existedFilesBox.find('#existed-number').html(_existedFilesIdx+1);
                _$existedFilesBox.find('#existed-current-name').html(current[0]);
            } else {
                reload();
                dialog.close();
            }
        }

        function existsToggleControls(enable) {
            if(enable){
                _$existedFilesBox.find('#existed-accept').prop('disabled', false);
                _$existedFilesBox.find('#existed-accept').removeProp('disabled');
                _$existedFilesBox.find('#existed-reject').prop('disabled', false);
                _$existedFilesBox.find('#existed-reject').removeProp('disabled');
                _$existedFilesBox.find('#apply-4-all').prop('disabled', false);
                _$existedFilesBox.find('#apply-4-all').removeProp('disabled');
            } else {
                _$existedFilesBox.find('#existed-accept').prop('disabled', true);
                _$existedFilesBox.find('#existed-reject').prop('disabled', true);
                _$existedFilesBox.find('#apply-4-all').prop('disabled', true);
            }
        }

        function saveNewFile(){
            var url, sendData;
            existsToggleControls(false);
            url = _baseURL + '/accept_newfile';
            if(''!==_workDir){
                url += '/'+_workDir;
            }
            if(_$existedFilesBox.find('#apply-4-all').prop('checked')) {
                sendData = _existedFiles;
            }else{
                sendData = [];
                sendData.push(_existedFiles[_existedFilesIdx]);
            }
            $.post(url, {'exfiles': sendData}, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        if(_useMaster) {
                            processExistFile();
                        } else {
                            reload();
                            dialog.close();
                        }
                    } else {
                        alert(answ.Msg);
                    }
                } else {
                    alert(answ.Msg);
                }
                existsToggleControls(true);
            }, 'json');
        }

        function saveExistFile(){
            var url, sendData;
            existsToggleControls(false);
            url = _baseURL + '/reject_newfile';
            if(''!==_workDir){
                url += '/'+_workDir;
            }
            if(_$existedFilesBox.find('#apply-4-all').prop('checked')) {
                sendData = _existedFiles;
            }else{
                sendData = [];
                sendData.push(_existedFiles[_existedFilesIdx]);
            }
            $.post(url, {'exfiles': sendData}, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        if(_useMaster) {
                            processExistFile();
                        } else {
                            reload();
                            dialog.close();
                        }
                    } else {
                        alert(answ.Msg);
                    }
                } else {
                    alert(answ.Msg);
                }
                existsToggleControls(true);
            }, 'json');
        }

        function getExistedFilesDialogTmpl(useMaster){
            var t = '';
            if(typeof true != typeof useMaster) {
                useMaster = false;
            }
            t += '<form name="FMExistedFilesForm" onsubmit="return false;">';
            t += '<table id="existed-files-table">';
            t += '<tbody>';
            t += '<tr>';
            t += '<td style="line-height:20px;font-weight:bold;">Всего дубликатов:&nbsp;&nbsp;</td><td id="existed-total"></td>';
            t += '</tr>';
            if(useMaster) {
                t += '<tr>';
                t += '<td>Файл:<span id="existed-number"></span>.';
                t += '<input type="hidden" value="" name="CurrentExistsID" id="current-exist-id" />';
                t += '</td>';
                t += '<td id="existed-current-name"></td>';
                t += '</tr><tr>';
                t += '<td><button id="existed-accept">Заменить</button></td>';
                t += '<td><button id="existed-reject">Пропустить</button></td>';
                t += '</tr><tr>';
                t += '<td><input type="checkbox" value="1" name="Apply4All" id="apply-4-all" /></td>';
                t += '<td><label for="apply-4-all">Применить ко всем файлам</label></td>';
                t += '</tr>';
            }else{
                t += '<tr>';
                t += '<td colspan="2"><div><input type="checkbox" value="1" name="Apply4All" id="apply-4-all" checked="true" style="display:none;" /></div><hr /></td>';
                t += '</tr>';
                t += '<tr>';
                t += '<td align="right"><button id="existed-accept">Заменить</button></td>';
                t += '<td align="left"><button id="existed-reject">Пропустить</button></td>';
                t += '</tr>';
                t += '<tr>';
                t += '<td colspan="2" style="line-height:20px;font-weight:bold;">Перечень дубликатов:<br /></td>';
                t += '</tr>';
            }
            t += '</tbody>';
            t += '</table>';
            t += '</form>';
            return t;
        };
        
        function getFilesDialogTmpl(){
            var t = '',
            selectFiles = 'Выберите файлы',
            maxFileSizeLbl = 'Максимальный размер файла',
            maxFileSize = '2M',
            maxFilesUploadLbl = 'Максимальное количество файлов',
            maxFilesUpload = '20',
            upload = 'Загрузить';
            t += '<form name="FMFilesForm" onsubmit="return false;" action="" target="'+cookFilesUploadIframe()+'" method="post" enctype="multipart/form-data">';
            t += '<label>'+selectFiles+':</label>&nbsp;';
            t += '<input type="file" multiple="true" name="File[]" value="" />';
//            t += '<br /><span>'+maxFileSizeLbl+': '+maxFileSize+'</span>';
//            t += '<br /><span>'+maxFilesUploadLbl+': '+maxFilesUpload+'</span>';
            t += '<br /><button name="Upload">'+ upload+'</button>';
            t += '</form>';
            return t;
        }
        
        function getFileDialogTmpl(){
            var t = '',
            nameFile = 'Имя файла',
            file = 'файл',
            maxFileSizeLbl = 'Максимальный размер файла',
            maxFileSize = '2M',
            maxFilesUploadLbl = 'Максимальное количество файлов',
            maxFilesUpload = '20',
            upload = 'Загрузить';
            t += '<form name="FMFileForm" onsubmit="return false;" action="" target="'+cookFilesUploadIframe()+'" method="post" enctype="multipart/form-data">';
            t += '<label>'+ nameFile+':</label>&nbsp;';
            t += '<input type="text" name="FileName" value="" />';
            t += '<input type="hidden" name="OldName" value="" />';
            t += '<br /><label>'+ file.substr(0,1).toUpperCase()+file.substr(1)+':</label>&nbsp;';
            t += '<input type="file" name="File" value="" />';
//            t += '<br /><span>'+maxFileSizeLbl+': '+maxFileSize+'</span>';
//            t += '<br /><span>'+maxFilesUploadLbl+': '+maxFilesUpload+'</span>';
            t += '<br /><button name="Update">'+ upload+'</button>';
            t += '</form>';
            return t;
        }

        function getDataFileDialogTmpl(){
            var t = '',
            nameFile = 'Выберите карту для',
            actBtnLbl = 'Установить';
            t += '<form name="FMFileForm" onsubmit="return false;" action="" target="'+cookFilesUploadIframe()+'" method="post" >';
            t += '<label>'+ nameFile+'&nbsp;<b class="file-name-select-map"></b>:</label>&nbsp;';
            t += '<input type="hidden" name="FileName" value="" />';
            t += '<br /><button name="SetMap">'+ actBtnLbl+'</button>';
            t += '</form>';
            return t;
        }

        function getPublishProcDialogTmpl(){
            var t = '',
            lbl3 = 'Файлов для загрузки';
            t += '<table id="publish-proc-table">';
            t += '<tbody>';
            t += '<tr>';
            t += '<td class="data-label">' + lbl3 + ':&nbsp;</td>';
            t += '<td id="upload-files-cnt" class="data-box"></td>';
            t += '</tr>';
            t += '</tbody>';
            t += '</table>';
            return t;
        }

        function gridRowToolbarEvCatcher(p){
    //       p=> {action:'', rowID:'' }
            var type,row, url, filename, msg;
            //alert('called gridRowToolbarEvCatcher');
            row = getRowData(p.rowID);
            row['rowID'] = p.rowID;
            type = row['Type']; // f - is a file, d - is a directory
            //alert('gridRowToolbarEvCatcher -> ' + p.action);
            switch(p.action){
                case 'open':
                    // если файл то даем скачать
                    downloadFile(row);
                    break;
                case 'edit':
                    dialog.open(getFileDialogTmpl(),function($box){
                            $box.find('input[name="FileName"]').val(row.Name);
                            $box.find('input[name="OldName"]').val(row.Name);
                            $box.find('button[name="Update"]').click(function(){ editFile($(this).parent(),row); });
                        });
                    break;
                case 'remove':
                    // удаляем файл/директорию
                    msg = 'Вы действительно хотите удалить - ' + row.Name +'?';
                    if(confirm(msg)){
                        removeFile(row);
                    }
                    break;
                case 'rollback':
                    if (confirm('Действительно хотите восстановить данную резервную копию - ' + row.Name +'?')) {
                            rollbackBackup(row.Name);
                    }
                    break;
            }
        }
        function rollbackBackup(filename)
        {
            var url, backup;
            url = _baseURL + '/rollbackBackup';
            if(''!==_workDir){
                url += '/'+_workDir;
            }
            backup = false;
            $.post(url, {'bfile': filename}, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        if(answ.Msg) {
                            alert(answ.Msg);
                        } else {
                            alert('Данные восстановлены!');
                        }
                    } else {
                        alert(answ.Msg);
                    }
                } else {
                    alert(answ.Msg);
                }
                reload();
            }, 'json');
        }

        function toggleDirGridRowSelection(p){
            // {rowID:string,selected:boolean}
            // надо проверить есть ли выделенные строки
            var selRows = getSelectedRows(),cnt=selRows.length,
                $tB = getGridToolBarEl(),
                $btn = $tB.find('toolbar-btn[action="groupDelete"]');
            // если строки есть то разблокировать кнопку группового удаления
            if(0<cnt){
                $btn.prop('disabled',false);
                $btn.removeProp('disabled');
            }else{
                // если ниобной строки не отмечено кнопку надо заблокировать
                $btn.prop('disabled',true);
            }
        }

        function updatePublishTime()
        {
            if(0 < $('#last-publish').length) {
                $.get(_baseURL + '/getLastPublishTime', null, function(answ) {
                    if (typeof void null !== typeof answ && null != answ){
                        if (200 === answ.State){
                            $('#last-publish').html(answ.publish_time);
                        } 
                    }
                }, 'json');
            }
        }

        function updateBackupTime()
        {
            if(0 < $('#last-backup').length) {
                $.get(_baseURL + '/getLastBackupTime', null, function(answ) {
                    if (typeof void null !== typeof answ && null != answ){
                        if (200 === answ.State){
                            $('#last-backup').html(answ.backup_time);
                        } 
                    }
                }, 'json');
            }
        }

        function backupData()
        {
            var url,
            $btn;

            $btn = $(this);
            url = _baseURL + '/backupData';
            $btn.prop('disabled', true);
            $.get(url, null, function(answ) {
                $btn.prop('disabled', false);
                $btn.removeProp('disabled');
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        alert('Резервная копия создана');
                        // теперь обновим время создания резервной копии
                    } else {
                        alert(answ.Msg);
                    }
                } else {
                    alert(answ.Msg);
                }
                reload();
            }, 'json');
        }

        function openPublishProcDialog() {
            _$lastOpenDlg = null;
            dialog.open(getPublishProcDialogTmpl(),function($box){
                _$lastOpenDlg = $box;
                $box.find('#publish-proc-table .data-box').each(function(){
                    $(this).html(_getPubProcCounterTPL());
                    $(this).find('.total-cnt').html('-');
                    $(this).find('.current-cnt').html('-');
                });
                if(null != _publishProcProxy) {
                    try {
                        _publishProcProxy.startIteration();
                    } catch(ex) {
                        alert('Не удалось запустить обновление информации о публикации. Ошибка: ' + ex.name + ":" + ex.message);
                    }
                }
            });
        }

        function _getPubProcCounterTPL() {
            var t;
            t = '<span class="current-cnt"></span>&nbsp;из&nbsp;<span></span><span class="total-cnt"></span>';
            return t;
        }

        function _updatePubDlgData(key, data){
            if(null == _$lastOpenDlg) {
                return;
            }
            _$lastOpenDlg.find(key).html('' + data);
        }

        function setDatafilesCount(num){
            _updatePubDlgData('#data-files-cnt .total-cnt', num);
        }

        function updateDatafilesCount(num){
            _updatePubDlgData('#data-files-cnt .current-cnt', num);
        }

        function setConvfilesCount(num){
            _updatePubDlgData('#conv-files-cnt .total-cnt', num);
        }

        function updateConvfilesCount(num){
            _updatePubDlgData('#conv-files-cnt .current-cnt', num);
        }

        function setUploadfilesCount(num){
            _updatePubDlgData('#upload-files-cnt .total-cnt', num);
        }

        function updateUploadfilesCount(num){
            _updatePubDlgData('#upload-files-cnt .current-cnt', num);
        }

        function iterationTrigger(stateData) {
            setDatafilesCount(stateData['work_files']['total']);
            updateDatafilesCount(stateData['work_files']['done']);
            setConvfilesCount(stateData['converted_files']['total']);
            updateConvfilesCount(stateData['converted_files']['done']);
            setUploadfilesCount(stateData['upload_files']['total']);
            updateUploadfilesCount(stateData['upload_files']['done']);
        }

        function stopTrigger(stateData) {
            publisingDoneTrigger();
        }

        function startPublish2($form){
            var url;
            url = _baseURL+'/publish';
            // сперва надо добавить информацию о директории
            $('#publicaator').prop('disabled', true);
            $.post(url, {}, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        openPublishProcDialog(); // открываем диалог с информацией о процессе публикации
                    } else {
                        alert(answ.Msg);
                    }
                } else {
                    alert('Неизвестная ошибка на сервере!');
                }
            }, 'json');
        }

        /********** Публикация файлов по очереди { */

        function publisingDoneTrigger(){
            updatePublishTime();
            FMIFrameHelperLoaded();
            $('#publicaator').prop('disabled', false);
            $('#publicaator').removeProp('disabled');
        }

        function getHashedLen(hashed) {
            var key, len;
            len = 0;
            for(key in hashed) {
                if (typeof void null == typeof key || null == key) { break; }
                len += 1;
            }
            return len;
        }

        function list2hashed(list, field='') {
            var cnt, xi, key,
                hashed = {};
            cnt = list.length;
            for(xi=0;xi<cnt;xi++) {
                key = 'field-' + parseStr(xi);
                if (typeof void null !== typeof list[xi][field]) {
                    key = list[xi][field]
                }
                hashed[key] = list[xi];
            }
            return hashed;
        }

        function searchFileIn(list, name) {
            var cnt, xi,
                flg = false;
            cnt = list.length;
            for(xi=0;xi<cnt;xi++) {
                if (list[xi]['name'] == name) {
                    flg = true;
                    break;
                }
            }
            return flg;
        }
        /********** Публикация файлов по очереди } */

        _$box = $('.maincontent:first');
        // считываем рабочуюю директорию
        _workDir = $('#files-cfg-tbl').parent().attr('dirname');
        if ('media' == _workDir){
            _media_path = _workDir;
            updatePathInformer();
        }
        // инициализация диалога для загрузки файлов
        dialog.init();
        // Note for future - изменение url и перезагрузка таблицы
        // jQuery("#list").jqGrid().setGridParam({url : 'newUrl'}).trigger("reloadGrid")
        // json config for the table
        cfgObj = JSON.parse($('#files-cfg-tbl').html());
        if (typeof void null != typeof cfgObj['colModel']){
            // считаем что таблица получилась
            // назначаем специализированный форматтер для  первой колонки
            cfgObj['colModel'][0]['formatter'] = custRToolbar;
            cfgObj['pager'] =  _gridID+'-pager';
            
            cfgObj['loadComplete'] = function(){
                $jqTbl.find('tr input.toolbar-row-selector').click(function(){
                    var rowID, selected;
                    rowID = $(this).parent().parent().attr('id');
                    selected = $(this).prop('checked');
                    toggleDirGridRowSelection({'rowID': rowID,'selected': selected});
                });
                $jqTbl.find('tr .toolbar-btn').click(function(){
                    var rowID, act;
                    rowID = $(this).parent().parent().attr('id');
                    act = $(this).attr('action');
                    //alert('called action -> ' + act);
                    gridRowToolbarEvCatcher({'rowID': rowID, 'action': act});
                });
            };

            $jqTbl = $('<table></table>');
            $('#files-cfg-tbl').parent().append($jqTbl);
            $('#files-cfg-tbl').parent().append('<div id="' + _gridID+'-pager"></div>');
            $jqTbl.attr('id', _gridID);
            _$grid = $jqTbl.jqGrid(cfgObj);
            // добавляем поиск по колонкам
            $jqTbl.jqGrid('filterToolbar',{searchOperators : true});
            // добавляем пагинатор
            $jqTbl.jqGrid('navGrid','#'+_gridID+'-pager',{edit:false,add:false,del:false});
            // добавляем toolbar
            //$jqTbl.append("<input type='button' value='Click Me' style='height:20px;font-size:-3'/>");
            cookToolbar();

            _$box.find('iframe[name="FMIFrameHelper"]').on('load', function(){
                FMIFrameHelperLoaded({iframe:$(this)});
            });
        }

        if ('data' == _workDir) {
            if (typeof window.WFM === 'object' && typeof window.document === 'object' && window.WFM != null) {
                if (null !== window.WFM['publishProcProxy'] && 'function' == typeof window.WFM['publishProcProxy']) {
                    try {
                        _publishProcProxy = new window.WFM['publishProcProxy']();
                        _publishProcProxy.setIterProcessTrigger(iterationTrigger);
                        _publishProcProxy.setStopProcessTrigger(stopTrigger);
                    } catch(ex) {
                        alert('Не удалось инициализировать функциональность публикации. Ошибка: ' + ex.name + ":" + ex.message);
                    }
                }
            }
            $('#publicaator').click(startPublish2);
            updateBackupTime();
            updatePublishTime();
        }
        if ('backups' == _workDir) {
            $('#backupper').click(backupData);
        }
        
    })(jQuery);
}else{
    alert('publisher.js say: jQuery is not loaded');
}