(function(win,undefined){
    if(typeof void null!==typeof jQuery){
        (function($){
            PortalFilesManager = function(parent) {
                var cls = function(p){
                    var _this = this,
                        _selfCode = 'PortalFiles',
                        _url_pref,
                        // _agrigator = p.container, // куда встраивается наш модуль
                        // _EvMan = null // _agrigator[p.eventBus], // менеджер событий объекта в который встраивается наш модуль
                        _$box=null;
                    // вызов родительского конструктора
                    cls.superclass.constructor.call(_this,p);
                    _this.langData = null;
                    if(typeof void null!=typeof p && null!==p){
                        _this.langData = (typeof void null!=typeof p.langData && null!==p.langData)? p.langData:null;
                    }

                    _this.EvMan = null
                    _this.loader = null;
                    _this.header = '';
                    _this.viewTmpl = '';
                    _this.blkBox = null;
                    _this.workDir = '';
                    _this.baseURL = '/portal/files';
                    _this.staticBase = '/static';
                    /* TreePanel для навигации по структуре [ */
                    _this.treePanel = function(){
                        var _cls = function(){
                            var _1this = this,
                                _$tree=null;

                            _1this.panelId = 'pfiles-treepanel';

                            function _getTreeCfg(){}

                            _1this.getPanelID = function(){ return _1this.panelId; };

                            _1this.fillTmpl = function(){
                                _this.viewTmpl += '<div id="'+_1this.panelId+'"></div>';
                            };

                            _1this.cookURL = function(){
                                var url = _this.baseURL+'/getStructTree';
                                if(''!==_this.workDir){
                                    url += '/'+_this.workDir;
                                }
                                return url;
                            };

                            _1this.build = function(){
                                var url = _1this.cookURL(),
                                    mainTree = {'name':'','text':'','path':'','children':[],
                                        'icon':_this.staticBase + '/img/home2.png',
                                        'state':{
                                            'opened':true,
                                            'disabled':false,
                                            'selected':true
                                        }};

                                $.post(url,null,function(struct){
                                    var _cfg = {};
                                    _cfg.core = {};
                                    mainTree.children = struct;
                                    _cfg.core.data = mainTree;
                                    _1this.remove();
                                    _$tree = $('#'+_1this.panelId)
                                            .on('select_node.jstree',function(e,data){
                                                var p = _$tree.jstree().get_path(data.node);
                                                _this.EvMan.fire('SelectTreePanelNode',{treeNode:data.node,
                                                    dir:data.node.text,
                                                    path:p,_skey:_selfCode
                                                });
                                            })
                                            .jstree(_cfg);
                                },'json');
                            };

                            _1this.remove = function(){
                                if(typeof void null!==typeof _$tree && null!==_$tree){
                                    _$tree.jstree().destroy();
                                }
                            };

                            _1this.reload = function(){
                                _1this.build();
                            };

                            _1this.resize = function(){};

                            _1this.init = function(){
                                _1this.build();
                            };

                            function _c(){}
                            _c();
                        };
                        return new _cls();
                    }();
                    /* TreePanel для навигации по структуре ] */
                    /* jqGrid для отображения содержимого одной директории [ */
                    _this.dirGrid = function(){
                        var _cls = function(){
                            var _1this = this,
                                _$grid;
                            _1this.gridBoxCls = 'jqgrid-box';
                            _1this.gridCls = 'jqgrid-tbl';
                            _1this.gridPgCls = 'jqgrid-tbl-pg';
                            _1this.gridBoxID = 'pfiles-dirgridbox';
                            _1this.gridID = 'pfiles-dirgrid';
                            _1this.gridPgID = 'pfiles-dirgrid-pg';

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

                            _1this.fillTmpl = function(){
                                _this.viewTmpl += '<div id="pfiles-dirgridbox" class="jqgrid-box">';
                                _this.viewTmpl += '<table id="pfiles-dirgrid" class="jqgrid-tbl"></table>';
                                _this.viewTmpl += '<div id="pfiles-dirgrid-pg" class="jqgrid-tbl-pg"></div>';
                                _this.viewTmpl += '</div>';
                            };

                            _1this.cookToolbar = function(){
                                var $tb = _1this.getGridToolBarEl(),
                                    lbl1 = _this.langData.interface.createDir,
                                    lbl2 = _this.langData.interface.uploadFiles,
                                    lbl3 = _this.langData.interface.delete;
                                $tb.append('<span class="ui-corner-all toolbar-btn" action="groupDelete" disabled="true"><span class="text">'+lbl3+'</span></span>');
                                $tb.append('<span class="toolbar-delim"></span>');
                                // кнопка "Перейти на уровень выше"
                                $tb.append('<span class="ui-corner-all toolbar-btn" action="uplevel"><span class="ui-icon ui-icon-arrowreturnthick-1-n"></span></span>');
                                // кнопка "Создать директорию"
                                $tb.append('<span class="ui-corner-all toolbar-btn" action="adddirectory"><span class="text">'+lbl1+'</span></span>');

                                // кнопка "загрузить файл(ы)"
                                $tb.append('<span class="ui-corner-all toolbar-btn" action="addfiles"><span class="text">'+lbl2+'</span></span>');

                                $tb.find('.toolbar-btn').click(function(){ _this.EvMan.fire('ClickGridToolbarBtn',{action:$(this).attr('action'),$btn:$(this),_skey:_selfCode}); });
                            };

                            _1this.cookURL = function(){
                                var bU = _this.baseURL+'/getDirSource/';
                                if(_this.workDir!==''){
                                    bU += _this.workDir4url(_this.workDir);
                                }
                                return bU;
                            };

                            _1this.cookRowToolbar = function(){
                                var tb = '';
                                tb += '<input type="checkbox" class="toolbar-row-selector" name="RowSelector[]" />';
                                tb += '<span class="toolbar-delim"></span>';
                                tb += '<span class="ui-corner-all toolbar-btn" action="open"><span class="ui-icon ui-icon-folder-open"></span></span>';
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
                                        _this.EvMan.fire('ToggleDirGridRowSelection',{rowID:$(this).parent().parent().attr('id'), selected:$(this).prop('checked'),_skey:_selfCode});
                                    });
                                    _$grid.find('tr .toolbar-btn').click(function(){
                                        _this.EvMan.fire('ClickGridRowToolbarBtn',{action:$(this).attr('action'),
                                            rowID:$(this).parent().parent().attr('id'),_skey:_selfCode
                                        });
                                    });
                                }
                            };

                            _1this.buildGrid = function(){
                                var _cfg = _getGridCfg();
                                _1this.remove();
                                _cfg.colModel.push({name:'Toolbar',index:'Toolbar',label:'-',width:'60px',sortable:false, search: false});
                                _cfg.colModel.push({name:'Type',index:'Type',label:'Type',hidden:true,sortable:false, search: false});
                                _cfg.colModel.push({name:'Name',index:'Name',label:'Name', 'searchoptions': {sopt:['cn','nc']}});
                                _cfg.colModel.push({name:'Path',index:'Path',label:'Path', sortable:false, search: false});
                                _cfg.pager = '#'+_1this.gridPgID;
                                // создать урл для запросов на сервер
                                _cfg.url = _1this.cookURL();

                                // Навесить события на тулбаре в каждой строке
                                _cfg.loadComplete = function(){
                                    _1this.addRowToolbars();
                                };

                                _$grid = $('#pfiles-dirgrid').jqGrid(_cfg);
                                // добавляем поиск по колонкам
                                _$grid.jqGrid('filterToolbar',{searchOperators : true});
                                if(''!==_cfg.pager){
                                    _$grid.jqGrid('navGrid','#'+_1this.gridPgID,{edit:false,add:false,del:false,search:false},{},
                                        {},
                                        {},
                                        {multipleSearch:false, multipleGroup:false});
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
                                    pdh = $c.outerHeight()-$c.height();
                                    pdw = $c.outerWidth()-$c.width();
                                    navColID = _this.treePanel.getPanelID();
                                    $c.children().each(function(){
                                        if($(this).hasClass('jqgrid-box') || navColID===$(this).attr('id')){ return false; }
                                        dh += $(this).outerHeight();
                                    });
                                    h = $c.height()-pdh-dh;
                                    w = $gb.width()-pdw;
                                    gdh += ($gb.find('.ui-jqgrid:first').outerHeight()-$gb.find('.ui-jqgrid:first').height()); // это рамки бокса от библиотеки
                                    gdh += $gb.find('.ui-jqgrid-hdiv:first').outerHeight(); // это шапка таблицы с фильтрами
                                    gdh += $gb.find('.ui-jqgrid-pager:first').outerHeight(); // это пагинатор таблицы
                                    gdh += $gb.find('.ui-userdata:first').outerHeight(); // toolbar
                                    h -= gdh;

                                    _$grid.setGridHeight(h-10); // magic
                                    _$grid.setGridWidth(w-10);
                                }
                            };

                            _1this.init = function(){
                                _1this.buildGrid();
                            };

                            function _c(){}
                            _c();
                        };
                        return new _cls();
                    }();
                    /* jqGrid для отображения содержимого одной директории ] */

                    /* uiDialog для работы с формами в диалогах */
                    _this.dialog = function(k){
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
                                                open:function(){ _this.EvMan.fire('FMDialogOpen',{content:$(this),_skey:_selfCode}); },
                                                beforeClose:function(){ _this.EvMan.fire('FMDialogBeforeClose',{content:$(this),_skey:_selfCode}); },
                                                close:function(){ _this.EvMan.fire('FMDialogClose',{content:$(this),_skey:_selfCode}); }
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
                                    _1this.close();
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

                    _this.fillTmpl = function(){
                //        _this.viewTmpl = '<div class="" id="">';
                        _this.treePanel.fillTmpl();
                        _this.dirGrid.fillTmpl();
                //        _this.viewTmpl += '</div>';
                    };

                    _this.getDirDialogTmpl = function(){
                        var t = '';
                        t += '<form name="FMDirForm" onsubmit="return false;">';
                        t += '<label>'+ _this.langData.interface.nameDir+':</label>&nbsp;';
                        t += '<input type="text" name="DName" value="" />';
                        t += '<br /><br /><button name="Save">'+ _this.langData.interface.save+'</button>';
                        t += '</form>';
                        return t;
                    };

                    _this.cookFilesUploadIframe = function(){
                        var name = 'FMIFrameHelper';
                        if(0===_$box.find('iframe[name="'+name+'"]').length){
                            _$box.append('<iframe name="'+name+'" style="display:none;width:0px;height:0px;"></iframe>');
                            // теперь надо навесить на iframe событие на загрузку
                            _$box.find('iframe[name="'+name+'"]').load(function(){
                                _this.EvMan.fire('FMIFrameHelperLoaded',{iframe:$(this),_skey:_selfCode});
                            });
                        }
                        return name;
                    };

                    _this.getFilesDialogTmpl = function(){
                        var t = '';
                        t += '<form name="FMFilesForm" onsubmit="return false;" action="" target="'+_this.cookFilesUploadIframe()+'" method="post" enctype="multipart/form-data">';
                        t += '<label>'+ _this.langData.interface.selectFiles+':</label>&nbsp;';
                        t += '<input type="file" multiple="true" name="File[]" value="" />';
                        t += '<br /><span>'+_this.langData.interface.maxFileSizeLbl+': '+_this.langData.interface.maxFileSize+'</span>';
                        //t += '<br /><span>'+_this.langData.interface.maxFilesUploadLbl+': '+_this.langData.interface.maxFilesUpload+'</span>';
                        t += '<br /><button name="Upload">'+ _this.langData.interface.upload+'</button>';
                        t += '</form>';
                        return t;
                    };

                    _this.getFileDialogTmpl = function(){
                        var t = '';
                        t += '<form name="FMFileForm" onsubmit="return false;" action="" target="'+_this.cookFilesUploadIframe()+'" method="post" enctype="multipart/form-data">';
                        t += '<label>'+ _this.langData.interface.nameFile+':</label>&nbsp;';
                        t += '<input type="text" name="FileName" value="" />';
                        t += '<input type="hidden" name="OldName" value="" />';
                        t += '<br /><label>'+ _this.langData.interface.file.substr(0,1).toUpperCase()+_this.langData.interface.file.substr(1)+':</label>&nbsp;';
                        t += '<input type="file" name="File" value="" />';
                        //t += '<br /><span>'+_this.langData.interface.maxFileSizeLbl+': '+_this.langData.interface.maxFileSize+'</span>';
                        t += '<br /><span>'+_this.langData.interface.maxFilesUploadLbl+': '+_this.langData.interface.maxFilesUpload+'</span>';
                        t += '<br /><button name="Update">'+ _this.langData.interface.upload+'</button>';
                        t += '</form>';
                        return t;
                    };

                    _this.workDir4url = function(wrkDir){
                        var t=[];
                        t = wrkDir.split('/');
                        return t.join('$')
                    };

                    _this.updateWorkDir = function(dir,act){
                        var t=[],cnt=0,kx;
                        if(''!==_this.workDir){
                            t = _this.workDir.split('/');
                        }
                        if(act=='up'){
                //            cnt = t.length;
                            t.pop();
                        }
                        if(act=='down'){
                            if(t[t.length-1]!==dir){ t.push(dir); }
                        }
                        _this.workDir = t.join('/');
                    };

                    _this.gridToolbarEvCatcher = function(evName, p){
                        if(p._skey!==_selfCode) { return ; }
                        switch(p.action){
                            case 'groupDelete':
                                // групповое удаление элементов на текущем уровне
                //                if(!p.$btn.prop('disabled')){ // почему-то в ИЕ 11 не возникает событие клик на чекбоксе
                                if(confirm('Вы действительно хотите удалить выделенные элементы?')){
                                    _this.deleteSelectedItems();
                                }
                //                }
                                break;
                            case 'uplevel':
                                // если возможно то поднимаемся на 1 уровень вверх
                                if(''!==_this.workDir){
                                    _this.updateWorkDir(_this.workDir.split('/').pop(),'up');
                                    _this.dirGrid.buildGrid();
                                }
                                break;
                            case 'adddirectory':
                                // открываем окно для создания новой директории
                                _this.dialog.open(_this.getDirDialogTmpl(),function($box){
                                    $box.find('button[name="Save"]').click(function(){ _this.saveDirectory($(this).parent()); });
                                });
                                break;
                            case 'addfiles':
                                // открываем окно для загрузки файла(ов)
                                _this.dialog.open(_this.getFilesDialogTmpl(),function($box){
                                    $box.find('button[name="Upload"]').click(function(){
                                        _this.uploadFiles($(this).parent());
                                    });
                                });
                                break;
                        }
                    };
                    _this.gridRowToolbarEvCatcher = function(evName, p){
                        if(p._skey!==_selfCode) { return ; }
                //       p=> {action:'', rowID:'' }
                        var type,row, _download;
                        row = _this.dirGrid.getRowData(p.rowID);
                        row['rowID'] = p.rowID;
                        type = row['Type']; // f - is a file, d - is a directory
                        switch(p.action){
                            case 'open':
                                // если файл то даем скачать
                                if(type==='f'){
                                    _download = _getFileDownloadTag(row['Path']);
                                    _download.attr('target', '_blank');
                                    _download.css({'display': 'none'});
                                    $('body').append(_download);
                                    _download.get(0).click();
                                    _download.remove();
                                }else{
                                    // если директория то проваливаемся в нее - т.е. перерисовываем таблицу с учетом директории
                                    _this.updateWorkDir(row['Name'],'down');
                                    _this.dirGrid.buildGrid();
                                }
                                break;
                            case 'edit':
                                // открываем окно редактирования директории/файла
                                if(type==='f'){
                                    _this.dialog.open(_this.getFileDialogTmpl(),function($box){
                                        $box.find('input[name="FileName"]').val(row.Name);
                                        $box.find('input[name="OldName"]').val(row.Name);
                                        $box.find('button[name="Update"]').click(function(){ _this.editFile($(this).parent(),row); });
                                    });
                                }else{
                                    // открываем окно для создания новой директории
                                    _this.dialog.open(_this.getDirDialogTmpl(),function($box){
                                        $box.find('input[name="DName"]').val(row.Name);
                                        $box.find('button[name="Save"]').click(function(){ _this.renameDirectory($(this).parent(),row); });
                                    });
                                }
                                break;
                            case 'remove':
                                // удаляем файл/директорию
                                if(confirm('Вы действительно хотите удалить - ' + row.Name +'?')){
                                    if(type==='f'){
                                        _this.removeFile(row);
                                    }else{
                                        _this.removeDirectory(row);
                                    }
                                }
                                break;
                        }
                    };

                    function _getFileDownloadTag(rel) {
                        var $a, _url;
                        _url = _this.baseURL+'/download';
                        _url += '/' + rel;
                        $a = $('<a></a>');
                        $a.attr('href', _url);
                        return $a;
                    }

                    _this.saveDirectory = function($form){
                        var url = _this.baseURL+'/saveDirectory', wD = _this.workDir,
                            dir;
                        dir = $form.find('input[name="DName"]').val();
                        $.post(url,{directory:dir,base:wD},function(sA){
                            if(sA.State==200){
                                // закрыть диалог
                                _this.dialog.close();
                                // перезагрузить таблицу
                                _this.dirGrid.reload();
                                // перезагрузить дерево
                                _this.treePanel.reload();
                            }else{
                                alert(sA.Msg);
                            }
                        },'json');
                    };
                    _this.renameDirectory = function($form,oldData){
                        var url = _this.baseURL+'/renameDirectory', wD = _this.workDir,
                            dir;
                        dir = $form.find('input[name="DName"]').val();
                        $.post(url,{directory:oldData.Name,newName:dir,base:wD},function(rmA){
                            if(rmA.State==200){
                                // закрыть диалог
                                _this.dialog.close();
                                // перезагрузить таблицу
                                _this.dirGrid.reload();
                                // перезагрузить дерево
                                _this.treePanel.reload();
                            }else{
                                alert(rmA.Msg);
                            }
                        },'json');
                    };

                    _this.removeDirectory = function(data){
                        var url = _this.baseURL+'/removeDirectory', wD = _this.workDir,
                            dir;
                            dir = data.Name;
                        $.post(url,{directory:dir,base:wD},function(rA){
                            if(rA.State==200){
                                // перезагрузить таблицу
                                _this.dirGrid.reload();
                                // перезагрузить дерево
                                _this.treePanel.reload();
                            }else{
                                alert(rA.Msg);
                            }
                        },'json');
                    };

                    _this.uploadFiles = function($form){
                        var url = _this.baseURL+'/uploadFiles';
                        if(''!==_this.workDir){
                            url += '/'+_this.workDir4url(_this.workDir);
                        }
                        // сперва надо добавить информацию о директории
                        $form.attr('onsubmit','');
                        $form.removeAttr('onsubmit');
                        $form.attr('action',url);
                        $form.trigger('submit');
                    };

                    _this.editFile = function($form,data){
                        var url = _this.baseURL+'/editFile';
                        if(''!==_this.workDir){
                            url += '/'+_this.workDir4url(_this.workDir);
                        }
                        // сперва надо добавить информацию о директории
                        $form.attr('onsubmit','');
                        $form.removeAttr('onsubmit');
                        $form.attr('action',url);
                        $form.trigger('submit');
                    };

                    _this.removeFile = function(data){
                        var url = _this.baseURL+'/removeFile';
                        if(''!==_this.workDir){
                            url += '/'+_this.workDir4url(_this.workDir);
                        }
                        $.post(url,{file:data.Name},function(rfA){
                            if(rfA.State==200){
                                _this.dirGrid.delRow(data.rowID);
                            }else{
                                alert(rfA.Msg);
                            }
                        },'json');
                    };

                    _this.deleteSelectedItems = function(){
                        var url = _this.baseURL+'/removeSelection',
                            selRows = _this.dirGrid.getSelectedRows(),
                            cnt=selRows.length,kx=0,
                            data = {items:[]};
                        if(''!==_this.workDir){
                            url += '/'+_this.workDir4url(_this.workDir);
                        }
                        for(kx=0;kx<cnt;kx++){
                            data.items.push(selRows[kx].Name);
                        }
                        $.post(url,data,function(riA){
                            if(riA.State==200){
                                _this.dirGrid.reload();
                                _this.treePanel.reload();
                            }else{
                                alert(riA.Msg);
                            }
                        },'json');
                    };

                    _this.resize = function(){
                        if(null!==_$box){
                            var wD = _$box.outerWidth(true)-_$box.width();
                            var hD = _$box.outerHeight(true)-_$box.height();
                            _$box.width(_this.blkBox.width()-wD);
                            // сперва надо взять родителя и вычесть высоту детей
                            _$box.height(_this.blkBox.height()-hD-_this.blkBox.find('h1').outerHeight());
                            _this.treePanel.resize();
                            _this.dirGrid.resize();
                        }
                    };
                    _this.run = function(iO){
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
                            //_$box.append(_this.blkHeaderTpl.replace(/#\{label\}/g, _this.header));
                            _$box.append(_this.viewTmpl);
                            _$box.hide();
                            $(_this.blkBox).append(_$box);
                            _this.resize();
                        }

                        _$box.show();
                        if(null===_this.loader){
                            _this.loader = $(_$box).WFMLoader({img:_this.staticBase + '/img/loader.gif',runOnCreate: false});
                        }
                        _this.loader.WFMLoader().show();
                        // теперь надо инициализировать treePanel для удобства навигации
                        _this.treePanel.init();
                        // теперь надо создать грид с содержимым корневой директории
                        _this.dirGrid.init();

                        _this.dialog.init();
                        _this.loader.WFMLoader().hide();
                    };

                    function _c(){
                        var _$box1;
                        // инициализируем менеджер событий, для взаимодействия
                        //_$box = $('.maincontent:first');
                        _$box1 = $('#page-content-marker').parent();
                        _this.baseURL = _$box1.find('#js-base-url').val();
                        _this.staticBase = _this.baseURL + _this.staticBase
                        try{
                            _this.EvMan = new win._custEvents();
                        }catch(err){
                            alert(err.toString());
                            return ;
                        }
                        // по-скольку наш модуль отвечает за пункт меню
                        // подпишимся на его событие
                        _this.EvMan.subscribe('SelectMenuItem', function(evName, p){
                            // если это наш пункт меню,то мы запускаемся
                            if('PortalFiles'===p.code){ _this.run(p); }
                        });
                        _this.EvMan.subscribe('pageResize', function(evName, p){ _this.resize(); });
                        // подписываемся на событие отработки кнопок на тулбаре
                        _this.EvMan.subscribe('ClickGridToolbarBtn',_this.gridToolbarEvCatcher);
                        _this.EvMan.subscribe('ClickGridRowToolbarBtn',_this.gridRowToolbarEvCatcher);
                        _this.EvMan.subscribe('FMIFrameHelperLoaded',function(evName, p){
                            var answer, answer_json;
                            if(p._skey!==_selfCode) { return ; }
                            answer = p.iframe.get(0).contentDocument.body.innerHTML;
                            answer_json = {};
                            if('' != answer) {
                                try {
                                    answer_json = JSON.parse(answer);
                                }catch{
                                    answer_json = {};
                                    answer_json['Msg'] = 'Не удалось преобразовать в объект ответ сервера!';
                                }
                            }
                            _this.dirGrid.reload();
                            _this.dialog.close();
                            if(typeof void null!=typeof answer_json.Msg) {
                                if('' != answer_json.Msg){
                                    alert(answer_json.Msg);
                                }
                            }
                        });
                        _this.EvMan.subscribe('ToggleDirGridRowSelection',function(evName, p){
                            if(p._skey!==_selfCode) { return ; }
                            // {rowID:string,selected:boolean}
                            // надо проверить есть ли выделенные строки
                            var selRows = _this.dirGrid.getSelectedRows(),cnt=selRows.length,
                                $tB = _this.dirGrid.getGridToolBarEl(),
                                $btn = $tB.find('toolbar-btn[action="groupDelete"]');
                            // если строки есть то разблокировать кнопку группового удаления
                            if(0<cnt){
                                $btn.prop('disabled',false);
                                $btn.removeProp('disabled');
                            }else{
                                // если ниобной строки не отмечено кнопку надо заблокировать
                                $btn.prop('disabled',true);
                            }
                        });
                        _this.EvMan.subscribe('SelectTreePanelNode',function(evName, p){
                            // {dir:node}
                //            console.log(p.path);
                            var nWD = p.path.join('/').substr(1);
                            if(nWD!==_this.workDir){
                                _this.workDir = nWD;
                                _this.dirGrid.buildGrid();
                            }
                        });
                    }
                    _c();
                };
                // теперь относледуемся
                _jsUtils.inherit(cls,parent);
                return cls;
            }(PageBlock || _jsUtils.emptyFunc);
            if ('object' === typeof win && typeof function(){} === typeof win.funcFixMaincontentBoxHeight) {  win.funcFixMaincontentBoxHeight(); }
            $('body').find('div.maincontent:first').attr('id', 'NaviPageBox');

            // подключаем наш модуль по событию что приложение готово подключать модуль, так как аяксом запрашиваются данные о локализации
            if(typeof void null!==typeof Desktop && null!==Desktop){
                Desktop.EvMan.subscribe('CanRegBlocks',function(evName, args){
                    PortalFilesManager = new PortalFilesManager({'langData':args.langData['PortalFiles']});
                    PortalFilesManager.run({'place':$('body').find('div.maincontent:first'),
                        'label': 'Управление файлами портала',
                        'lang': 'ru',
                        'code': 'PortalFiles',
                        'targetBlkID': ''
                    });
                });
            }
        })(jQuery);
    }else{
        alert('jQuery portal administrative user files tool say: jQuery lib is not loaded');
    }
})(window);