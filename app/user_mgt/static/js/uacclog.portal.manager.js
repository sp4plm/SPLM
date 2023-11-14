var _PortalUAccLogManagerCls = function(p){
    var _this = this,
        _selfCode = 'PortalUAccLog',
        _isInit = false,
        _initTO = null,
        _agrigator = p.container, // куда встраивается наш модуль
        _EvMan = _agrigator[p.eventBus], // менеджер событий объекта в который встраивается наш модуль
        _$box=null;
    // вызов родительского конструктора
    _PortalUAccLogManagerCls.superclass.constructor.call(_this,p.constructorParams);
    _this.langData = null;
    if(typeof void null!=typeof p.constructorParams && null!==p.constructorParams){
        _this.langData = (typeof void null!=typeof p.constructorParams.langData && null!==p.constructorParams.langData)? p.constructorParams.langData:null;
    }

    _this.loader = null;
    _this.header = '';
    _this.viewTmpl = '';
    _this.blkBox = null;
    _this.baseURL = '/portal/uacclog';
    _this.moduleData = null;

    /* jqGrid для отображения содержимого одной директории [ */
    _this.Grid = function(k){
        var _cls = function(p){
            var _1this = this,
                _$grid;
            _1this.gridBoxCls = 'jqgrid-box';
            _1this.gridCls = 'jqgrid-tbl';
            _1this.gridPgCls = 'jqgrid-tbl-pg';
            _1this.gridBoxID = p.id+'-gridbox';
            _1this.gridID = p.id+'-grid';
            _1this.gridPgID = p.id+'-grid-pg';

            function _getGridCfg(){
                return {
                    mtype:'POST', url:'', datatype: 'json',
                    colModel:[],
                    rowNum:20, rowList:[5, 10, 20, 30, 50],
                    autowidth:true,
                    sortname: '', sortorder: '',
                    caption: '',
                    pager: '',
                    toolbar: [true,'top'],
                    jsonReader: { repeatitems : false },
                    viewrecords: true,
                    gridview: true
                };
            }

            _1this.getWorkArea = function(){
                var wa={w:0,h:0,top:0,left:0},pos;
                wa.w = $('#'+_1this.gridBoxID).outerWidth(true);
                wa.h = $('#'+_1this.gridBoxID).outerHeight(true);
                pos = $('#'+_1this.gridBoxID).offset();
                wa.top = pos.top;
                wa.left = pos.left;
                return wa;
            };

            _1this.fillTmpl = function(){
                _this.viewTmpl += '<div id="'+_1this.gridBoxID+'" class="'+_1this.gridBoxCls+'">';
                _this.viewTmpl += '<table id="'+_1this.gridID+'" class="'+_1this.gridCls+'"></table>';
                _this.viewTmpl += '<div id="'+_1this.gridPgID+'" class="'+_1this.gridPgCls+'"></div>';
                _this.viewTmpl += '</div>';
            };

            _1this.cookToolbar = function(){
                var $tb = _1this.getGridToolBarEl(),
                    lbl1 = '<a target="_blank" href="'+_this.baseURL+'/export/excel/"><img style="width:16px;height:16px;margin:2px;float:left;clear:none;" src="/static/img/excel-icon16.gif" /></a>';
                $tb.append('<span class="ui-corner-all toolbar-btn" style="float:right;clear:none;" action="export2Excel">'+lbl1+'</span>');
                $tb.find('.toolbar-btn').click(function(){ _EvMan.fire('ClickGridToolbarBtn',{action:$(this).attr('action'),$btn:$(this)}); });
            };

            _1this.cookURL = function(){
                var bU = _this.baseURL+'/getList/';
                return bU;
            };

            _1this.cookRowToolbar = function(){
                var tb = '';
                tb += '<input type="checkbox" class="toolbar-row-selector" name="RowSelector[]" />';
                tb += '<span class="toolbar-delim"></span>';
//                tb += '<span class="ui-corner-all toolbar-btn" action="open"><span class="ui-icon ui-icon-folder-open"></span></span>';
                tb += '<span class="ui-corner-all toolbar-btn" action="edit"><span class="ui-icon ui-icon-pencil"></span></span>';
                tb += '<span class="ui-corner-all toolbar-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></span>';
                return tb;
            };
            _1this.addRowToolbars = function(){
                var cN='Toolbar',cnt=0,ids=_$grid.getDataIDs(),
                    kx=0,cell;
                cnt = ids.length;
                if(cnt>0){
                    // добавить в ячейку Toolbar
                    // для всех удалить и открыть и переименовать
                    for(kx=0;kx<cnt;kx++){
                        cell='';
                        cell = _1this.cookRowToolbar();
                        _$grid.setCell(ids[kx],cN,cell);
                    }
                    _$grid.find('tr input.toolbar-row-selector').click(function(){
                        _EvMan.fire('ToggleGridRowSelection',{rowID:$(this).parent().parent().attr('id'), selected:$(this).prop('checked')});
                    });
                    _$grid.find('tr .toolbar-btn').click(function(){
                        _EvMan.fire('ClickGridRowToolbarBtn',{action:$(this).attr('action'),
                            rowID:$(this).parent().parent().attr('id')
                        });
                    });
                }
            };

            _1this.buildGrid = function(){
                var _cfg = _getGridCfg();
                _1this.remove();
                _cfg.colModel = _this.moduleData.grid.columns;
                _cfg.pager = '#'+_1this.gridPgID;
                // создать урл для запросов на сервер
                _cfg.url = _1this.cookURL();

                // Навесить события на тулбаре в каждой строке
                _cfg.loadComplete = function(){
                    _1this.addRowToolbars();
                };

                _$grid = $('#'+_1this.gridID).jqGrid(_cfg);
                if(''!==_cfg.pager){
                    _$grid.jqGrid('navGrid','#'+_1this.gridPgID,{edit:false,add:false,del:false,search:false});
                }
                if(typeof void null!==typeof _cfg.toolbar && _cfg.toolbar[0]){
                    _1this.cookToolbar();
                }
                _1this.resize();
            };

            _1this.updateData = function(){
                _$grid.setGridParam('url',_1this.cookURL());
                _1this.reload();
            };

            _1this.clearData = function(){
                if(typeof void null!==typeof _$grid && null!==_$grid){
                    _$grid.clearGridData();
                }
            };
            _1this.getRowData = function(rID){
                if(typeof void null!=typeof rID && null!==rID){
                    return _$grid.getRowData(rID);
                }else{
                    return _$grid.getRowData();
                }
            };
            _1this.remove = function(){
                if(typeof void null!==typeof _$grid && null!==_$grid){
                    _$grid.GridUnload(_$grid.attr('id'));
                }
            };
            _1this.delRow = function(rID){
                var t;
                if(typeof void null!=typeof rID && null!==rID){
                    _$grid.delRowData(rID);
                    // надо проверить если строка была последней, но надо перезагрузить таблицу
                    t = _1this.getRowData();
                    if(0===t.length){
                        _1this.reload();
                    }
                }else{
                    _1this.clearData();
                }
            };

            _1this.reload = function(){
                if(typeof void null!==typeof _$grid && null!==_$grid){
                    _$grid.trigger('reloadGrid');
                }
            };

            _1this.getSelectedRows = function(){
                var rows = [];
                _$grid.find('tr input.toolbar-row-selector:checked').each(function(){
                    var row = {},rID = $(this).parent().parent().attr('id');
                    row = _1this.getRowData(rID);
                    rows.push(row);
                });
                return rows;
            };

            _1this.getGridToolBarEl = function(){
                return $('#t_'+_1this.gridID);
            };

            _1this.resize = function(){
                if(typeof void null!==typeof _$grid && null!==_$grid){
                    var h=0,dh=0,gdh=0,pdh=0,w=0,pdw=0,
                        $gb = $('#'+_1this.gridBoxID),
                        $c = $gb.parent(),
                        navColID;
                    pdh = $c.outerHeight(true)-$c.height();
                    pdw = $c.outerWidth(true)-$c.width();
//                    navColID = _this.treePanel.getPanelID();
                    $c.children().each(function(){
//                        if($(this).hasClass('jqgrid-box') || navColID===$(this).attr('id')){ return false; }
                        if($(this).hasClass(_1this.gridBoxCls)){ return false; }
                        dh += $(this).outerHeight(true);
                    });
                    h = $c.height()-pdh-dh;
                    w = $gb.width()-pdw;
                    gdh += ($gb.find('.ui-jqgrid:first').outerHeight(true)-$gb.find('.ui-jqgrid:first').height()); // это рамки бокса от библиотеки
                    gdh += $gb.find('.ui-jqgrid-hdiv:first').outerHeight(true); // это шапка таблицы с фильтрами
                    gdh += $gb.find('.ui-jqgrid-pager:first').outerHeight(true); // это пагинатор таблицы
                    gdh += $gb.find('.ui-userdata:first').outerHeight(true); // toolbar
                    h -= gdh;

                    _$grid.setGridHeight(h);
                    _$grid.setGridWidth(w);
                }
            };

            _1this.init = function(){
                _1this.buildGrid();
            };

            _this.baseURL = $('#js-base-url').val();

            function _c(){}
            _c();
        };
        return new _cls(k);
    };
    /* jqGrid для отображения содержимого одной директории ] */

    _this.gridToolbarEvCatcher = function(p){
        switch(p.action){
            case 'groupDelete':
                break;
            case 'export2Excel':
//                _this.exportLog('excel');
                break;
        }
    };
    _this.gridRowToolbarEvCatcher = function(p){
        // p=> {action:'', rowID:'' }
        var row;
        row = _this.Grid.getRowData(p.rowID);
        row['rowID'] = p.rowID;
        switch(p.action){
            case 'open':
                break;
            case 'edit':
                break;
            case 'remove':
                break;
        }
    };

    _this.exportLog = function(format){
        // сперва нам надо создать ссылку скрытую
        var $a = $('<a style="display:none;">l</a>');
        // указать ей правильный адрес
        $a.attr('href',_this.baseURL+'/export/'+format+'/');
        // указать чтобы открывалась в новом окне
        $a.attr('target','_blank');
//        alert(format);
        $('body').append($a);
        $a.trigger('click');
//        $a.remove();
    };

    _this.fillTmpl = function(){
//        _this.viewTmpl = '<div class="" id="">';
        _this.Grid.fillTmpl();
//        _this.viewTmpl += '</div>';
    };

    _this.resize = function(){
        if(null!==_$box){
            var wD = _$box.outerWidth(true)-_$box.width();
            var hD = _$box.outerHeight(true)-_$box.height();
            _$box.width(_this.blkBox.width()-wD);
            _$box.height(_this.blkBox.height()-hD);
        }
    };

    _this.run = function(iO){
        if(!_isInit){
            _initTO = setTimeout(function(){ _this.run(iO); },100);
            return;
        }
        if(_initTO){ clearTimeout(_initTO); }
        _this.header = iO.pageLabel;
        _this.blkBox = iO.place;
        _this.hideBrothers(_this.blkBox);
        _this.fillTmpl();
        if(null===_$box){
            _$box = $(_this._tmpl);
            _$box.addClass('clns-box');
            _$box.addClass(_this.cls);
            _$box.addClass('ui-widget');
            _$box.attr('code',iO.code);
            _$box.append(_this.blkHeaderTpl.replace(/#\{label\}/g, _this.header));
            _$box.append(_this.viewTmpl);
            _$box.hide();
            $(_this.blkBox).append(_$box);
            _this.resize();
        }

        _$box.show();
        if(null===_this.loader){
            _this.loader = $(_$box).WFMLoader({img:'/static/img/loader.gif',runOnCreate: false});
        }
        _this.loader.WFMLoader().show();
        // теперь надо создать грид сосписком новостей
        _this.Grid.init();
        _this.loader.WFMLoader().hide();
    };

    function _c(){
        // по-скольку наш модуль отвечает за пункт меню
        // подпишимся на его событие
        _EvMan.subscribe('SelectMenuItem', function(p){
            // если это наш пункт меню,то мы запускаемся
            if(_selfCode===p.code){ _this.run(p); }
        });
        _EvMan.subscribe('pageResize', function(p){ _this.resize(); });
        _EvMan.subscribe('ClickGridToolbarBtn',_this.gridToolbarEvCatcher);
//        _EvMan.subscribe('ClickGridRowToolbarBtn',_this.gridRowToolbarEvCatcher);
        // надо загрузить данные для модуля
        $.post(_this.baseURL+'/getModuleData/',null,function(amd){ _this.moduleData = amd; _isInit = true;
            _this.Grid = _this.Grid({id:'uacclog-register'})
        },'json');
    }

    _c();
};
// теперь относледуемся
_jsUtils.inherit(_PortalUAccLogManagerCls,PageBlock);

// подключаем наш модуль по событию что приложение готово подключать модуль, так как аяксом запрашиваются данные о локализации
if(typeof void null!==typeof Desktop && null!==Desktop){
    Desktop.EvMan.subscribe('CanRegBlocks',function(p){
        if(typeof void null!==typeof Desktop.app && null!==Desktop.app){
            p['langData']['PortalUAccLog'].curLangCode = p.curLangCode;
            Desktop.app.registerBlock('PortalUAccLog',_PortalUAccLogManagerCls,{langData:p['langData']['PortalUAccLog']});
        }
    });
}