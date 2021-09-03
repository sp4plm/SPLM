(function(win,undefined){
    if(typeof void null!==typeof jQuery){
        (function($){
            var _this = this,
                _selfCode = 'PortalUsers',
                wid = 'portal-users',
                gridBoxCls = 'jqgrid-box',
                gridCls = 'jqgrid-tbl',
                gridPgCls = gridCls+'-pg',
                gridTBCls = gridCls+'-tool',
                _$box,
                _$grid;

            _this.langData = null;
            _this.moduleData = null;
            _this.baseURL = '/users';
            _this.interface = {};
            _this.storage = {};
            _this._roles = [];
            _this.Grid = function(){
                var cls;
                cls = function(){
                    var _cls = this;

                    _cls.reload = function(){};
                    _cls.build = function(){};
                    _cls.init = function(){};
                };
                return new cls();
            }();

            _this.pswdMinLen = 8; // _this.langData.minPaswdLength;
            _this.loginMinLen = 8; // _this.langData.minLoginLength;
            _this.tmplEditForm = '';
            _this.tmplViewInfo = '';
            _this.EvMan = null;
            _this.dialog = null;
            _this.gridBoxID = wid+'-gridbox';
            _this.gridID = wid+'-grid';
            _this.gridPgID = wid+'-grid-pg';
            //gbox_portal-users-grid
            // создание таблицы jqGrid - freeGrid
            function _getGridCfg(){
                return {
                    mtype:'POST', url:'', datatype: 'json',
                    colModel:[],
                    rowNum:20, rowList:[5, 10, 20, 30, 50],
                    autowidth:true,
                    sortname: 'login', sortorder: 'ASC',
                    caption: '',
                    pager: '',
                    toolbar: [true,'top'],
                    jsonReader: { repeatitems : false },
                    viewrecords: true,
                    gridview: true
                };
            }

            _this.cookURL = function(){
                var bU = _this.baseURL + '/list';
                return bU;
            };

            _this.getColModel = function(){
                var row, cols=[];

                // {name:'amount',index:'amount', width:80, align:"right",sorttype:"float"},
                row = {'label': '-', 'name': 'toolbar', 'index':'toolbar'};
                row['searchoptions'] = {sopt:['cn','nc','eq','ne','bw','bn','ew','en']};
                row['sortable'] = false;
                row['align'] = 'right';
                row['sorttype'] = 'text';
                cols.push(row);
                row = {'label': 'Login', 'name': 'login', 'index':'login'};
                row['searchoptions'] = {sopt:['cn','nc','eq','ne','bw','bn','ew','en']};
                row['sortable'] = true;
                row['align'] = 'right';
                row['sorttype'] = 'text';
                cols.push(row);
                row = {'label': 'Email', 'name': 'email', 'index':'email'};
                row['searchoptions'] = {sopt:['cn','nc','eq','ne','bw','bn','ew','en']};
                row['sortable'] = true;
                row['align'] = 'right';
                row['sorttype'] = 'text';
                cols.push(row);
                row = {'label': 'Roles', 'name': 'roles', 'index':'roles'};
                row['searchoptions'] = {sopt:['cn','nc','eq','ne','bw','bn','ew','en']};
                row['sortable'] = true;
                row['align'] = 'right';
                row['sorttype'] = 'text';
                cols.push(row);
                row = {'label': 'ID', 'name': 'ID', 'index':'ID', 'hidden': true};
                cols.push(row);
                return cols;
            };

            _this.addRowToolbars = function(){
                var cN='toolbar',cnt=0,ids=_$grid.getDataIDs(),
                    kx=0,cell;
                cnt = ids.length;
                if(cnt>0){
                    // добавить в ячейку Toolbar
                    // для всех удалить и открыть и переименовать
                    for(kx=0;kx<cnt;kx++){
                        cell='';
                        cell = _this.cookRowToolbar();
                        _$grid.setCell(ids[kx],cN,cell);
                    }
                    _$grid.find('tr input.toolbar-row-selector').click(function(){
                        _this.EvMan.fire('ToggleGridRowSelection',{rowID:$(this).parent().parent().attr('id'),
                            selected:$(this).prop('checked'), _skey:_selfCode
                         });
                    });
                    _$grid.find('tr .toolbar-btn').click(function(){
                        _this.EvMan.fire('ClickGridRowToolbarBtn',{action:$(this).attr('action'),
                            rowID:$(this).parent().parent().attr('id'), _skey:_selfCode
                        });
                    });
                }
            };

            _this.buildGrid = function(){
                var $pager,
                    _cfg = _getGridCfg();
                //_this.remove();
                _cfg.colModel = _this.getColModel();
                _cfg.pager = '#'+_this.gridPgID;
                // создать урл для запросов на сервер
                _cfg.url = _this.cookURL();

                // Навесить события на тулбаре в каждой строке
                _cfg.loadComplete = function(){
                    _this.addRowToolbars();
                };
                // добавляем html элемент для пагинации
                if(''!==_cfg.pager){
                    $pager = $('<div></div>');
                    $pager.attr('id', _this.gridPgID);
                    $('#'+_this.gridID).after($pager);
                }

                _$grid = $('#'+_this.gridID).jqGrid(_cfg);
                if(''!==_cfg.pager){
                    _$grid.jqGrid('navGrid','#'+_this.gridPgID,{edit:false,add:false,del:false,search:false},{},
                        {},
                        {},
                        {multipleSearch:false, multipleGroup:false}
                    );
                }
                if(typeof void null!==typeof _cfg.toolbar && _cfg.toolbar[0]){
                    _this.cookToolbar();
                }
                //_this.resize();
            };
            // создание панели с кнопками для управления пользователями
            _this.cookToolbar = function(){
                var $tb = _this.getGridToolBarEl(),
                    lbl1 = 'Добавить пользователя',
                    lbl2 = '',
                    lbl3 = 'Удалить';
                $tb.append('<span class="ui-corner-all toolbar-btn" action="groupDelete" disabled="true"><span class="ui-icon ui-icon-trash"></span></span>');
                $tb.append('<span class="toolbar-delim"></span>');
                // кнопка "Создать пользователя"
                $tb.append('<span class="ui-corner-all toolbar-btn" action="addobject"><span class="ui-icon ui-icon-plus"></span></span>');
                // export
                $tb.append('<span class="ui-corner-all" style="float:right;clear:none;cursor:pointer;margin-right:4px;"><a href="/portal/users/export"><img src="/static/img/excel-icon16.gif" /></a></span>');

                $tb.find('.toolbar-btn').click(function(){ _this.EvMan.fire('ClickGridToolbarBtn',{action:$(this).attr('action'),$btn:$(this),_skey:_selfCode}); });
            };

            _this.getGridToolBarEl = function(){
                return $('#t_'+_this.gridID);
            };
            // функция вызова окна с формой создания пользователя

            // функция вызова окна с формой для редактирования пользователя

            // функция удаления пользователя

            // функция сохранения пользователя

             _this.cookRowToolbar = function(){
                var tb = '';
                tb += '<input type="checkbox" class="toolbar-row-selector" name="RowSelector[]" />';
                tb += '<span class="toolbar-delim"></span>';
    //                tb += '<span class="ui-corner-all toolbar-btn" action="open"><span class="ui-icon ui-icon-folder-open"></span></span>';
                tb += '<span class="ui-corner-all toolbar-btn" action="edit"><span class="ui-icon ui-icon-pencil"></span></span>';
                tb += '<span class="ui-corner-all toolbar-btn" action="remove"><span class="ui-icon ui-icon-trash"></span></span>';
                return tb;
            };

            _this.gridToolbarEvCatcher = function(eN, p){
                if(p._skey!==_selfCode) { return ; }
                switch(p.action){
                    case 'groupDelete':
                        // групповое удаление элементов на текущем уровне
        //                if(!p.$btn.prop('disabled')){ // почему-то в ИЕ 11 не возникает событие клик на чекбоксе
                            _this.deleteSelectedItems();
        //                }
                        break;
                    case 'addobject':
                        // открываем окно для загрузки файла(ов)
                        _this.dialog.open(_this.tmplEditForm,function($box){
                            // для начала надо заполнть роли как объекты формы
                            _this._roles = [];
                            _this.exportRoles(_this._roles,true);
                            _this.roles2form(_this._roles,$box.find('form[name="UserEditForm"]'));
                            _this.initEditDialog($box);
                        });
                        break;
                }
            };

            // функция установки событий для кнопок удаления, редактирования пользователей
            _this.gridRowToolbarEvCatcher = function(eN, p){
                if(p._skey!==_selfCode) { return ; }
                // p=> {action:'', rowID:'' }
                var row;
                row = _$grid.getRowData(p.rowID);
                //row['ID'] = p.rowID;
                switch(p.action){
                    case 'open':
                        _this.view(row);
                        break;
                    case 'edit':
                        // открываем окно для создания новой директории
                        _this.edit(row);
                        break;
                    case 'remove':
                        _this.delete(row);
                        break;
                }
            };
            /* uiDialog для работы с формами в диалогах */
            _this.dialog = function(k){
                var _cls = function(p){
                    var _1this = this,
                        _$dlg=null,
                        _$parent;
                    _1this.id = '';
                    _1this.id = p.id;
                    _1this.content = null;
                    _1this.editor = null;
                    _1this.build = function(){
                        var w=0,h=0,cfg,wa,pos;
                        if(0===_$parent.find('#'+_1this.id).length){
                            _$dlg = $('<div></div>');
                            _$dlg.attr('id',_1this.id);
        //                    _$dlg.hide();
                            _$parent.append(_$dlg);
                        }
                        wa = _this.getDialogWA();
                        w = Math.ceil(wa.w/2)-4; h = Math.ceil(wa.h/2)-4;
                        cfg = {title:'',
                                autoOpen: false,
                                modal: false,
                                open:function(){ _this.EvMan.fire('UserDialogOpen',{content:$(this),_skey:_selfCode}); },
                                beforeClose:function(){ _this.EvMan.fire('UserDialogBeforeClose',{content:$(this),_skey:_selfCode}); },
                                close:function(){ _this.EvMan.fire('UserDialogClose',{content:$(this),_skey:_selfCode}); }
                            };
                        if(w>0){ cfg.width = w; }
                        if(h>0){ cfg.height = h; }
                        if(typeof void null!=typeof wa.top && wa.top>0
                            && typeof void null!=typeof wa.left && wa.left>0){
                            cfg.position = [wa.left,wa.top];
                        }
                        _$dlg = _$dlg.dialog(cfg);
                    };
                    _1this.destroy = function(){
                        if(typeof void null!==typeof _$dlg && null!==_$dlg){
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
            };

            _this.toggleLockFrmButtons = function(lock,frm){
                if(win._jsTypes.tofU===typeof frm || null===frm){
                    //считаем что форма находиться в активном окне диалога
                    frm = tab.tabHtml.find('.user-edit-form:first');
                }
                lock = (win._jsTypes.tofU!==typeof lock)? 'enable':'disable';
                frm.find('.form-toolbar button').button(lock);
            };

            _this.save = function(form){
                var frm,frmData,_2send='',error='',
                    data={};
                data = _this.userFormToObject(form);
                error = _this.checkData(data);
                if(win._jsTypes.emptyStr!==error){
                    alert(error);
                    _this.toggleLockFrmButtons(1,form);
                    return;
                }
                $.post(_this.baseURL+'/save/',data,function(asn){
                    if(asn.state==200){
                        //_this.Grid.reload();
                        if(typeof void null!==typeof _$grid && null!==_$grid){
                            _$grid.trigger('reloadGrid');
                        }
                        _this.dialog.close();
                    }else{
                        alert(asn.Msg);
                    }
                },'json');
            };

            _this.checkMandFields = function(fields,isNU){
                // обязательно должны быть заполнены логин и пароль
                // а то пользователь не сможет войти
                var msg,mark,kx,cnt=0,manFields = ['Login','Password'],labels = {'Login':'Логин','Password':'Пароль'};
                cnt = manFields.length;
                mark = '#{field}';
                msg = 'Не заполнено обязательное поле "'+mark+'"!';
                msg = _this.langData.Errors['101']+' "'+mark+'"!';
                for(kx=0;kx<cnt;kx++){
                    if(!isNU && 'Password'===manFields[kx]){ continue; }
                    if(win._jsTypes.tofU===typeof fields[manFields[kx]] || win._jsTypes.tofS!==typeof fields[manFields[kx]] || win._jsTypes.emptyStr===fields[manFields[kx]]){
                        return msg.replace(new RegExp(mark),labels[manFields[kx]]);
                    }
                }
                return '';
            };

            _this.checkLogin = function(str){
                if(win._jsTypes.tofS!==typeof str || win._jsTypes.emptyStr===str || _this.loginMinLen>str.length){
                    return _this.langData.Errors['102'].replace(/#{field}/,_this.langData.interface.login)+'('+_this.loginMinLen+')!';
        //            return 'Поле "Логин" незаполнено или имеет неверный формат или количество символов меньше минимального('+_this.loginMinLen+')!';
                }
                return '';
            };

            _this.checkPswd = function(p1,p2,isNU){
                // сперва проверим что это строки и они не пустые
                var isEmpty = (win._jsTypes.tofS!==typeof p1 || win._jsTypes.emptyStr===p1 || win._jsTypes.tofS!==typeof p2 || win._jsTypes.emptyStr===p2);
                if(isNU && isEmpty){
                    return _this.langData.Errors['103'].replace(/#{field}/,_this.langData.interface.password);
        //            return 'Поле "Пароль" или его подтверждение незаполнено!';
                }
                if(!isNU && !isEmpty){
                    // теперь проверим что они одинаковые
                    if(p1!==p2){
                        return _this.langData.Errors['105'];
        //                return 'Пароль и Подтверждение пароля несовпадают!';
                    }
                }
                if(isNU){
                    // теперь проверим что они одинаковые
                    if(p1!==p2){
                        return _this.langData.Errors['105'];
        //                return 'Пароль и Подтверждение пароля несовпадают!';
                    }
                    // у а теперь надо проверить на минимальную длину
                    if(_this.pswdMinLen>p1.length){
                        return _this.langData.Errors['106']+' ('+_this.pswdMinLen+')!';
        //                return 'Длина пароля меньше минимальной('+$this.pswdMinLen+')!';
                    }
                }
                return '';
            };

            _this.checkEmail = function(str){
                // поскольку формат email завистит от почтового сервера, применяем лишь общий шаблон(regExp): .+@.+\..+
                if(win._jsTypes.tofS!==typeof str || win._jsTypes.emptyStr===str){
                    return _this.langData.Errors['104'].replace(/#{field}/,_this.langData.interface.email);
        //                    return 'Поле "Email" незаполнено!';
                }else{
                    var srv,at,msg = 'Не корректный формат email';
                    msg = _this.langData.Errors['107']+' '+_this.langData.interface.email;
                    // сперва разобьем на две части по @ так как это разделение имени пользователя от сервера
                    at = str.split('@');
                    if(!win._jsTypes.isArray(at) || at.length<2 || at.length>2){
                        return msg;
                    }
                    // проверим что обечасти не пустые
                    if(win._jsTypes.tofU===typeof at[0] || win._jsTypes.tofS!==typeof at[0] || win._jsTypes.emptyStr===at[0]){
                        return msg;
                    }
                    if(win._jsTypes.tofU===typeof at[1] || win._jsTypes.tofS!==typeof at[1] || win._jsTypes.emptyStr===at[1]){
                        return msg;
                    }
                    // теперь надо проверить сервер в общих чертах
                    // строка должна состоять как минимум из 2 доменов 1 и второго уровня - domen.rootDomen
                    srv = at[1].split('.');
                    if(!win._jsTypes.isArray(srv)){
                        return msg;
                    }
                    var cnt = srv.length;
                    if(win._jsTypes.tofU===srv[cnt-2] || win._jsTypes.tofS!==typeof srv[cnt-2] || win._jsTypes.emptyStr===srv[cnt-2]){
                        return msg;
                    }
                    if(win._jsTypes.tofU===srv[cnt-1] || win._jsTypes.tofS!==typeof srv[cnt-1] || win._jsTypes.emptyStr===srv[cnt-1]){
                        return msg;
                    }
                }
                return '';
            };

            _this.isNewUser = function(data){
                if(win._jsTypes.emptyStr===data.ID){
                    return true;
                }
                return 1>parseInt((data.ID+0));
            };

            _this.checkData = function(data){
                var msg = '';
                // сперва проверим все обязательные поля
                if(win._jsTypes.emptyStr===msg){
                    msg = _this.checkMandFields(data,_this.isNewUser(data));
                }
                // теперь проверим логин
                if(win._jsTypes.emptyStr===msg){
                    msg = _this.checkLogin(data.Login);
                }
                // теперь проверим пароль
                if(win._jsTypes.emptyStr===msg){
                    msg = _this.checkPswd(data.Password,data.PasswordCheck,_this.isNewUser(data));
                }
                // теперь проверим email
                if(win._jsTypes.emptyStr===msg){
                    msg = _this.checkEmail(data.Email);
                }
                return msg;
            };

            _this.Grid_delRow = function(rID){
                var t;
                if(typeof void null!=typeof rID && null!==rID){
                    _$grid.delRowData(rID);
                    // надо проверить если строка была последней, но надо перезагрузить таблицу
                    t = _$grid.getRowData();
                    if(0===t.length){
                        _$grid.trigger('reloadGrid');
                    }
                }else{
                    _$grid.clearGridData();
                }
            };

            _this.delete = function(data,fromForm){
                if(typeof void null==data.ID || ''===data.ID){ return; }
                if(typeof void null===typeof fromForm || null===fromForm){ fromForm = false; }else{ fromForm = (fromForm); }
                if(!confirm('Выдействительно хотите удалить пользователя "' + data.name + '"?')) {
                    return;
                }
                $.get(_this.baseURL+'/delete/'+data.ID,null,function(dna){
                    if(dna.state==200){
                        if(fromForm){
                            //_this.Grid.reload();
                            if(typeof void null!==typeof _$grid && null!==_$grid){
                                _$grid.trigger('reloadGrid');
                            }
                            _this.dialog.close();
                        }else{
                            _this.Grid_delRow(data.ID);
                        }
                    }else{
                        alert(dna.Msg);
                    }
                },'json');
            };

            _this.edit = function(data){
                _this._roles = [];
                _this.exportRoles(_this._roles,true);
                $.post(_this.baseURL+'/getInfo/',data,function(ned){
                    _this.dialog.open(_this.tmplEditForm,function($box){
                        var $frm = $box.find('form[name="UserEditForm"]'),kx=0,cnt=0;
                        _this.storage['user-'+data.ID] = ned.data;
                        $frm.find('input[name="ID"]').val(ned.data.id);
                        $box.find('.input-text[name="FIO"]').val(ned.data.name);
                        $box.find('.input-text[name="Login"]').val(ned.data.login);
                        $box.find('.input-email[name="Email"]').val(ned.data.email);
                        _this.roles2form(_this._roles,$frm);
                        if(win._jsTypes.isArray(ned.data.roles)){
                            cnt = ned.data.roles.length;
                            if(cnt>0){
                                var uri = '';
                                // здесь мы будем отмечать те роли которые у нас уже установлены
                                for(kx=0;kx<cnt;kx++){
                                    uri = 'roles-'+ned.data.roles[kx].id;
                                    $frm.find('.link-item .input-checkbox[value="'+uri+'"]').prop('checked',true);
                                }
                            }
                        }
                        _this.initEditDialog($box);
                    });
                },'json');
            };
            _this.view = function(data){
                _this._roles = [];
                // win._jsTypes.UserRolesManager.exportRoles(_this._roles,true);
                _this.exportRoles(_this._roles,true);
                $.post(_this.baseURL+'/getInfo/',data,function(ned){
                    _this.dialog.open(_this.tmplViewInfo,function($box){
                        $box.find('tr[field="FIO"] .form-field-data').html(ned.data.name);
                        $box.find('tr[field="Login"] .form-field-data').html(ned.data.login);
                        $box.find('tr[field="Email"] .form-field-data').html(ned.data.email);
                        $box.find('tr[field="Roles"] .form-field-data').html(_this.roles2list(ned.data.roles));
                        _this.initEditDialog($box);
                    });
                },'json');
            };

            _this.deleteSelectedItems = function(){
                var url = _this.baseURL+'/removeSelection',
                    selRows = _this.Grid.getSelectedRows(),
                    cnt=selRows.length,kx=0,
                    data = {items:[]};
                for(kx=0;kx<cnt;kx++){
                    data.items.push(selRows[kx]);
                }
                $.post(url,data,function(rnA){
                    if(rnA.State==200){
                        _this.Grid.reload();
                    }else{
                        alert(rnA.Msg);
                    }
                },'json');
            };

            _this.roles2list = function(roles){
                var kx,cnt=0,list='';
                cnt = roles.length;
                if(0<cnt){
                    for(kx=0;kx<cnt;kx++){
                        list += roles[kx].name;
                        if(kx<(cnt-1)){
                            list += ', ';
                        }
                    }
                }
                return list;
            };

            _this.roles2form = function(roles,$frm){
                var $ul,kx=0,cnt=0,list='';
                if(win._jsTypes.isArray(_this._roles)){
                cnt = roles.length;
                if(0<cnt){
                        if(0===$frm.find('tr[field="Roles"] .form-field-data .field-ui-wrp .link-items-list').length){
                            $ul = $('<ul class="link-items-list items-edit-list" style="margin:10px;"></ul>');
                            $frm.find('tr[field="Roles"] .form-field-data .field-ui-wrp').append($ul);
                        }else{
                            $ul = $frm.find('tr[field="Roles"] .form-field-data .field-ui-wrp .link-items-list');
                            $ul.html('');
                        }
                        for(kx=0;kx<cnt;kx++){
                            $ul.append('<li class="link-item"><input class="input-checkbox" type="checkbox" name="Roles[]" value="'+_this._roles[kx]._tbl+'-'+_this._roles[kx].ID+'"/><span class="link-item-label">'+_this._roles[kx].Name+'</span></li>');
                        }
                    }
                }
                return list;
            };

            _this.shortFIO = function(fio){
                var str,m = fio;
                m = m.split(' ');
                str = '';
                if(win._jsTypes.tofS===typeof m[0] && win._jsTypes.emptyStr!==m[0]){ str += m[0]; }
                if(win._jsTypes.emptyStr!==str){ str += ' '; }
                if(win._jsTypes.tofS===typeof m[1] && win._jsTypes.emptyStr!==m[1]){ str += m[1].substring(0,1)+'.'; }
                if(win._jsTypes.tofS===typeof m[2] && win._jsTypes.emptyStr!==m[2]){ str += m[2].substring(0,1)+'.'; }
                return (win._jsTypes.tofS!==typeof str || win._jsTypes.emptyStr===str)? fio:str;
            };
            _this.exportUsers = function(point,sync,callback){
                if(!win._jsTypes.isArray(point) && win._jsTypes.tofF!==typeof callback){
                    throw new Error(_this.langData.Errors['108']);
                }
                var url,func,format='json';
                if(_agrigator.tofU===typeof sync){
                    sync = false;
                }
                url = _this.baseURL + '/getList';
                func = function(ans){
                    if(sync){
                        ans = win._jsUtils.oJSON.parse(ans.responseText);
                    }
                    if(!win._jsTypes.isUndefined(ans)){
                        if(200==ans.state){
                            var kx=0,cnt=0;
                            cnt = ans.data.length;
                            if(cnt>0){
                                for(kx=0;kx<cnt;kx++){
                                    point.push({ID:ans.data[kx].id,Name:_this.shortFIO(ans.data[kx].name),'_tbl':'users','_otype':'user'});
                                    ans.data[kx]['_tbl'] = 'users';
                                    ans.data[kx]['_otype'] = 'user';
                                }
                            }
                            if(win._jsTypes.tofF===typeof callback){
                                callback(ans.data);
                            }
                        }else{
                            alert(ans.msg);
                        }
                    }
                };
                if(sync){
                     $.ajax({'url': url, 'type': 'POST', 'data': {}, 'dataType': format, 'async':!sync,'cache':false, 'complete':func });
                }else{
                    $.post(url,{},func,format);
                }
            };

            _this.exportRoles = function(point,sync,callback){
                if(!win._jsTypes.isArray(point) && win._jsTypes.tofF!==typeof callback){
                    throw new Error(_this.langData.Errors['100']);
                }
                var url,func,format='json';
                if(win._jsTypes.tofU===typeof sync){
                    sync = false;
                }
                url = _this.baseURL + '/roles/getList';
                func = function(ans){
                    if(sync){
                        ans = win._jsUtils.oJSON.parse(ans.responseText);
                    }
                    if(!win._jsTypes.isUndefined(ans)){
                        if(200==ans.state){
                            var kx=0,cnt=0;
                            cnt = ans.data.length;
                            if(cnt>0){
                                for(kx=0;kx<cnt;kx++){
                                    point.push({ID:ans.data[kx].id,Name:ans.data[kx].name,'_tbl':'roles','_otype':'role'});
                                    ans.data[kx]['_tbl'] = 'roles';
                                    ans.data[kx]['_otype'] = 'role';
                                }
                            }
                            if(win._jsTypes.tofF===typeof callback){
                                callback(ans.data);
                            }
                        }else{
                            alert(ans.msg);
                        }
                    }
                };
                if(sync){
                     $.ajax({'url': url, 'type': 'POST', 'data': {}, 'dataType': format, 'async':!sync,'cache':false, 'complete':func });
                }else{
                    $.post(url,{},func,format);
                }
            }

            _this.getRoles= function(){
                _this._roles = [];
                $.post(_this.baseURL + '/roles/getList',{},function(ans){
                    if(!win._jsTypes.isUndefined(ans)){
                        if(ans.state==200){
                            var kx=0,cnt=0;
                            cnt = ans.data.length;
                            if(cnt>0){
                                for(kx=0;kx<cnt;kx++){
                                    _this._roles.push({ID:ans.data[kx].id,Name:ans.data[kx].name,id:ans.data[kx].id,name:ans.data[kx].name,'_tbl':'roles','_otype':'role'});
                                }
                            }
                            //_this.buildRolesList();
                        }else{
                            alert(ans.msg);
                        }
                    }
                },'json');
                // _this._roles.push({ID:3,Name:'Role 2'});
            };

            _this.userFormToObject = function($frm){
                var o={};
                o = win._jsUtils.fToObj($frm.get(0));
                return o;
            };


            _this.initEditDialog = function($box){
        //        $box.find('form:first .form-tbl').css({width:'100%'});
        //        $box.find('.input-text[name="PubDate"]').datepicker({
        //            dateFormat:'dd.mm.yy',
        //            showOn: 'button',
        //            buttonImage: '/img/calendar.png',
        //            buttonImageOnly: true
        //        });
                $box.find('.close-btn:first').click(function(){ _this.dialog.close(); });
                $box.find('.save-btn:first').click(function(){ _this.save($(this.form)); });
                $box.find('.del-btn:first').click(function(){ _this.delete({ID:this.form.elements['ID'].value},true); });

                $box.find('.form-toolbar button').button();
            };
            /* uiDialog для работы с формами в диалогах */

            _this.getDialogWA = function(){
                var wa={w:0,h:0};
                wa = _this.getContentWorkArea();
                return wa;
            };

            _this.getGridWorkArea = function(){
                var wa={w:0,h:0,top:0,left:0},pos;
                wa.w = $('#gbox_'+_this.gridID).outerWidth(true);
                wa.h = $('#gbox_'+_this.gridID).outerHeight(true);
                pos = $('#gbox_'+_this.gridID).offset();
                wa.top = pos.top;
                wa.left = pos.left;
                return wa;
            };

            _this.getContentWorkArea = function(){
                var wa={w:0,h:0,top:0,left:0},pos;
                wa.w = _$box.outerWidth(true);
                wa.h = _$box.outerHeight(true);
                pos = _$box.offset();
                wa.top = pos.top;
                wa.left = pos.left;
                return wa;
            };

            // constructor level straight down

            // инициализируем менеджер событий, для взаимодействия
            _$box = $('.maincontent:first');
            try{
                _this.EvMan = new win._custEvents();
            }catch(err){
                alert(err.toString());
                return ;
            }

            // надо загрузить данные для модуля
            $.get(_this.baseURL+'/getModuleData/',null,function(amd){
                _this.moduleData = amd;
                _this.langData = amd;
                _this.dialog = _this.dialog({id:'pu-dialog'});
                //_this.Grid = _this.Grid({id:'user-register'});
                 _this.buildGrid();
                 _this.dialog.init();
            },'json');

            // надо загрузить роли первичные
            _this.exportRoles(_this._roles,true);;

            _this.tmplEditForm = '';
            $.get(_this.baseURL+'/dialog/edit', null, function(answ){
                _this.tmplEditForm = answ;
                //_this.dialog.init();
            }, 'html');
            _this.tmplViewInfo = '';
            $.get(_this.baseURL+'/dialog/view', null, function(answ){
                _this.tmplViewInfo = answ;
            }, 'html');

            _this.EvMan.subscribe('ClickGridToolbarBtn',_this.gridToolbarEvCatcher);
            _this.EvMan.subscribe('ClickGridRowToolbarBtn',_this.gridRowToolbarEvCatcher);
            _this.EvMan.subscribe('ToggleDirGridRowSelection',function(eN, p){
                if(p._skey!==_selfCode) { return ; }
                // {rowID:string,selected:boolean}
                // надо проверить есть ли выделенные строки
                var selRows = _$grid.getSelectedRows(),cnt=selRows.length,
                    $tB = _this.getGridToolBarEl(),
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
            // инициализация механизма
            // _this.buildGrid();
            // _this.dialog = _this.dialog({id:'pu-dialog'});
            // _this.dialog.init();
        })(jQuery);
    }else{
        alert('jQuery portal administrative user tool say: jQuery lib is not loaded');
    }
})(window);