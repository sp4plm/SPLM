(function(win,undefined){
    var _clsQueryResult;

    _clsQueryResult = function(conta, _eventBus) {
        var _this = this,
            _gridID = 'qrt';

        _this._$box = null;
        _this._base_url = '';
        _this._section_head = 'content-section-header';
        _this._section_conte = 'content-section-content';
        _this._section_toggler = 'header-section-toggler';
        _this.loadMarker = '/img/loader2.gif';
        _this.loaderBox = 'loader-status';

        _this._grid = null;
        _this._gridBoxCls = 'jqgrid-box',
        _this._gridCls = 'jqgrid-tbl',
        _this._gridPgCls = _this._gridCls+'-pg',
        _this._gridTBCls = _this._gridCls+'-tool',
        _this.gridBoxID = _gridID + '-gridbox';
        _this.gridID = _gridID+'-grid';
        _this.gridPgID = _gridID+'-grid-pg';
        _this._gridTpl = '';
        _this._errorBoxId = 'result-error-box';

        _this._currentQuery = '';
        _this._lastError = '';
        _this._lastData = null;
        _this._lastEP = '';
        _this._errorMsgTpl = '';

        // get request url

        function _exportData() {
            var _url, _sendData, href;
            _url = _this._base_url + '/man/api/exportQuery';
            _sendData = {};
            _sendData['q'] = _this._currentQuery;
            _sendData['ts'] = _this._lastEP;
            _sendData['fmt'] = 'xml';
            _this.showLoader();
            $.post(_url, _sendData, function(answ){
                // Ожидание answ = {'Data': [], 'Error': '', '?State': 0-1000, 'Msg':''}
                if(typeof void null != typeof answ && null != answ) {
                    try{
                        // получаем урл для скачивания файла
                        // подставляем
                        href = _this._base_url + '/man/download_exported/' + answ['Data'];
                        /***/
                        $a = $('<a></a>');
                        $a.html('ddd');
                        $a.css("display", "none");
                        $('body').append($a);
                        $a.attr('target', "_blank");
                        $a.attr('href', href);
                        //$a.trigger('click');
                        $a[0].click();
                        $a.remove();
                        _this.hideLoader();
                        /***/
                    }catch(_ex) {
                        alert('Ошибка при попытке скачать файл! Except: ' + _ex);
                    }
                } else {
                    alert('Неизвестная ошибка на сервере!');
                }
            }, 'json');
        }

        // send query with data to url
        function _sendQuery(_qText, _targetEP, _callback) {
            var _url, _sendData;
            _url = _this._base_url + '/man/api/sendQuery';
            _sendData = {};
            _sendData['q'] = _qText;
            _sendData['ts'] = _targetEP;
            $.post(_url, _sendData, function(answ){
                // Ожидание answ = {'Data': [], 'Error': '', '?State': 0-1000, 'Msg':''}
                if(typeof void null != typeof answ && null != answ) {
                    try{
                        _callback(answ);
                    }catch(_ex) {
                        alert('Исключение при попытке отобразить результат! Except: ' + _ex);
                    }
                } else {
                    alert('Неизвестная ошибка на сервере!');
                }
            }, 'json');
        }

        function _execQueryCallback(_srvAns) {
            // Ожидание _srvAns = {'Data': [], 'Error': '', '?State': 0-1000, 'Msg':''}
            _this.hideLoader();
            if(null != _srvAns) {
                // сохраняем ошибку
                _this._lastError = _srvAns['Error'];
                if('' != _srvAns['Error']) {
                    // пишем сообщение об ошибке и выходим
                    //alert(_srvAns['Msg']);
                    _this.showError(_srvAns['Msg']);
                    return ;
                }
                _this._lastData = _srvAns['Data'];
                //строим таблицу
                _buildResultTable();
            }
        }

        // build table by results and fill table by data

        function _buildResultTable() {
            /**
            создаем таблицу  и заполняем ее данными из  _this._lastData
            если там пусто, то таблица будет содержать 0 строк
            */
            _buildGrid();
            _this.showToolbarButtons();
        }

        // set button for result export

        // utils

        _this.buttonEvents = function(_click_trgt){
            var _ev, _btn, $btn;
            if (typeof void null != _click_trgt.target && null != _click_trgt.target) {
                $btn = $(_click_trgt.target);  // для jquery 3.6.0 при событии click
            } else {
                $btn = $(_click_trgt);  // для старого jquery 1.12.4 при событии click
            }
            _ev = $btn.attr('action');
            try {
                __resultEvents(_ev, $btn.get(0));
            } catch(_ex) {
                alert('Непредвиденная ошибка при обработке события - ' + _ev + '!');
            }
        };

        function __resultEvents(_evName, _evTarget) {
            switch(_evName) {
                case 'download':
                    // alert('Download query result!');
                    _exportData();
                    break;

            }
        }

        // ********************** Grid ********** {
        function _getGridCfg() {
            return {
                datatype: 'local',
                colModel: [],
                rowNum: 0,
                rowTotal: -1,
                rowList: [10, 20, 50],
                loadonce: true,
                gridview: true,
                sortname: '',
                viewrecords: true,
                rownumbers: true,
                height: "auto",
                autoencode: true,
                gridview: true,
                ignoreCase: true,
                jsonReader: { repeatitems : false },
                sortorder: 'asc',
                pager: ''
            };
        }

        function _getGridTpl(){
            if('' == _this._gridTpl) {
                _this._gridTpl += '<div id="'+_this.gridBoxID+'" class="'+_this._gridBoxCls+'">';
                _this._gridTpl += '<table id="'+_this.gridID+'" class="'+_this._gridCls+'"></table>';
                _this._gridTpl += '<div id="'+_this.gridPgID+'" class="'+_this._gridPgCls+'"></div>';
                _this._gridTpl += '</div>';
            }
            return _this._gridTpl;
        }

        function _existsTplGrid() {
            /** проверяет наличие вставленного в страницу шаблона таблицы */
            var _flg, _$c;
            _flg = false;
            _$c = _getSectionContent();
            if(0 < _$c.find('.' + _this._gridCls + ':first').length) {
                _flg = true;
            }
            return _flg;
        }

        function _addTplGrid() {
            var _gT, _$c;
            _$c = _getSectionContent();
            if(0 < _$c.length) {
                _gT = _getGridTpl();
                _$c.append(_gT);
            }
        }

        function _addQErrorTpl() {
            var _gT, _$c;
            _$c = _getSectionContent();
            if(0 < _$c.length) {
                _gT = '<div id="' + _this._errorBoxId + '" class="message-box"></div>';
                _$c.append(_gT);
            }
        }

        function _removeGridTpl() {
            var _flg, _$c, _$gt, _$gb;
            _flg = false;
            _$c = _getSectionContent();
            _$gt = _$c.find('.' + _this._gridCls + ':first');
            if(0 < _$gt.length) {
                _$gt.remove();
            }
            _$gb = _$c.find('.' + _this._gridBoxCls + ':first');
            if(0 < _$gb.length) {
                _$gb.remove();
            }
        }

        function _buildGrid() {
            var _cfg, _creGrid, _collectedCols;
            _creGrid = false;
            _collectedCols = [];
            // сперва вставить шаблон если его нет еще
            if(_existsTplGrid()) {
                _removeGrid();
                _removeGridTpl();
            }
            _addTplGrid();
            _cfg = _getGridCfg();
            _cfg.pager = '#'+_this.gridPgID;
            // требуется добавить описание колонок
            if (0 < _this._lastData.length) {
                _collectedCols = _getColsFromResult();
            } else {
                //  по какой-то причине результат запроса пуст, но мы добрались до данной строки
                // значит будем вытаскивать колонки из запроса
                _collectedCols = _getColsFromQuery();
            }
//            _cfg.colNames = ['s', 'p', 'o'];
            _cfg.colModel = [
                {'name': 's', 'index': 's'},
                {'name': 'p', 'index': 'p'},
                {'name': 'o', 'index': 'o'}
            ];

            if(0 < _collectedCols.length) {
                _cfg.colModel = _collectedCols;
            }
            // загружаем данные
            _cfg['data'] = _this._lastData;

            // теперь для пагинации надо собрать данные
            _cfg['rowNum'] = 10;
            _cfg['rowTotal'] = _cfg['data'].length;


            _this._grid = $('#'+_this.gridID).jqGrid(_cfg);
            _creGrid = (null !== _this._grid && 0 < _this._grid.length) ;
            if(''!==_cfg.pager && _creGrid){
                _this._grid.jqGrid('navGrid', _cfg.pager,{edit:false,add:false,del:false,search:false});
            }
            if (_creGrid) {
                _this._grid.jqGrid('filterToolbar',{searchOperators : true});
                _resizeGrid();
            }
        }

        function __parseAggrigateVar(_aVar) {
            var _var, _t, _cnt, _ix, _tvar;
            _var = '';
            if(4 < _aVar.length) {
                _t = _aVar.split(' ');
                _cnt = _t.length;
                for(_ix = _cnt -1; -1 < _ix; _ix--) {
                    if ('?' == _t[_ix][0] || '$' == _t[_ix][0]) {
                        break;
                    }
                }
                _tvar = _t[_ix];
                _cnt = _tvar.length;
                for(_ix = 1; _ix< _cnt;_ix++) {
                    if(')' == _tvar[_ix]) {
                        break;
                    }
                    _var += _tvar[_ix];
                }
            }
            return _var;
        }

        function __parseSelectVars(_line) {
            var _cnt, _ix, _search, _pos, _ch, _readVar, _readBrace,
                _var, _brace, _vars,
                _ob, _cb, _aVar;
            _vars = [];
            _search = 'SELECT';
            _pos = _line.indexOf(_search);
            if ( 0 > _pos) {
                _pos = _line.indexOf(_search.toLowerCase());
            }
            if ( -1 < _pos) {
                _pos += _search.length;
                _line = _line.substr(_pos).replace("\n", '');
                _cnt = _line.length;
                _readBrace = false;
                _readVar = false;
                _var = '';
                _brace = '';
                _ob = 0;
                _cb = 0;
                for(_ix=0;_ix < _cnt; _ix++) {
                    if (0 == _line[_ix].length) { continue; }
                    if (!_line[_ix]) { continue; }
                    _ch = _line.at(_ix);
                    // обрабатываем символ в соответствии с режимом
                    if(_readVar)  {
                        if(' ' == _ch) {
                            _readVar = false; // отключает режим
                            _vars.push(_var); // сохраняем переменную
                            _var = ''; // очищаем кеш-переменную
                            continue; // переходим к следующему символу
                        }
                        _var += _ch; // собираем имя переменной
                        continue; //  исключительность одного режима
                    }
                    if(_readBrace) {
                        // требуется вставить условие выхода из режима
                        // основное условие - количество открытых и закрытых скобок + текущий символ пробела
                        if ('(' == _ch) { _ob += 1; }
                        if (')' == _ch) { _cb += 1; }
                        if (_ob == _cb && ' ' == _ch) {
                            _readBrace = false; // отключаем режим
                            // теперь нужно вытащить из скобок нужную переменную
                            _aVar = __parseAggrigateVar(_brace);
                            if (_aVar) {
                                _vars.push(_aVar); // сохраняем переменную
                            }
                            _brace = ''; // очищаем кеш-переменную
                            continue; // переходим к следующему символу
                        }
                        _brace += _ch; // собираем скобку
                        continue; // исключительность одного режима
                    }
                    // когда ни один режим не включен
                    if ('?' !== _ch && '$' !== _ch && '(' !== _ch) {
                        continue;
                    }
                    if ('(' == _ch) {
                        _readBrace = true; // включаем режим чтения скобки
                        _ob += 1; // нашли первую открытую скобку
                        continue; // переходим к чтению следующего символа
                    }
                    if ('?' !== _ch || '$' !== _ch) {
                        _readVar = true; // включаем режим чтения переменной
                        continue; // переходим к чтению следующего символа
                    }
                }
            }
            return _vars;
        }

        function _getColsFromQuery() {
            var _cols, _base, t, _cnt, _ix, _m, _t1, _m1, _ts;
            _cols = [];
            if('' != _this._currentQuery) {
                // требуется выяснить какой тип запроса
                if (_isSelectQuery()) {
                    _base = __getDetectedSource();
                    // alert('Find vars: ' + __parseSelectVars(_base).join(', '));
                    t = __parseSelectVars(_base);
                    _cnt = t.length;
                    for(_ix = 0;_ix<_cnt;_ix++) {
                        _cols.push(__createColByKey(t[_ix]));
                    }
                }
                if (_isConstructQuery()) {
                    _cols.push(__createColByKey('s'));
                    _cols.push(__createColByKey('p'));
                    _cols.push(__createColByKey('o'));
                }
            }
            return _cols;
        }

        function _isSelectQuery(_qtxt) {
            var _flg;
            _base = __getDetectedSource();
            _flg = __hasWord('SELECT', _base);
            if(!_flg) {
                _flg = __hasWord('select', _base);
            }
            return _flg;
        }

        function _isConstructQuery(_qtxt){
            var _flg;
            _base = __getDetectedSource();
            _flg = __hasWord('CONSTRUCT', _base);
            if(!_flg) {
                _flg = __hasWord('construct', _base);
            }
            return _flg;
        }

        function __hasWord(_wrd, _txt) {
            var _flg;
            _flg = _txt.split(' ').some(function(t){ return t === _wrd; });
            return _flg;
        }

        function __getDetectedSource(){
            var _res, t;
            if('' != _this._currentQuery) {
                t = _this._currentQuery.split('{');
                _res = t[0];
            }
            return _res;
        }

        function _getColsFromResult() {
            var _cols, _cr, _cc, _nc;
            _cols = [];
            if (0 < _this._lastData.length) {
                _cr = _this._lastData[0];
                for (_cc in _cr) {
                    _nc = __createColByKey(_cc);
                    _cols.push(_nc);
                }
            }
            return _cols;
        }

        function __createColByKey(_k) {
            var _nc;
            _nc = _getColTpl();
            _nc['name'] = _k;
            _nc['index'] = _k;
            return _nc
        }

        function _getColTpl() {
            return {'name': '', 'index': '', 'sorttype': 'text',
                'search': true, 'stype': 'text', 'searchoptions':{sopt:['cn','nc','eq','ne','bw','bn','ew','en']}
                }
        }

        function _removeGrid() {
            if(typeof void null!==typeof _this._grid && null!==_this._grid){
                _this._grid.GridUnload(_this._grid.attr('id'));
            }
        }

        function _resizeGrid() {
            var h=0,dh=0,gdh=0,pdh=0,w=0,pdw=0,$gb,$c,navColID;
            if(typeof void null!==typeof _this._grid && null!==_this._grid){
                $gb = $('#'+_this.gridBoxID);
                $c = $gb.parent();
                pdh = $c.outerHeight(true)-$c.height();
                pdw = $c.outerWidth(true)-$c.width();
//                    navColID = _this.treePanel.getPanelID();
                $c.children().each(function(){
//                        if($(this).hasClass('jqgrid-box') || navColID===$(this).attr('id')){ return false; }
                    if($(this).hasClass(_this._gridBoxCls)){ return false; }
                    dh += $(this).outerHeight(true);
                });
                h = $c.height()-pdh-dh;
                w = $gb.width()-pdw;
                gdh += ($gb.find('.ui-jqgrid:first').outerHeight(true)-$gb.find('.ui-jqgrid:first').height()); // это рамки бокса от библиотеки
                gdh += $gb.find('.ui-jqgrid-hdiv:first').outerHeight(true); // это шапка таблицы с фильтрами
                gdh += $gb.find('.ui-jqgrid-pager:first').outerHeight(true); // это пагинатор таблицы
                gdh += $gb.find('.ui-userdata:first').outerHeight(true); // toolbar
                h -= gdh;

                // if(0 < h) {
                //    _this._grid.setGridHeight(h);
                //}
                if(0 < w) {
                    _this._grid.setGridWidth(w);
                }
            }
        }

        function _reloadGrid() {
            if(typeof void null!==typeof _this._grid && null!==_this._grid){
                _this._grid.trigger('reloadGrid');
            }
        }
        // ********************** Grid ********** }

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

        // API

        _this.initToolbar = function(){
            $('#results-toolbar .result-btn').each(function(){
                $(this).on('click', _this.buttonEvents);
                // $(this).button();
            });
            _this.hideToolbarButtons();
        };

        _this.showToolbarButtons = function(){
            $('#results-toolbar .result-btn').show();
        };

        _this.hideToolbarButtons = function(){
            $('#results-toolbar .result-btn').hide();
        };

        _this.initLoader = function(){
            var _$img;
            $('#' + _this.loaderBox).hide();
            $('#' + _this.loaderBox).css({'width': '40px', 'height': '40px'});
            _$img = $('<img src="" />');
            _$img.attr('src', _this._base_url + '/static' + _this.loadMarker);
            $('#' + _this.loaderBox).append(_$img);
        };

        _this.showLoader = function(){
            $('#' + _this.loaderBox).show();
        };

        _this.hideLoader = function(){
            $('#' + _this.loaderBox).hide();
        };

        _this.clearResult = function() {
            if(_existsTplGrid()) {
                _removeGrid();
                _removeGridTpl();
                _this.hideToolbarButtons();
            }
            _hideSection();
        };

        _this.showError = function(errMsg){
            if(0 == $('#' + _this._errorBoxId).length) {
                _addQErrorTpl();
            }
            $('#' + _this._errorBoxId).html(errMsg);
            $('#' + _this._errorBoxId).show();
        };

        _this.hideError = function(){
            if(0 < $('#' + _this._errorBoxId).length) {
                $('#' + _this._errorBoxId).html();
                $('#' + _this._errorBoxId).hide();
            }
        };

        _this.execQuery = function(txt, _ep) {
            var _$c;
            _this.hideError();
            _showSection();
            _$c = _getSectionContent();
            _this._currentQuery = txt;
            _this._lastEP = _ep;
            //  удалить таблицу если она есть
            if(_existsTplGrid()) {
                _removeGrid();
                _removeGridTpl();
            }
            // показать индикатор загрузки
            _this.showLoader();
            _this.hideToolbarButtons();
            _sendQuery(txt, _ep, _execQueryCallback);
        };

        // constructor actions
        _this._$box = $(conta);
        _this._base_url = $('#js-base-url').val();
        _hideSection();
        _this.initLoader();
        _this.initToolbar();
    };

    try {

    } catch(e) {
        alert(e);
    }
    if ('object' === typeof win && 'object' === typeof win.document) {
        win['_clsQueryResult'] = _clsQueryResult;
    }
}(window));