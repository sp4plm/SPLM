(function(win,undefined){
    var _clsQueryHistory;

    _clsQueryHistory = function(conta, _eventBus) {
        var _this = this;

        _this._$box = null;
        _this._base_url = '';
        _this._section_head = 'content-section-header';
        _this._section_conte = 'content-section-content';
        _this._section_toggler = 'header-section-toggler';
        // register classes
        _this._row_cls = 'query-history';
        _this._hact_cls = 'history-act';
        _this._qtime_cls = 'query-time';
        _this._qcell_cls = 'query-text';
        _this._vcell_cls = 'query-vars';
        _this._qact_cls = 'query-acts';

        _this._storeKey = '';
        _this._register = null;
        _this._exists = [];
        _this._lastItem = null;
        _this._$table = null;
        _this._tableTpl = '';
        //  сейчас исполняемый запрос
        _this._lastRow = {'$': null, 'query': '', 'vars': null, 'start': 0, 'stop': 0, '_key_': null};
        _this._$mountPoint = null; // ссылка на tbody

        _this._addRow = function() {
            var _vHtml, _qHtml, _$r, _qtime, _rI, _oldQ;

            _vHtml = _vars2html(_this._lastRow['vars']);
            _qHtml = _query2html(_this._lastRow['query']);
            _qtime = new Date(_this._lastRow['start']);
            //теперь требуется создать строку с данными запроса
            if(-1 < _this._exists.indexOf(_this._lastRow['_key_'])) {
                // надо удалить имеющуюся запись из html таблицы
                _oldQ = _getItem(_this._lastRow['_key_']);
                $('#tq_' + _oldQ['start']).remove();
            }
            _this._lastRow['$'] = _this._addHtmlRow(_qHtml, _vHtml, _this._lastRow['start']);

            // добавим в реестер
            _rI = {'query': '', 'vars': null, 'start': 0, 'stop': 0, '_key_': null};
            _rI['query'] = _this._lastRow['query'];
            _rI['vars'] = _this._lastRow['vars'];
            _rI['start'] = _this._lastRow['start'];
            _rI['_key_'] = _this._lastRow['_key_'];
            _addItem(_rI);
            // теперь сохраняем в реестре
            if(-1 == _this._exists.indexOf(_this._lastRow['_key_'])) {
                _this._exists.push(_this._lastRow['_key_']);
            }
        };

        _this._addHtmlRow = function(_q, _vars, _time){
            var _$r, _btnRem, _btnLoad, _btnLoadQ, _btnLoadV, _manStr, _f_time;

            _f_time = new Date(_time);
            _$r = $('<tr class="' + _this._row_cls + '" id="tq_' + _time + '"></tr>');
            // добавляем ячейку с кнопкой удаление из истории
            _btnRem = '<span class="ui-corner-all history-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></span>';
            _btnRem = '<button class="ui-button ui-corner-all ui-widget history-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></button>';
            _$r.append('<td class="' + _this._hact_cls + '">' + _btnRem + '</td>');
            // добавляем ячейку датой старта запроса
            _$r.append('<td class="' + _this._qtime_cls + '">' + _f_time + '</td>');
            // добавляем ячейку с текстом запроса
            _$r.append('<td class="' + _this._qcell_cls + '">' + _q + '</td>');
            // добавляем ячейку с переменными запроса
            _$r.append('<td class="' + _this._vcell_cls + '">' + _vars + '</td>');
            // добавляем ячейку с кнопками управления
            _manStr = '';
            _btnLoad = '<button class="history-btn" action="load">Загрузить все</button>';
            _btnLoadQ = '<button class="history-btn" action="load_query">Загрузить запрос</button>';
            _btnLoadV = '<button class="history-btn" action="load_vars">Загрузить переменные</button>';
            _manStr = _btnLoad + '<hr />' + _btnLoadQ + '<hr />' + _btnLoadV;
            _$r.append('<td class="' + _this._qact_cls + '">' + _manStr + '</td>');
            // теперь вставляем в html документ
            _this._$mountPoint.prepend(_$r.get(0));
            // теперь назначим обработчики событий
            _$r.find('.history-btn').each(function(){
                // $(this).button();
                $(this).on('click', _this.buttonEvents);
            });
            return _$r;
        };

        _this._createTable = function() {
            var _$c,_$st, _tTpl;
            // сохранить в стек запросе
            // требуется создать таблицу с оформлением
            // отобразить запрос первой строкой таблицы
            _$c = _getSectionContent();
            _tTpl = _getTableTpl();
            _this._$table = $(_tTpl);
            _$c.append(_this._$table);
            _this._$mountPoint = _this._$table.find('tbody:first');
        };

        _this._createToolbar = function() {
            var _$c, _$t, _btnClear;
            _$c = _getSectionContent();
            _$t = $('<div id="history-toolbar"></div>');
            _btnClear = '<button class="history-btn" action="clear_history">Очистить историю</button>';
            _$t.append(_btnClear);
            _$c.append(_$t);
            _$t.find('.history-btn').each(function(){
                $(this).on('click', _this.buttonEvents);
                // $(this).button();
            });
        };

        _this._clearTable = function() {
            _this._$table.find('tbody:first tr').each(function(){ $(this).remove(); });
        };

        _this._removeRow = function(t,q,v) {
        };

        _this.tableExists = function() { return null !== _this._$table && 0 < _this._$table.length; }

        _this.getStoreKey = function() { return _this._storeKey; }

        _this.clearHistory = function(){
            if(!_this.tableExists()) { return ; }
            _this._clearTable();
            if(0 == _this._register.length) { return ; }
            _dropRegister();
        };

        _this.__getQDataByClick = function(_clkTarget) {
            var _res, _$tr, _qt, _qv, _rid;
            _res = {'query': '', 'vars': null, '_key_': ''};

            _$tr = $(_clkTarget).parents('tr:first');
            _rid = _$tr.attr('id');
            _qt = _$tr.find('.'+ _this._qcell_cls).html();
            _qv = _$tr.find('.'+ _this._vcell_cls).html();
            // получаем текст запроса и переменные
            _res['query'] = _htmlQ2Query(_qt);
            _res['vars'] = _htmlV2Vars(_qv);
            // получаем хэш
            _res['_key_'] = _getQueryHash(_res['query'], _res['vars']);

            return _res;
        };

        _this.removeQuery = function(_btn){
            var _$tr, _qO, _rData;

            _rData = _this.__getQDataByClick(_btn);
            _qO = null;
            _$tr = $(_btn).parents('tr:first');
            //alert('removeQuery.chatchHash -> ' + _rData['_key_']);
            try {
                _qO = _getItem(_rData['_key_']);
            } catch(_ex) {
                _qO = null;
            }
            //alert('removeQuery.catchTime -> ' + _qO['start']);
            // удаляем строку из таблицы
            // перед удалением хорошо бы снять события со всех кнопок в строке
            // проверяем есть ли в реестре запись с таким хэшем - если есть удаляем
            if(null != _qO) {
                _$tr.remove();
                _removeItem(_rData['_key_']);
            }
        };

        _this.loadQuery = function(_btn){
            var _$tr, _qO, _rData, _res;

            _rData = _this.__getQDataByClick(_btn);
            _qO = null;
            _res = null;
            _$tr = $(_btn).parents('tr:first');
            try {
                _qO = _getItem(_rData['_key_']);
            } catch(_ex) {
                _qO = null;
            }
            if(null != _qO) {
                _res = {'text': _qO['query'], 'vars': _qO['vars']};
            }
            // теперь требуется вызвать событие в интерфейсе
            _eventBus('HistorySelectQuery', _res);
        };

        _this.loadOnlyQuery = function(_btn){
            var _$tr, _qO, _rData, _res;

            _rData = _this.__getQDataByClick(_btn);
            _qO = null;
            _res = null;
            _$tr = $(_btn).parents('tr:first');
            try {
                _qO = _getItem(_rData['_key_']);
            } catch(_ex) {
                _qO = null;
            }
            if(null != _qO) {
                _res = _qO['query']
            }
            // теперь требуется вызвать событие в интерфейсе
            _eventBus('HistorySelectQueryText', _res);
        };

        _this.loadOnlyVars = function(_btn){
            var _$tr, _qO, _rData, _res;

            _rData = _this.__getQDataByClick(_btn);
            _qO = null;
            _res = null;
            _$tr = $(_btn).parents('tr:first');
            //alert('removeQuery.chatchHash -> ' + _rData['_key_']);
            try {
                _qO = _getItem(_rData['_key_']);
            } catch(_ex) {
                _qO = null;
            }
            if(null != _qO) {
                _res = _qO['vars'];
            }
            // теперь требуется вызвать событие в интерфейсе
            _eventBus('HistorySelectQueryVars', _res);
        };

        _this.buttonEvents = function(_click_trgt){
            var _ev, _btn, $btn;
            if (typeof void null != _click_trgt.target && null != _click_trgt.target) {
                $btn = $(_click_trgt.target);  // для jquery 3.6.0 при событии click
            } else {
                $btn = $(_click_trgt);  // для старого jquery 1.12.4 при событии click
            }
            _ev = $btn.attr('action');
            try {
                __historyEvents(_ev, $btn.get(0));
            } catch(_ex) {
                alert('Непредвиденная ошибка при обработке события - ' + _ev + '!');
            }
        };

        // Utils

        function __historyEvents(_evName, _evTarget) {
            switch(_evName) {
                case 'clear_history':
                    // удаляем все запросы из: html таблицы, реестра и локального харнилища
                    _this.clearHistory();
                    break;
                case 'remove':
                    // удаляем запрос из: html таблицы, реестра и локального харнилища
                    _this.removeQuery(_evTarget);
                    break;
                case 'load':
                    // загружаем текст запроса в поле текстового редактора и переменные в блок переменных
                    _this.loadQuery(_evTarget);
                    break;
                case 'load_vars':
                    // загружаем переменные в блок переменных
                    _this.loadOnlyVars(_evTarget);
                    break;
                case 'load_query':
                    // загружаем текст запроса в поле текстового редактора
                    _this.loadOnlyQuery(_evTarget);
                    break;
            }
        }

        // { localStorage
        function __storageExists() {
            var _flg;
            _flg = false;
            if ('' === _this._storeKey) {
                return _flg;
            }
            _flg = (null !== window.localStorage.getItem(_this._storeKey));
            return _flg;
        }

        function __readFromStorage() {
            var _d, _sd;
            if (!__storageExists()) { return null; }
            _sd = window.localStorage.getItem(_this._storeKey);
            if('[object Object]' == _sd) {
                _sd = '[]';
            }
            if('' != _sd) {
                _d = JSON.parse(_sd);
            } else {
                _d = [];
            }
            return _d;
        }

        function __loadFromStorage() {
            if (!__storageExists()) { return false; }
            _this._register = __readFromStorage();
            return true;
        }

        function __dump2Storage() {
            if(!_existsRegister()) { return false; }
            window.localStorage.setItem(_this._storeKey, JSON.stringify(_this._register));
            return true;
        }

        function __clearStorage() {
            if (!__storageExists()) { return false; }
            window.localStorage.removeItem(_this._storeKey);
            return true;
        }
        // } localStorage

        // { Register

        function _existsRegister() {
            return null !== _this._register;
        }

        function _initRegister() {
            if(!_existsRegister()) {
                _this._register = [];
            }
        }

        function _addItem(_item) {
            _initRegister();
            if(-1 < _this._exists.indexOf(_item['_key_'])) {
                // надо удалить имеющуюся запись
                _removeItem(_item['_key_']);
            }
            _this._register.push(_item)
            __dump2Storage();
        }

        function _removeItem(_key) {
            var _flg, _qI;
            _flg = false;
            _qI = __catchItem(_key);
            if (_qI > -1) {
                _this._register.splice(_qI, 1);
                _flg = true;
                __dump2Storage();
            }
            return _flg;
        }

        function __catchItem(_key) {
            var _cnt, _ix, _res;
            _cnt = _this._register.length;
            _res = -1;
            if(0 < _cnt) {
                for(_ix = 0;_ix<_cnt;_ix++) {
                    if(_key == _this._register[_ix]['_key_']) {
                        _res = _ix;
                        break;
                    }
                }
            }
            return _res;
        }

        function _getItem(_key) {
            var _q, _qI;
            _q = null;
            _qI = __catchItem(_key);
            if (_qI > -1) {
                _q = _this._register[_qI];
            }
            return _q;
        }

        function _dropRegister() {
            _this._register = [];
            __dump2Storage();
        }
        // } Register

        function __getStoreKey() {
            if('' === _this._storeKey) {
                _this._storeKey = __getSessionKey();
                if('' === _this._storeKey) {
                    _this._storeKey = __getUrlKey();
                }
            }
            return _this._storeKey;
        }

        function __getUrlKey() {
            var _loc;
            _loc = window.location.host;
            return __genHash(_loc);
        }

        function __getSessionKey() {
            var _key;
            _key = document.cookie || '';
            return _key;
        }

        function _getTableTpl() {
            if('' == _this._tableTpl) {
                _this._tableTpl = '<table border="1">';
                _this._tableTpl += '<thead>';
                _this._tableTpl += '<tr>';
                _this._tableTpl += '<th>Удалить</th>';
                _this._tableTpl += '<th>Дата выполнения</th>';
                _this._tableTpl += '<th>Текст запроса</th>';
                _this._tableTpl += '<th>Переменные</th>';
                _this._tableTpl += '<th>Действия</th>';
                _this._tableTpl += '</tr>';
                _this._tableTpl += '</thead>';
                _this._tableTpl += '<tbody></tbody>';
                _this._tableTpl += '</table>';
            }
            return _this._tableTpl;
        }

        function _vars2html(_vars) {
            var _html, _v;
             _html = '<ul>';
            for(_v in _vars) {
                _html += '<li>';
                _html += _var2html(_v, _vars[_v]);
                _html += '</li>';
            }
            _html += '</ul>';
            return _html;
        }

        function _vars2str(_vars) {
            var _str, _v;
            _str = '';
            for(_v in _vars) {
                _str += '' + _v + ':' + _vars[_v];
            }
            return _str;
        }

        function _var2html(_n, _v) {
            var _html;
            _html = "" + _n + ":&nbsp;" + _escapeHtml(_v);
            return _html;
        }

        function _htmlV2Vars(_htmlV) {
            var _line, _v, _q$;
            _v = {};
            $(_htmlV).find('li').each(function(){
                var _t;
                _line = $(this).html();
                _t = _line.split(':&nbsp;');
                _t[1] = _t[1].replace('&lt;', '<');
                _t[1] = _t[1].replace('&gt;', '>');
                _v[_t[0]] = _t[1];
            });
            return _v;
        }

        function _htmlQ2Query(_htmlQ) {
            var _q;
            _q = $(_htmlQ).html();
            _q = _q.replace('&lt;', '<');
            _q = _q.replace('&gt;', '>');
            return _q;
        }

        function _query2html(_txt) {
            var _html;
            _html = '<pre>' + _escapeHtml(_txt) + '</pre>';
            return _html;
        }

        function _query2str(_txt) {
            var _str;
            _str = _txt.replace("\n", 'NL');
            _str = _str.replace(" ", '');
            return _str;
        }

        function _escapeHtml(_s) {
            var _r;
            _r = _s.replace('<', '&lt;');
            _r = _r.replace('>', '&gt;');
            return _r;
        }

        function _getItemTpl() {
            return {'text': '', 'vars': {}}
        }

        function _getSectionHeader() {
            return _this._$box.find('.' + _this._section_head + ':first');
        }

        function _getSectionContent() {
            return _this._$box.find('.' + _this._section_conte + ':first');
        }

        function _getSectionToggler() {
            var _$h;
            _$h = _getSectionHeader();
            return _$h.find('.' + _this._section_toggler + ':first')
        }

        function _toggleSectionContent(){
            var _$st;
            _$st = _getSectionToggler();
            _$st.trigger('click');
        }

        function _showSection() {
            var _$c,_$st;
            _$st = _getSectionToggler();
            _$c = _getSectionContent();
            if(_$st.hasClass('xicon-close')){
                _$c.show();
                _$st.addClass('xicon-open');
                _$st.removeClass('xicon-close');
            }
        }

        function _hideSection() {
            var _$c,_$st;
            _$st = _getSectionToggler();
            _$c = _getSectionContent();
            if(_$st.hasClass('xicon-open')){
                _$c.hide();
                _$st.addClass('xicon-close');
                _$st.removeClass('xicon-open');
            }
        }

        function __genHash(_base){
            var _hash, _digits;
            _digits = _base.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0);
            if (0 > _digits) {
                _digits = -1 * _digits;
            }
            _hash = _digits.toString(16).toUpperCase();
            if (0 > _digits) {
                _hash = '0' + _hash;
            }
            return _hash;
        }

        function _getQueryHash(_qtxt, _vars) {
            var _base, _h1, _h2;

            _base = 'my SPARQL query with vars!';

            _base = '' + _vars2str(_vars) + _query2str(_qtxt) ;
            _h1 = __genHash(_base);
            return _h1;
        }


        // API
        /**
            Метод добавляет запрос в историю
        */
        _this.addQuery = function(_qtxt, _vars) {
            var _$c,_$st, _$tbl, _vHtml, _qHtml, _$r, _qtime, _h;

            _h = _getQueryHash(_qtxt, _vars);
            _qtime = new Date();

            _this._lastRow['_key_'] = _h;
            _this._lastRow['vars'] = _vars;
            _this._lastRow['query'] = _qtxt;
            _this._lastRow['start'] = _qtime.getTime();
            _showSection();
            // требуется создать таблицу с оформлением
            // отобразить запрос первой строкой таблицы

            // проверить существование таблицы - реестра запросов
            if(!_this.tableExists()) {
                _this._createTable();
            }

            // сохранить в реестр запрос
            _this._addRow(_qtxt, _vars);
        };

        /**
            Метод-событие вызывается нажатием на текст запроса, вызывает загрузку текста запроса и переменные
            (при наличии) в редактор
        */
        _this.selectQuery = function(_clkTarget) {};

        /**
            Метод должен вызываться при загрузке интерфейса для отображения сохраненных запросов (? на клиенте?)
        */
        _this.onLoad = function(){
            var _storeKey, _inStore, _t,
                _cnt, _ix, _$r;
            _storeKey = __getStoreKey(); // получаем ключ для данных

            if(!_this.tableExists()) {
                // надо добавить тулбар
                _this._createToolbar();
                _this._createTable();
            }

            //  проверяем доступно ли хранилище в браузере
            if(__storageExists()) {
                // если данные есть до выбираем их
                // и заполняем таблицу на странице
                _inStore = __readFromStorage();
                if (typeof [] !== typeof _inStore) {
                    __clearStorage();
                    _inStore = [];
                }else{
                    __loadFromStorage();
                    _inStore = _this._register;
                }
                _cnt = _inStore.length;
                if(0 < _cnt) {
                    // сортируем по времени выполнения - так чтобы самый старый запрос был первым
                    _inStore.sort(function(a, b){
                        return a.start - b.start;
                    });

                    for(_ix=0;_ix<_cnt;_ix++) {
                        _t = _inStore[_ix];
                        _this._exists.push(_t['_key_']);
                        // при добавлении на страницу запрос вставляется перед вставленным
                        _vHtml = _vars2html(_t['vars']);
                        _qHtml = _query2html(_t['query']);
                        _qtime = new Date(_t['start']);
                        _$r = _this._addHtmlRow(_qHtml, _vHtml, _t['start']);
                    }
                    _showSection();
                }
            }else{
                //  чистка мусора
                try{
                    _inStore = __readFromStorage();
                    if (typeof [] !== typeof _inStore) {
                        __clearStorage();
                    }
                }catch(ex){
                    // no actions
                }
            }

        };

        // constructor actions
        _this._$box = $(conta);
        _this._base_url = $('#js-base-url').val();
        _hideSection();
    };

    try {

    } catch(e) {
        alert(e);
    }
    if ('object' === typeof win && 'object' === typeof win.document) {
        win['_clsQueryHistory'] = _clsQueryHistory;
    }
}(window));