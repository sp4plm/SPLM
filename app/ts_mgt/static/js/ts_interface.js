(function(win,undefined){
    var _clsTSInterface,
        tsIFace,
        blockVars,
        blockTextEdit,
        blockResults,
        blockHistory;

    _clsTSInterface = function() {
        var _this = this;

        _this._editor = null;
        _this._base_url = '';
        _this._$box = null;
        _this._queryStopWords = ['DELETE', 'INSERT', 'delete', 'insert'];

        _this.getCurrentText = function() {
            var _txt;
            if(typeof void null != typeof _this._editor && null != _this._editor) {
                _txt = _this._editor.getValue();
            }
            return _txt;
        };

        _this.getCurrentVariables = function() {
            var _vars;
            _vars = {};
            if (typeof void null != blockVars && null != blockVars) {
                _vars = blockVars.getVars();
            }
            return _vars;
        };

        function __checkQuery(_txt) {
            // требуется оставить выполнение только двух типов запросов: SELECT и CONSTRUCT
            var _flg, _stops, _cnt, _ix;
            _flg = true;
            _stops = _this._queryStopWords;
            _cnt = _stops.length;
            for(_ix=0;_ix<_cnt;_ix++){
                if(__hasWord(_stops[_ix], _txt)) {
                    _flg = false;
                    break;
                }
            }
            return _flg;
        }

        function __hasWord(_target, _source) {
            var _flg;
            _flg = false;
            _flg = _source.split(' ').some(function(w){return w === _target})
            return _flg;
        }

        function __compileQueryText(_txt, _vars) {
            var _qtxt,
                _vStart, _vEnd,
                ix, cnt, ix2, cnt2,
                _lines, _cLine, _cVar;
            _vStart = '#{';
            _vEnd = '}';
            _qtxt = '';
            _lines = _txt.split(_vStart);
            cnt = _lines.length;
            if(1<cnt) {
                for(ix=1;ix<cnt;ix++) {
                    _cVar = '';
                    _cLine = _lines[ix];
                    cnt2 = _cLine.length;
                    for(ix2=0; ix2<cnt2;ix2++){
                        if(_cLine[ix2] == _vEnd) {
                            break;
                        }
                        _cVar += _cLine[ix2];
                    }
                    if( _cVar in _vars &&
                        (typeof "" == typeof _vars[_cVar] || typeof "" == typeof _vars[_cVar])) {
                        _lines[ix] = _vars[_cVar] + _cLine.substr(ix2+1);
                    }
                }
                _qtxt = _lines.join('');
            } else {
                _qtxt = _txt;
            }
            return _qtxt;
        }

        function _sendQuery(){
            var _text, _vars, _sendQueryT, _history, _varsDump, _v,
                _textVars, _kv, _ep;
            // сперва получим текст запроса
            _text = _this.getCurrentText();

            if('' == _text) {
                alert('Отсутствует текст запроса!');
                return;
            }

            // надо получить переменные из запроса
            _textVars = __getVarsFromQuery(_text); // массив одноуровневый
            _vars = _this.getCurrentVariables(); // ассоциативный массив с ключами

            if (_vars) {
                for(_kv in _vars) {
                    if(typeof 'z' != typeof _kv || '' == _kv ){
                        alert('Не указано имя переменной!');
                        return;
                    }
                    if(typeof void null == typeof _vars[_kv] || null == _vars[_kv] || '' == _vars[_kv] ){
                        alert('Не указано значение переменной ' + _kv + '!');
                        return;
                    }
                }
            }
            // теперь сравнить с переменными из блока
            if (_textVars) {
                for(_kv in _textVars) {
                    if(typeof 'z' !== typeof _textVars[_kv] || '' === _textVars[_kv] ){
                        alert('В тексте запроса присутствует безымянная переменная!');
                        return;
                    }
                    if(typeof void null == typeof _vars[_textVars[_kv]] || null == _vars[_textVars[_kv]]){
                        alert('В тексте запроса присутствует переменная ' + _textVars[_kv] + ' не указанная в блоке переменных!');
                        return;
                    }
                }
            }

            // сформируем данные для истории
            _history = [];
            _history.push(_text);
            _history.push(_vars);

            // заменим метки переменных на значения из блока переменных
            _sendQueryT = __compileQueryText(_text, _vars);

            // требуется убедиться что запрос либо SELECT, либо CONSTRUCT
            // иначе щговорим об ошибке !!!
            if (!__checkQuery(_sendQueryT)) {
                alert('Запрос содержит одно из недопустимых слов: ' + _this._queryStopWords.join(', '));
                return; // выходим
            }
            _ep = $('#request-point').val();
            if('-1' == _ep) {
                alert('Не выбран репозиторий для выполнения запроса!');
                return; // выходим
            }
            // передаем запрос блоку результата
            // блок результата либо создает и отображает таблицу с результатом, либо отображает сообщение об ошибке
            if (typeof void null != blockResults && null != blockResults) {
                blockResults.execQuery(_sendQueryT, _ep);
            }
            //  блок истории
            if (typeof void null != blockHistory && null != blockHistory) {
                blockHistory.addQuery(_text, _vars);
            }
        }

        function _clearQueryText(){
            if(typeof void null != typeof _this._editor && null != _this._editor) {
                _this._editor.setValue('');
            }
            if (typeof void null != blockResults && null != blockResults) {
                // blockResults.clearResult(); ???
            }
        }

        function _clearVariables(){
            if (typeof void null != blockVars && null != blockVars) {
                blockVars.clearVars();
            }
        }

        function _removeVariable(){
            if (typeof void null != blockVars && null != blockVars) {
                blockVars.remVar();
            }
        }

        function _addVariable(){
            if (typeof void null != blockVars && null != blockVars) {
                blockVars.addVar();
            }
        }

        function _addVariables(){}

        function _loadVariables(_vars){
            if (typeof void null != blockVars && null != blockVars) {
                blockVars.loadVars(_vars);
            }
        }

        function _loadVariablesFromText() {
            var _text, _vars;
            _text = '';
            _vars = [];
            _text = _this.getCurrentText();
            if(typeof '' == typeof _text && 0 < _text.length) {
                _vars = __getVarsFromQuery(_text);
            }
            _loadVariables(_vars);
        }

        function _selectQuery(){}

        function _loadResults() {}

        function _ev_changeEditor(delta) {
            // delta.start, delta.end, delta.lines, delta.action
            var _text, _vars, ix, _t;
            _text = '';
            switch(delta.action) {
                case "insert":
                    // разбираем текст на переменные
                    if (0 < delta.lines.length) {
                        _text = delta.lines.join("\n");
                        _vars = __getVarsFromQuery(_text);
                        _t = '';
                        for(ix=0;ix<_vars.length;ix++){
                            _t += _vars[ix] + ' | ';
                        }
                         // alert('Variables: ' + _t); // работает - TODO: add to variables block
                        _loadVariables(_vars);
                    }
                    break;
                case "remove":
                    // удаяем переменные если все удалили
                    break;
            }
        }

        _this.setTextEditor = function(_editor) {
            _this._editor = _editor;
            // _this._editor.on('change', _ev_changeEditor);
        };

        _this.__buttons_click = function(_act, $btn) {
            var msg;
            if($btn.hasClass('disabled-btn')) {
                return;
            }
            // pre event
            switch(_act) {
                case 'clear-vars':
                    _clearVariables();
                    break;
                case 'add-var':
                    _addVariable();
                    break;
                case 'rem-var':
                    _removeVariable();
                    break;
                case "load-from-text":
                    _loadVariablesFromText();
                    break;
                case 'send-query':
                    _sendQuery();
                    break;
                case 'clear-text':
                    _clearQueryText();
                    break;
            }
            // post event
        };

        _this.__eventBus = function(_evName, _evData) {
            var _2arr;
            _2arr = [[], []]; // чтобы не было ошибок
            // требуется для передачи переменных в виде двух массивов
            function _object2array(_obj) {
                var _res, _t, _k, _v;
                _res = [];
                _k = [];
                _v = [];
                if(typeof void null != typeof _obj && null != _obj) {
                    for(_t in _obj) {
                        if(typeof 'z' != typeof _t) { continue; }
                        _k.push(_t);
                        _v.push(_obj[_t]);
                    }
                }
                _res.push(_k);
                _res.push(_v);
                return _res;
            }

            switch(_evName) {
                case 'HistorySelectQuery':
                    _this._editor.setValue(_evData['text']);
                    if (typeof void null != blockVars && null != blockVars) {
                        _2arr = _object2array(_evData['vars']);
                        blockVars.loadVars(_2arr[0], _2arr[1]);
                    }
                    break;
                case 'HistorySelectQueryText':
                    _this._editor.setValue(_evData);
                    break;
                case 'HistorySelectQueryVars':
                    if (typeof void null != blockVars && null != blockVars) {
                        _2arr = _object2array(_evData);
                        blockVars.loadVars(_2arr[0], _2arr[1]);
                    }
                    break;
                default:
                    break;
            }
        };

        _this.getEventBus = function() {
            return _this.__eventBus;
        };

        _this._$box = $('#page-content-marker').parent();
        _this._base_url = $('#js-base-url').val();
        // $('#query-toolbar .action-btn').button();

    };

    function __getVarsFromQuery(_txt) {
        var _vStart, _vEnd, _lines, _vars,
            ix, cnt, ix2, cnt2, _cLine,
            _cVar;
        _vStart = '#{';
        _vEnd = '}';
        _vars = [];
        _lines = _txt.split(_vStart);
        cnt = _lines.length;
        ix=0;
        // требуется пропускать первую строку так как делим началом переменной
        for(ix=1;ix<cnt;ix++) {
            _cVar = '';
            _cLine = _lines[ix];
            cnt2 = _cLine.length;
            for(ix2=0; ix2<cnt2;ix2++){
                if(_cLine[ix2] == _vEnd) {
                    break;
                }
                _cVar += _cLine[ix2];
            }
            if(-1 == _vars.indexOf(_cVar)){
                _vars.push(_cVar);
            }
        }
        return _vars
    }

    function _toggleSection(_click_trgt){
        /**
        Функция исключительно для работы из интерфейс пользователя - по нажатию на иконку скрывает или отображает
        содержимое секции
        */
        var $btn, _$sec, _$sc;
        if (typeof void null != _click_trgt.target && null != _click_trgt.target) {
            $btn = $(_click_trgt.target);  // для jquery 3.6.0 при событии click
        } else {
            $btn = $(_click_trgt);  // для старого jquery 1.12.4 при событии click
        }
        _$sec = $btn.parents('.content-section:first');
        if($btn.hasClass('xicon-open')){
            _$sec.find('.content-section-content').hide();
            $btn.addClass('xicon-close');
            $btn.removeClass('xicon-open');
        } else {
            _$sec.find('.content-section-content').show();
            $btn.addClass('xicon-open');
            $btn.removeClass('xicon-close');
        }
    }

    // button event clicker
    function __click_on_button(_btn) {
        var act, msg, $btn;
        if (typeof void null != _btn.target && null != _btn.target) {
            $btn = $(_btn.target);  // для jquery 3.6.0 при событии click
        } else {
            $btn = $(_btn);  // для старого jquery 1.12.4 при событии click
        }
        act = $btn.attr('act');
        if($btn.hasClass('disabled-btn')) {
            return;
        }
        if($btn.prop('disabled')) {
            return;
        }
        tsIFace.__buttons_click(act, $btn);
    }

    /* блок инициализации всей функциональности интерфейса { */
    tsIFace = new _clsTSInterface();
    // инициализация редактора текста запроса
    tsIFace.setTextEditor(QueryTextEditor);
    // инициализация блока переменных
    blockVars = new _clsTextEditVars(tsIFace.getEventBus());
    // инициализация блока результата
    blockResults = new  _clsQueryResult($('#query-result'), tsIFace.getEventBus());
    // инициализация блока истории запросов
    blockHistory = new _clsQueryHistory($('#query-history'), tsIFace.getEventBus());
    // инициализация функциальности интерфейса - связывание всех функциальностей
    // click edit vars
    $('button.action-btn').on('click', __click_on_button);
//    $('button.action-btn').click(__click_on_button);
    $('span.header-section-toggler').on('click', _toggleSection);
    if (typeof void null != blockHistory && null != blockHistory) {
        blockHistory.onLoad();
    }
    /* блок инициализации всей функциональности интерфейса } */

    if ('object' === typeof win && 'object' === typeof win.document) {
        win['_tsIFace'] = tsIFace;
    }

    // требуется выполнить тестирование TS Endpoint

}(window));