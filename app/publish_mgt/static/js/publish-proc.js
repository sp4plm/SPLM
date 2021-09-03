if(typeof void null!=typeof jQuery){
    (function($){
        var cfgObj, dialog, _$box,
            _baseURL = '/publisher',
            _wait_proc_int=0,
            _process_data = {},
            _iterTriggerOuter = null,
            _stopTriggerOuter = null,
            publishProcProxy = null,
            // переменую оставляем для упрощения переноса кода
            _$lastOpenDlg = null;

            _$box = $('.maincontent:first');

        function _checkProcDone() {
            var flg;
            flg = false;
            if (typeof void null !== typeof _process_data['process']['Done']
                && null != _process_data['process']['Done']){
                flg = Boolean(_process_data['process']['Done']);
            }
            return flg;
        }

        function publishProcessStep() {
            // надо запросить список для загрузки на сервере
            var url;
            url = _baseURL + '/publish_proc/step';
            $.post(url, null, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        _process_data = answ.Data;
                        if(typeof function(){} == typeof _iterTriggerOuter) {
                            _iterTriggerOuter(_process_data);
                        }
                        if(0< $('center#mark-publish-proc-page').length){
                            _updateIterationInfo(_process_data);
                        }
                        if (_checkProcDone()) {
                            // сбрасываем интервал опроса сервера о процессе
                            _processIterationStop();
                            // запускаем функцию завершения
                            publishProcessDone();
                        }
                    } else {
                        alert(answ.Msg);
                        if (501 == answ.State || 302 == answ.State){
                            // сбрасываем интервал опроса сервера о процессе
                            _processIterationStop();
                            // аварийное завершение публикации
                            publishProcessStop();
                        }
                    }
                } else {
                    // надо понять останавливаться или игнорировать??
                    alert('Неизвестная ошибка на сервере!');
                }
            }, 'json');
        }

        function publishProcessStop() {
            // надо запросить список для загрузки на сервере
            var url;
            url = _baseURL + '/publish_proc/error_break';
            $.post(url, null, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (typeof '' == typeof answ.Msg){
                        alert(answ.Msg);
                        // если мы находимся на странице информации о публикации
                        if(0< $('center#mark-publish-proc-page').length){
                            window.location = '/'; // принудительно отправляемся на главную страницу
                        }
                        if(typeof function(){} == typeof _stopTriggerOuter) {
                            _stopTriggerOuter(_process_data);
                        }
                    }
                } else {
                    alert('Неизвестная ошибка на сервере!');
                }
            }, 'json');
        }

        function publishProcessDone() {
            // надо запросить список для загрузки на сервере
            var url;
            url = _baseURL + '/publish_proc/done';
            $.post(url, null, function(answ){
                if (typeof void null !== typeof answ && null != answ){
                    if (200 == answ.State){
                        // надо проверить - если страница отображения процесса
                        // то перенаправляем на главную - наверно || настройки
                        // перенаправляем на главную странцу
                        alert('Процесс публикации завершен!');
                        // если мы находимся на странице информации о публикации
                        if(0< $('center#mark-publish-proc-page').length){
                            window.location = '/'; // принудительно отправляемся на главную страницу
                        }

                        if(typeof function(){} == typeof _stopTriggerOuter) {
                            _stopTriggerOuter(_process_data);
                        }
                    } else {
                        // перезапускаем процесс "тика"
                        _processIterationStart()
                        alert(answ.Msg);
                    }
                } else {
                    alert('Неизвестная ошибка на сервере!');
                }
            }, 'json');
        }

        function _processIterationStop() {
            clearInterval(_wait_proc_int)
        }

        function _processIterationStart() {
            _wait_proc_int=setInterval(publishProcessStep, 20000); // каждые двадцать секунд
        }

        function _getPublishDialogTmpl(){
            var t = '',
            nameFile = 'Выберите онтологии для конвертирования',
            lbl1 = 'Файл онтологии',
            lbl2 = 'Файл онтологии единиц измерений',
            actBtnLbl = 'Запустить публикацию';
            t += '<form name="FMFileForm" onsubmit="return false;" action="" target="'+cookFilesUploadIframe()+'" method="post" >';
            t += '<label>'+ nameFile+':</label>&nbsp;';
            t += '<br /><label>'+ lbl1 +':</label>&nbsp;';
            t += '<select name="UseOnto"></select><br />';
            t += '<br /><label>'+ lbl2 +':</label>&nbsp;';
            t += '<select name="UseUnitsOnto"></select><br />';
            //t += '<input type="checkbox" name="dropStorage" value="1" /><label>Очистить хранилище перед загрузкой</label><br />';
            t += '<br /><button name="StartPublish">'+ actBtnLbl+'</button>';
            t += '</form>';
            return t;
        }

        function _getPublishProcDialogTmpl(){
            var t = '',
            lbl1 = 'Файлов данных',
            lbl2 = 'Файлов для конвертации',
            lbl3 = 'Файлов для загрузки';
            t += '<table id="publish-proc-table">';
            t += '<tbody>';
            t += '<tr>';
            t += '<td class="data-label">' + lbl1 + ':&nbsp;</td>';
            t += '<td id="data-files-cnt" class="data-box"></td>';
            t += '</tr>';
            t += '<tr>';
            t += '<td class="data-label">' + lbl2 + ':&nbsp;</td>';
            t += '<td id="conv-files-cnt" class="data-box"></td>';
            t += '</tr>';
            t += '<tr>';
            t += '<td class="data-label">' + lbl3 + ':&nbsp;</td>';
            t += '<td id="upload-files-cnt" class="data-box"></td>';
            t += '</tr>';
            t += '</tbody>';
            t += '</table>';
            return t;
        }

        publishProcProxy = function() {
            var _cls = function() {
                var _this = this;

                _this.startIteration = function() {
                    _processIterationStart();
                    _$lastOpenDlg = $('center#mark-publish-proc-page');
                    //
                    if(_$lastOpenDlg.length>0) {
                        _$lastOpenDlg.find('#publish-proc-table .data-box').each(function(){
                            $(this).html(_getPubProcCounterTPL());
                            $(this).find('.total-cnt').html('-');
                            $(this).find('.current-cnt').html('-');
                        });
                    }
                };

                _this.setStopProcessTrigger = function(funcTrigger) {
                    _stopTriggerOuter = funcTrigger;
                };

                _this.setIterProcessTrigger = function(funcTrigger) {
                    _iterTriggerOuter = funcTrigger;
                };

                _this.getTemplate = function(tplName) {
                    if ('startDialog') {
                        return _getPublishDialogTmpl();
                    }
                    if ('procDialog') {
                        return _getPublishProcDialogTmpl();
                    }
                    return '<div></div>';
                };
            };
            return _cls
        }();

        function _updateIterationInfo(stateData) {
            _setDatafilesCount(stateData['work_files']['total']);
            _updateDatafilesCount(stateData['work_files']['done']);
            _setConvfilesCount(stateData['converted_files']['total']);
            _updateConvfilesCount(stateData['converted_files']['done']);
            _setUploadfilesCount(stateData['upload_files']['total']);
            _updateUploadfilesCount(stateData['upload_files']['done']);
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

        function _setDatafilesCount(num){
            _updatePubDlgData('#data-files-cnt .total-cnt', num);
        }

        function _updateDatafilesCount(num){
            _updatePubDlgData('#data-files-cnt .current-cnt', num);
        }

        function _setConvfilesCount(num){
            _updatePubDlgData('#conv-files-cnt .total-cnt', num);
        }

        function _updateConvfilesCount(num){
            _updatePubDlgData('#conv-files-cnt .current-cnt', num);
        }

        function _setUploadfilesCount(num){
            _updatePubDlgData('#upload-files-cnt .total-cnt', num);
        }

        function _updateUploadfilesCount(num){
            _updatePubDlgData('#upload-files-cnt .current-cnt', num);
        }

        if (typeof window.WFM === 'object' && typeof window.document === 'object' && window.WFM != null) {
            if (null !=publishProcProxy && 'function' === typeof publishProcProxy) {
                window.WFM['publishProcProxy'] = publishProcProxy;
            } else {
                alert('publishProcProxy is null or is not a function');
            }
        } else {
            alert('No mount point for _drv');
        }

    })(jQuery);
}else{
    alert('data_operator.js say: jQuery is not loaded');
}