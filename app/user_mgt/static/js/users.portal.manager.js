var _PortalUsersManagerCls = function(p){
    var _this = this,
        _selfCode = 'PortalUsers1',
        _isInit = false,
        _initTO = null,
        _agrigator = p.container, // куда встраивается наш модуль
        _EvMan = _agrigator[p.eventBus], // менеджер событий объекта в который встраивается наш модуль
        _$box=null;
    // вызов родительского конструктора
    _PortalUsersManagerCls.superclass.constructor.call(_this,p.constructorParams);
    _this.langData = null;
    if(typeof void null!=typeof p.constructorParams && null!==p.constructorParams){
        _this.langData = (typeof void null!=typeof p.constructorParams.langData && null!==p.constructorParams.langData)? p.constructorParams.langData:null;
    }

    _this.loader = null;
    _this.header = '';
    _this.viewTmpl = '';
    _this.blkBox = null;
    _this.baseURL = '/portal/users';
    _this.moduleData = null;
    _this.textEditor = null;
    _this.windowManager = null;
    _this.interface = {};
    _this.storage = {};
    _this.pswdMinLen = _this.langData.minPaswdLength;
    _this.loginMinLen = _this.langData.minLoginLength;

    _this.tmplEditForm = '\
            <div class="form-box user-edit-formBox">\
                <form name="UserEditForm" class="edit-form user-edit-form" method="post" onsubmit="return false;">\
                    <input type="hidden" name="ID" value="" />\
                    <input type="hidden" name="TYPE" value="" />\
                    <input type="hidden" name="Roles[]" value="" />\
                    <table class="form-tbl">\
                        <tbody>\
                            <tr field="FIO">\
                                <td class="form-field-label">'+_this.langData.interface.fio+'</td>\
                                <td class="form-field-data">\
                                    <div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp">\
                                        <input type="text" class="input-text" name="FIO" value="" />\
                                    </div>\
                                </td>\
                            </tr>\
                            <tr field="Login">\
                                <td class="form-field-label">'+_this.langData.interface.login+'</td>\
                                <td class="form-field-data">\
                                    <div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp">\
                                        <input type="text" class="input-text" name="Login" value="" />\
                                    </div>\
                                </td>\
                            </tr>\
                            <tr field="Password">\
                                <td class="form-field-label">'+_this.langData.interface.password+'</td>\
                                <td class="form-field-data">\
                                    <div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp">\
                                        <input type="password" class="input-password" name="Password" value="" />\
                                    </div>\
                                    <div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp password-field">\
                                        <input type="password" class="input-password" name="PasswordCheck" value="" />\
                                    </div>\
                                </td>\
                            </tr>\
                            <tr field="Email">\
                                <td class="form-field-label">'+_this.langData.interface.email+'</td>\
                                <td class="form-field-data">\
                                    <div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp">\
                                        <input type="text" class="input-email" name="Email" value="" />\
                                    </div>\
                                </td>\
                            </tr>\
                            <tr field="Roles">\
                                <td class="form-field-label">'+_this.langData.interface.roles+'</td>\
                                <td class="form-field-data"><div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp"></div></td>\
                            </tr>\
                        </tbody>\
                    </table>\
                    <div class="toolbar form-toolbar">\
                        <button name="CloseUserFormBtn" class="toolbar-btn close-btn user-close-btn">'+_this.langData.interface.close+'</button>\
                        <button name="SaveUserDataBtn" class="toolbar-btn save-btn user-save-btn">'+_this.langData.interface.save+'</button>\
                        <button name="DeleteUserBtn" class="toolbar-btn del-btn user-del-btn">'+_this.langData.interface.delete+'</button>\
                    </div>\
                </form>\
            </div>\
            ';
            _this.tmplViewInfo = '<table class="view-tbl">\
                        <tbody>\
                            <tr field="FIO">\
                                <td class="form-field-label">'+_this.langData.interface.fio+'</td><td class="form-field-data"></td>\
                            </tr>\
                            <tr field="Login">\
                                <td class="form-field-label">'+_this.langData.interface.login+'</td><td class="form-field-data"></td>\
                            </tr>\
                            <tr field="Email">\
                                <td class="form-field-label">'+_this.langData.interface.email+'</td><td class="form-field-data"></td>\
                            </tr>\
                            <tr field="Roles">\
                                <td class="form-field-label">'+_this.langData.interface.roles+'</td><td class="form-field-data"></td>\
                            </tr>\
                        </tbody>\
                    </table>';

    /******************* Widgets ***************************/
    _this.widgets = {};
    _this.tabs = null;
    _this.grid = null;
    _this.tabsW = new Function();
    _this.gridW = new Function();
    _this.winW = new Function();
    _this.tabsW.wO = null;
    _this.tabsW.html = null;
    _this.gridW.wO = null;
    _this.gridW.html = null;
    _this.winW.wO = null;
    _this.winW.html = null;

    /**************** tabs functions [ *******************/
        _this.tabsW.init = function(){
            this.tabsItems = [];
            this.cls = 'ui-tabs-list';
            this.tmpl = '<ul></ul>';
            this.itemCls = 'ui-tab'
            this.itemLabelCls = 'tab-label'
            this.itemTmpl = '<li><a href="#{href}">#{label}</a></li>';
            this.tmplCloseBtn = '<span class="tab-close ui-icon ui-icon-close">&nbsp;</span>';
            this.currentTab = {navi:null,panel:null};
        };

        _this.tabsW.create = function(cfg){
            var _wgt = this;
            this.tabsNavi = $(this.tmpl);
            this.tabsNavi.addClass(this.cls);
            this.html = cfg.target;
            this.html.append(this.tabsNavi);
            this.wO = this.html.tabs(cfg.plugin);
            this.tabsNavi.on('click','.tab-close',function(){
                _wgt.closeTab(this);
            });
        };

        _this.tabsW.resize = function(){
            var p1,parent,pW,pH,dW,dH,pdW,pdH;
            if(_agrigator.tofU!==typeof this.tabsNavi){
                parent = _this.tabsW.tabsNavi.parent();
                p1 = parent.find('.ui-tabs-panel:first');
                dW = p1.outerWidth(true)-p1.width();
                dH = p1.outerHeight(true)-p1.height();
                pdW = parent.outerWidth(true)-parent.width();
                pdH = parent.outerHeight(true)-parent.height();
                pH = parent.height()-_this.tabsW.tabsNavi.outerHeight(true)-parent.find('.header-footer:first').outerHeight(true)-dH;
                pW = parent.width()-pdW-dW;
                parent.find('.ui-tabs-panel').width(pW);
                parent.find('.ui-tabs-panel').height(pH);
            }
        };

        _this.tabsW.genID = function(){
            return 'tab-'+(new Date().getTime());
        };

        _this.tabsW.addTab = function(data){
            var ID = this.genID(),
                pane = $('<div id="' + ID + '"></div>'),
                li = $(this.itemTmpl.replace(/#\{href\}/g, '#'+ID).replace(/#\{label\}/g, '<span class="'+this.itemLabelCls+'">'+data.label+'</span>'));
            li.addClass(this.itemCls);
            li.attr('code',ID);
            if(data.isClosable){
                li.append(this.tmplCloseBtn);
            }
            this.tabsNavi.append( li );
            this.html.append( pane );
            this.wO.tabs( 'refresh' );
            data['tabID'] = ID;
            _EvMan.fire('addTab',{tabD:data,tabN:li,tabHtml:pane});
            this.openLast();
            return ID;
        };

        _this.tabsW.openTab = function(idy){
            var index,cnt=0,isIndex = (_agrigator.tofN===typeof idy && -1<idy),
            isID = (_agrigator.tofS===typeof idy && _agrigator.emptyStr!==idy);
            if(isID){
                this.tabsNavi.find('li.'+this.itemCls).each(function(i){
                    if($(this).attr('code')===idy){
                        index = i; return false;
                    }
                });
            }
            if(isIndex){
                index = idy;
            }
            index = parseInt(index);
            if(_agrigator.tofN!==typeof index){
                throw new Error(_this.langData.Errors[100].replace(/#{id}/,index));
            }
            cnt = this.tabsNavi.find('li.'+this.itemCls).length;
            if(0>index || (cnt-1)<index){
                throw new Error(_this.langData.Errors[100].replace(/#{id}/,index));
            }
            this.wO.tabs( 'option' ,'active', index);
        };
        _this.tabsW.closeTab = function(idy){
            var panelId,label,li;
            li = ($(idy).hasClass(this.itemCls))? idy:$(idy).parents( 'li:first' );
            label = li.find('.'+this.itemLabelCls).html();
            panelId = li.remove().attr( 'aria-controls' );
            $( '#' + panelId ).remove();
            this.wO.tabs( 'refresh' );
            _EvMan.fire('closeTab',{tabD:{'ID':panelId,'label':label},tabN:null,tabHtml:null});
        };
        _this.tabsW.openFirst = function(){
            this.wO.tabs( 'option' ,'active', 0);
        };
        _this.tabsW.openLast = function(){
            var cnt = this.tabsNavi.find('li.'+this.itemCls).length;
            this.wO.tabs( 'option' ,'active', cnt-1);
        };
        _this.tabsW.searchTab = function(id,o){
            var kx, li, panel;
            o = (_agrigator.tofN===typeof o && 1===o);
            this.tabsNavi.find('li.'+this.itemCls).each(function(i){
                if($(this).attr('code')===id){
                    kx=i;
                    if(o){
                        li = $(this);
                        panel = $('#'+$(this).attr('code'));
                    }
                    return false;
                }
            });
            return (!o)? kx:{tabN:li,tabHtml:panel,tabInd:kx};
        };

        _this.tabsW.getCurrentTab = function(){
            var li,panel,i;
            li = this.tabsNavi.find('li.'+this.itemCls+'.ui-tabs-active');
            panel = $('#'+li.attr('code'));
            i = li.attr('tabindex');
            return {tabN:li,tabHtml:panel,tabInd:i};
        };

        _this.tabsW.getTabID = function(li){ return $(li).attr('code'); };
        /**************** tabs functions ] *******************/
        _this.tabsW.init();
        
            /**************** grid functions [ *******************/
        _this.gridW.init = function(){
            this.gridCls = 'jstbl';
            this.gridBoxCls = 'jstbl-box';
            this.html = $('<table></table>');
            this.html.addClass(this.gridCls);
            this.gridBox = $('<div></div>');
            this.gridBox.addClass(this.gridBoxCls);
            this.gridBox.append(this.html);
            this.tmplRowToolbar = '<div class="row-toolbar" style="width:60px;height:20px;"></div>';
        };

        _this.gridW.create = function(cfg){
            cfg.target.append(this.gridBox);
            this.wO = this.html.dataTable(cfg.plugin);
            this.initRowToolbar();
            this.resize();
        };

        _this.gridW.initRowToolbar = function(){
            _this.gridW.html.on('click','.view-usr',function(){ _this.viewUser(this); });
            _this.gridW.html.on('click','.edit-usr',function(){ _this.editUser(this); });
            _this.gridW.html.on('click','.del-usr',function(){ _this.delUser(this); });
        };

        _this.gridW.addRowToolbar = function(){
            this.html.find('tbody tr').each(function(ix){
                _this.gridW.addTollbar2Row(this);
            });
        };

        _this.gridW.addToolbar2Row = function(tr){
            if($($(tr).find('td')[0]).find('.row-toolbar').length===0){
                var tt = $(this.tmplRowToolbar);
                tt.append('<span class="act-btn ui-state-default ui-corner-all"><span class="view-usr ui-icon ui-icon-newwin"></span></span>');
                tt.append('<span class="act-btn ui-state-default ui-corner-all"><span class="edit-usr ui-icon ui-icon-pencil"></span></span>');
                tt.append('<span class="act-btn ui-state-default ui-corner-all"><span class="del-usr ui-icon ui-icon-trash"></span></span>');
                $($(tr).find('td')[0]).append(tt);
            }
        };

        _this.gridW.resize = function(){
            var wD,hD,cdW,cdH,container = this.gridBox.parent(),
            cdW = container.outerWidth(true)-container.width();
            cdH = container.outerHeight(true)-container.height();
            wD = this.gridBox.outerWidth(true)-this.gridBox.width(),
            hD = this.gridBox.outerHeight(true)-this.gridBox.height();
            container.children().each(function(){
                if($(this)!==this.gridBox){
                    hD += $(this).outerHeight(true);
                }
            });
            this.gridBox.width(container.width()-wD);
            this.gridBox.height(container.height()-hD);
            // далее можно вставить вызов ресайза самого плагина который используется для работы с таблицей
        };

        _this.gridW.addRow = function(data){
            data['Actions'] = '';
            data['DT_RowId'] = 'udr-'+data.ID;
            data['DT_RowClass'] = 'udata'
            this.wO.fnDraw();
            // теперь надо установить идентификатор строки
            _EvMan.fire('addRow',data);
        };

        _this.gridW.getEmptyRowObject = function(){
            var colsCfg, kx, o = {}, cnt=0,cName='',
            oSettings = this.wO.fnSettings();
            colsCfg = oSettings.aoColumns;
            cnt = colsCfg.length;
            for(kx=0;kx<cnt;kx++){
                cName = colsCfg[kx]['sName'];
                o[cName] = '';
            }
            return o;
        };

        _this.gridW.delRow = function(idy){
            var data,tr;
            tr = (_agrigator.tofS===typeof idy && _agrigator.emptyStr!==idy)? $('#'+idy):idy;
            data = this.rowToObj(tr);
            $(tr).find('.row-toolbar').remove();
            $(tr).remove();
            data['plaginData'] = this.wO.fnDeleteRow(this.getRowIndex($(tr).get(0)));
            this.wO.fnDraw();
            _agrigator.EvMan.fire('deleteRow',data);
        };

        _this.gridW.getRowIndex = function(tr){
            var i = 0;
            this.html.find('tr').each(function(i){
                if($(tr).attr('id')===$(this).attr('id')){
                    return false;
                }
            });
            return i;
        };

        _this.gridW.getRowID = function(row){
            return $(row).attr('id');
        };

        _this.gridW.getRowByBTN = function(btn){
            return $(btn).parents('td:first').parent();
        };

        _this.gridW.rowToObj = function(row){
            var colsCfg, kx, rO, o = {}, cnt=0,cCls='',cName='',
            oSettings = this.wO.fnSettings();
            colsCfg = oSettings.aoColumns;
            cnt = colsCfg.length;
            rO = this.wO.fnGetData(row.get(0));
            for(kx=0;kx<cnt;kx++){
                cCls = colsCfg[kx]['sClass'];
                cName = colsCfg[kx]['sName'];
                o[cName] = (0===row.find('td.'+cCls).length)? rO[cName]:row.find('td.'+cCls).html();
            }
            return o;
        };
        /**************** grid functions ] *******************/
        _this.gridW.init();
        
        /**************** win functions [ *******************/
        /**************** win functions ] *******************/

/******************* Widgets ] ***************************/
        _this._roles = [];
        _this.resize = function(){
            if(null!==_$box){
                // теперь надо установить такой размер для страницы чтобы на него могли положиться вычисления для самой страницы
                var wD = _$box.outerWidth(true)-_$box.width();
                var hD = _$box.outerHeight(true)-_$box.height();
                _$box.width(_this.blkBox.width()-wD);
                _$box.height(_this.blkBox.height()-hD);
                _this.tabsW.resize();
                _this.gridW.resize();
            }
        };
        _this.isUserTab = function(tabID){
            var kx;
            for(kx in _this.interface.Opened){
                if(null===_this.interface.Opened[kx].tab) continue;
                if(tabID===_this.interface.Opened[kx].tab){
                    return true;
                }
            }
            return false;
        };
        _this.viewUser = function(btn){
            var tr,trData;
            // получаем данные о выбранном пользователе
            tr = _this.gridW.getRowByBTN(btn);
            trData = _this.gridW.rowToObj(tr);
            // отправляем запрос на сервер о дополнительных данных
            // открываем окно с информацие о выбранном пользователе
            var dialog,dID = 'userInfoWin';
            if(0===_$box.find('#'+dID).length){
                dialog = $('<div style="display:none;"></div>');
                dialog.attr('id', dID);
                dialog.html($this.tmplViewInfo);
                _$box.append(dialog);
            }
            function closeDialog(){
                // здесь будем чистить :)
                $(this).find('tr[field="FIO"] .form-field-data').html('');
                $(this).find('tr[field="Login"] .form-field-data').html('');
                $(this).find('tr[field="Email"] .form-field-data').html('');
                $(this).find('tr[field="Roles"] .form-field-data').html('');
            }
            $.post('/portal/users/getInfo',{'ID':trData.ID},function(ans){
                if(!_agrigator.isUndefined(ans)){
                    if(200==ans.state){
                        dialog = $('#'+dID).dialog({
                            title:$this.langData.interface.user+' :: '+trData.FIO,
                            autoOpen: false,
                            modal: false,
                            open: function(){
                                // здесь будем добавлять наш хтмл с описанием пользователя
                                $(this).find('tr[field="FIO"] .form-field-data').html(ans.data.name);
                                $(this).find('tr[field="Login"] .form-field-data').html(ans.data.login);
                                $(this).find('tr[field="Email"] .form-field-data').html(ans.data.email);
                                var roles = '';
                                if(_agrigator.isArray(ans.data.roles)){
                                    var kx,cnt=0;
                                    cnt = ans.data.roles.length;
                                    if(0<cnt){
                                        for(kx=0;kx<cnt;kx++){
                                            roles += ans.data.roles[kx].name;
                                            if(kx<(cnt-1)){
                                                roles += ', ';
                                            }
                                        }
                                    }
                                }
                                $(this).find('tr[field="Roles"] .form-field-data').html(roles);
                            },
                            close: closeDialog
                        });
                        dialog.dialog('open');
                    }else{ alert(ans.msg); }
                }
            },'json');
        };
        _this.editUser = function(btn){
            var tabO,idy;
            _this._roles = [];
            _agrigator.UserRolesManager.exportRoles($this._roles,true);
            if(typeof void null!==typeof btn){
                // получим строку
                var rowID,uID,rowData,$tr;
                $tr = _this.gridW.getRowByBTN(btn);
                // надо получить идентификатор пользователя
                rowID = _this.gridW.getRowID($tr);
                uID = rowID.replace(/udr-/,'');
                rowData = _this.gridW.rowToObj($tr);
                // затем собрать данные для таба
                idy = 'User-'+rowData.ID;
                tabO = {'ID':idy,'label':rowData.FIO,isClosable:true};
            }else{
                idy = 'User-n'+(new Date().getTime());
                tabO = {'ID':idy,'label':_this.langData.interface.newUser,isClosable:true};
            }
            if(_agrigator.tofU===typeof _this.interface.Opened[idy]){
                _this.interface.Opened[idy] ={tab:null,win:null};
            }
            if(null===_this.interface.Opened[idy].tab){
                _this.interface.Opened[idy].tab = _this.tabsW.addTab(tabO);
                if(0<parseInt(uID)){
                    // теперь нужно отправить запрос на сервер для получения данных о пользователе
                    $.post('/portal/users/getInfo',{'ID':uID},function(ans){
                        if(!_agrigator.isUndefined(ans)){
                            if(ans.state==200){
                                _this.storage['user-'+uID] = ans.data;
                            }else{
                                alert(ans.msg);
                            }
                        }
                    },'json');
                }
            }else{
                _this.tabsW.openTab(_this.interface.Opened[idy].tab);
            }
            _this.toggleLockFrmButtons(1);
        };

        _this.toggleLockFrmButtons = function(lock,frm){
            if(_agrigator.tofU===typeof frm || null===frm){
                var tab;
                //считаем что форма находиться в активном табе
                tab = _this.tabsW.getCurrentTab();
                frm = tab.tabHtml.find('.user-edit-form:first');
            }
            lock = (_agrigator.tofU!==typeof lock)? 'enable':'disable';
            frm.find('.form-toolbar button').button(lock);
        };

        _this.delUser = function(btn){
            var tr,trData,q = _this.langData.Msgs.del;
            tr = _this.gridW.getRowByBTN(btn);
            trData = _this.gridW.rowToObj(tr);
            // спрашиваем действительно ли хотят удалить пользователя
            if(confirm(q+' "'+trData.FIO+'"?')){
                // если да, то отправляем запрос на сервер
                $.post('/portal/users/delete',{ID:trData.ID},function(ans){
                    if(!_agrigator.isUndefined(ans)){
                        if(ans.state==200){
                            // в случае успешного удаления данных на сервере удаляем строку в таблице
                            _this.gridW.delRow(tr);
                        }else{
                            alert(ans.msg);
                        }
                    }
                },'json');
            }
        };

        _this.delUserFromForm = function(btn){
            // предполагаем что мы нажались в активном табе :)
            var frm,frmData,uID,tabID,
            q = _this.langData.Msgs.del,
            tab = _this.tabsW.getCurrentTab();
            _this.toggleLockFrmButtons();
            if(confirm(q+' "'+tab.tabN.find('.'+_this.tabsW.itemLabelCls).html()+'"?')){
                frm = tab.tabHtml.find('.user-edit-form:first');
                frmData = _this.userFormToObject(frm);
                uID = frmData.ID;
//                    alert(_agrigator.oJSON.make(frmData));
                // для тестирования
                if((!(0<parseInt(uID)))){
                    tabID = _this.tabsW.getTabID(tab.tabN);
                    uID = _this.getUkeyByTab(tabID);
                    uID = uID.split('-');
                    uID = uID[1];
                }
                $.post('/portal/users/delete',{ID:uID},function(ans){
                    if(!_agrigator.isUndefined(ans)){
                        if(ans.state===200){
                           var trID = 'udr-'+uID;
                            _this.gridW.delRow(trID); // удаляем строку из таблицы
                            _this.tabsW.closeTab(tab.tabN); // закрываем таб
                        }else{
                            alert(ans.msg);
                        }
                    }
                },'json');

            }
            _this.toggleLockFrmButtons(1);
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
                if(_agrigator.tofU===typeof fields[manFields[kx]] || _agrigator.tofS!==typeof fields[manFields[kx]] || _agrigator.emptyStr===fields[manFields[kx]]){
                    return msg.replace(new RegExp(mark),labels[manFields[kx]]);
                }
            }
            return '';
        };

        _this.checkLogin = function(str){
            if(_agrigator.tofS!==typeof str || _agrigator.emptyStr===str || _this.loginMinLen>str.length){
                return _this.langData.Errors['102'].replace(/#{field}/,_this.langData.interface.login)+'('+$this.loginMinLen+')!';
//                    return 'Поле "Логин" незаполнено или имеет неверный формат или количество символов меньше минимального('+$this.loginMinLen+')!';
            }
            return '';
        };

        _this.checkPswd = function(p1,p2,isNU){
            // сперва проверим что это строки и они не пустые
            var isEmpty = (_agrigator.tofS!==typeof p1 || _agrigator.emptyStr===p1 || _agrigator.tofS!==typeof p2 || _agrigator.emptyStr===p2);
            if(isNU && isEmpty){
                return _this.langData.Errors['103'].replace(/#{field}/,_this.langData.interface.password);
//                    return 'Поле "Пароль" или его подтверждение незаполнено!';
            }
            if(!isNU && !isEmpty){
                // теперь проверим что они одинаковые
                if(p1!==p2){
                    return _this.langData.Errors['105'];
//                        return 'Пароль и Подтверждение пароля несовпадают!';
                }
            }
            if(isNU){
                // теперь проверим что они одинаковые
                if(p1!==p2){
                    return _this.langData.Errors['105'];
//                        return 'Пароль и Подтверждение пароля несовпадают!';
                }
                // у а теперь надо проверить на минимальную длину
                if(_this.pswdMinLen>p1.length){
                    return _this.langData.Errors['106']+' ('+_this.pswdMinLen+')!';
//                        return 'Длина пароля меньше минимальной('+$this.pswdMinLen+')!';
                }
            }
            return '';
        };

        _this.checkEmail = function(str){
            // поскольку формат email завистит от почтового сервера, применяем лишь общий шаблон(regExp): .+@.+\..+
            if(_agrigator.tofS!==typeof str || _agrigator.emptyStr===str){
                return _this.langData.Errors['104'].replace(/#{field}/,_this.langData.interface.email);
//                    return 'Поле "Email" незаполнено!';
            }else{
                var srv,at,msg = 'Не корректный формат email';
                msg = _this.langData.Errors['107']+' '+_this.langData.interface.email;
                // сперва разобьем на две части по @ так как это разделение имени пользователя от сервера
                at = str.split('@');
                if(!_agrigator.isArray(at) || at.length<2 || at.length>2){
                    return msg;
                }
                // проверим что обечасти не пустые
                if(_agrigator.tofU===typeof at[0] || _agrigator.tofS!==typeof at[0] || _agrigator.emptyStr===at[0]){
                    return msg;
                }
                if(_agrigator.tofU===typeof at[1] || _agrigator.tofS!==typeof at[1] || _agrigator.emptyStr===at[1]){
                    return msg;
                }
                // теперь надо проверить сервер в общих чертах
                // строка должна состоять как минимум из 2 доменов 1 и второго уровня - domen.rootDomen
                srv = at[1].split('.');
                if(!_agrigator.isArray(srv)){
                    return msg;
                }
                var cnt = srv.length;
                if(_agrigator.tofU===srv[cnt-2] || _agrigator.tofS!==typeof srv[cnt-2] || _agrigator.emptyStr===srv[cnt-2]){
                    return msg;
                }
                if(_agrigator.tofU===srv[cnt-1] || _agrigator.tofS!==typeof srv[cnt-1] || _agrigator.emptyStr===srv[cnt-1]){
                    return msg;
                }
            }
            return '';
        };

        _this.checkData = function(data){
            var msg = '';
            // сперва проверим все обязательные поля
            if(_agrigator.emptyStr===msg){
                msg = _this.checkMandFields(data,_this.isNewUser(data));
            }
            // теперь проверим логин
            if(_agrigator.emptyStr===msg){
                msg = _this.checkLogin(data.Login);
            }
            // теперь проверим пароль
            if(_agrigator.emptyStr===msg){
                msg = _this.checkPswd(data.Password,data.PasswordCheck,_this.isNewUser(data));
            }
            // теперь проверим email
            if(_agrigator.emptyStr===msg){
                msg = _this.checkEmail(data.Email);
            }
            return msg;
        };

        _this.isNewUser = function(data){
            if(_agrigator.emptyStr===data.ID) return true;
            return 1>parseInt((data.ID+0));
        };

        _this.saveUserData = function(btn){
            // предполагаем что мы нажались в активном табе :)
            var frm,frmData,_2send='',error='',tab = _this.tabsW.getCurrentTab();
            _this.toggleLockFrmButtons();
            // прикольно было бы повесить лоадер на место поверх кнопки сохранения
            frm = tab.tabHtml.find('.user-edit-form:first');
            frmData = _this.userFormToObject(frm);
            error = _this.checkData(frmData);
            if(_agrigator.emptyStr!==error){
                alert(error);
                _this.toggleLockFrmButtons(1);
                return;
            }
            // если пароль пустой - значит мы его не меняем и даже не
            // отправляем на сервер
            if(typeof void null!=typeof frmData.Password){
                if(''==frmData.Password){
                    delete frmData.Password;
                }
                if(typeof void null!=typeof frmData.PasswordCheck){ delete frmData.PasswordCheck; }
            }
            $.post('/portal/users/save',frmData,function(ans){
                _this.toggleLockFrmButtons(1);
                if(!_agrigator.isUndefined(ans)){
                    if(ans.state==200){
                        var kx,trData = {};
                        trData = _this.gridW.getEmptyRowObject();
                        trData.FIO = ans.data.name;
                        trData.Login = ans.data.login;
                        trData.Email = ans.data.email;
                        trData.FIO = _this.shortFIO(trData.FIO);
                        _this.gridW.addRow(trData);
                        _this.tabsW.closeTab(tab.tabN); // закрываем таб
                    }else{
                        alert(ans.msg);
                    }
                }
            },'json');
        };

        _this.shortFIO = function(fio){
            var str,m = fio;
            m = m.split(' ');
            str = '';
            if(_agrigator.tofS===typeof m[0] && _agrigator.emptyStr!==m[0]){ str += m[0]; }
            if(_agrigator.emptyStr!==str){ str += ' '; }
            if(_agrigator.tofS===typeof m[1] && _agrigator.emptyStr!==m[1]){ str += m[1].substring(0,1)+'.'; }
            if(_agrigator.tofS===typeof m[2] && _agrigator.emptyStr!==m[2]){ str += m[2].substring(0,1)+'.'; }
            return (_agrigator.tofS!==typeof str || _agrigator.emptyStr===str)? fio:str;
        };

        _this.exportUsers = function(point,sync,callback){
            if(!_agrigator.isArray(point) && _agrigator.tofF!==typeof callback){
                throw new Error($this.langData.Errors['108']);
            }
            var url,func,format='json';
            if(_agrigator.tofU===typeof sync){
                sync = false;
            }
            url = '/portal/users/getList';
            func = function(ans){
                if(sync){
                    ans = _agrigator.oJSON.parse(ans.responseText);
                }
                if(!_agrigator.isUndefined(ans)){
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
                        if(_agrigator.tofF===typeof callback){
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

        _this.userFormToObject = function(frm){
            var o;
            o={};
            o = _agrigator.fToObj(frm.get(0));
            return o;
        };

        _this.closeEditForm = function(btn){
            // предполагаем что мы нажались в активном табе :)
            var tab = _this.tabsW.getCurrentTab();
            _this.tabsW.closeTab(tab.tabN);
        };

        _this.fillUserEditForm = function(form,data){};

        _this.isNewUserByKey = function(key){
            var kM = key.split('-');
            return !(0<parseInt(kM[1]));
        };

            $this.getUkeyByTab = function(tab){
                var kx,tabID;
                if(_agrigator.tofS===typeof tab && _agrigator.emptyStr!==tab){
                    // предполагаем что это ID таба
                    tabID=tab;
                }else{
                    if($(tab).hasClass($this.tabsW.itemCls)){
                        // предполагаем что нам дали html элемент li таба
                        tabID = $this.tabsW.getTabID(tab);
                    }
                }
                if(_agrigator.tofS!==typeof tabID || _agrigator.emptyStr===tabID){
                    throw new Error($this.langData.Errors['109']);
                }
                for(kx in $this.interface.Opened){
                    if(null===$this.interface.Opened[kx].tab) continue;
                    if(tabID===$this.interface.Opened[kx].tab){
                        break;;
                    }
                }
                return kx;
            };

            $this.getUserRowByKey = function(key){};

            $this.applyLangPack = function(){};
    /* Менеджер диалогов [ */
    _this.windowManager = function(p){
        var _1this = this,
            _list={};

        _1this.active = null;
        _1this.getActive = function(){ return _1this.active; };

        _1this.add = function(dlg){};
        _1this.remove = function(idy){};
        function _c(cp){

        };

        _c(p);
    };
    /* Менеджер диалогов ] */

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
                    lbl1 = _this.moduleData.interface.createNews,
                    lbl2 = '',
                    lbl3 = _this.moduleData.interface.delete;
                $tb.append('<span class="ui-corner-all toolbar-btn" action="groupDelete" disabled="true"><span class="text">'+lbl3+'</span></span>');
                $tb.append('<span class="toolbar-delim"></span>');
                // кнопка "Перейти на уровень выше"
//                $tb.append('<span class="ui-corner-all toolbar-btn" action="uplevel"><span class="ui-icon ui-icon-arrowreturnthick-1-n"></span></span>');
                // кнопка "Создать директорию"
                $tb.append('<span class="ui-corner-all toolbar-btn" action="createnews"><span class="text">'+lbl1+'</span></span>');

                // кнопка "загрузить файл(ы)"
//                $tb.append('<span class="ui-corner-all toolbar-btn" action="addfiles"><span class="text">'+lbl2+'</span></span>');

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

            function _c(){}
            _c();
        };
        return new _cls(k);
    };
    /* jqGrid для отображения содержимого одной директории ] */
    /* uiDialog для работы с формами в диалогах */
    _this.dialog = function(k){
        var _cls = function(p){
            var _1this = this,
                _$dlg=null,
                _$parent;
            _1this.id = '';
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
                        open:function(){ _EvMan.fire('NewsDialogOpen',{content:$(this)}); },
                        beforeClose:function(){ _EvMan.fire('NewsDialogBeforeClose',{content:$(this)}); },
                        close:function(){ _EvMan.fire('NewsDialogClose',{content:$(this)}); }
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
    /* uiDialog для работы с формами в диалогах */

    _this.getDialogWA = function(){
        var wa={w:0,h:0};
        wa = _this.Grid.getWorkArea();
        return wa;
    };


    _this.gridToolbarEvCatcher = function(p){
        switch(p.action){
            case 'groupDelete':
                // групповое удаление элементов на текущем уровне
//                if(!p.$btn.prop('disabled')){ // почему-то в ИЕ 11 не возникает событие клик на чекбоксе
                    _this.deleteSelectedItems();
//                }
                break;
            case 'createnews':
                // открываем окно для загрузки файла(ов)
                _this.dialog.open(_this.moduleData.templates.createNews,function($box){
                    _this.initNewsEditDialog($box);
                });
                break;
        }
    };
    _this.gridRowToolbarEvCatcher = function(p){
//       p=> {action:'', rowID:'' }
        var row;
        row = _this.Grid.getRowData(p.rowID);
        row['rowID'] = p.rowID;
        switch(p.action){
            case 'open':
                break;
            case 'edit':
                // открываем окно для создания новой директории
                _this.editNews(row);
                break;
            case 'remove':
                _this.deleteNews(row);
                break;
        }
    };

    _this.saveNews = function(form){
        var data={};
        data.ID = $(form).find('input[name="ID"]').val();
        data.Name = $(form).find('input[name="Name"]').val();
        data.Lang = $(form).find('select[name="Lang"]').val();
        data.PubDate = $(form).find('input[name="PubDate"]').val();
        data.Text = $(form).find('textarea[name="Text"]').val();
        data.Text = tinymce.get($(form).find('textarea[name="Text"]').attr('id')).getContent();
        $.post(_this.baseURL+'/saveNews/',data,function(asn){
            if(asn.State==200){
                _this.Grid.reload();
                _this.dialog.close();
            }else{
                alert(asn.Msg);
            }
        },'json');
    };

    _this.deleteNews = function(data,fromForm){
        if(typeof void null==data.ID || ''===data.ID){ return; }
        if(typeof void null===typeof fromForm || null===fromForm){ fromForm = false; }else{ fromForm = (fromForm); }
        $.get(_this.baseURL+'/deleteNews/'+data.ID,null,function(dna){
            if(dna.State==200){
                if(fromForm){
                    _this.Grid.reload();
                    _this.dialog.close();
                }else{
                    _this.Grid.delRow(data.rowID);
                }
            }else{
                alert(dna.Msg);
            }
        },'json');
    };

    _this.editNews = function(data){
        $.post(_this.baseURL+'/getNews/',data,function(ned){
            _this.dialog.open(_this.moduleData.templates.createNews,function($box){
                $box.find('input[name="ID"]').val(ned.Data.ID);
                $box.find('.input-text[name="Name"]').val(ned.Data.Name);
                $box.find('.select-ctrl[name="Lang"]').val(ned.Data.Lang);
                $box.find('.input-text[name="PubDate"]').val(ned.Data.PubDate);
                $box.find('textarea[name="Text"]').val(ned.Data.Text);
                _this.initNewsEditDialog($box);
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


    _this.initNewsEditDialog = function($box){
//        $box.find('form:first .form-tbl').css({width:'100%'});
        $box.find('.input-text[name="PubDate"]').datepicker({
            dateFormat:'dd.mm.yy',
            showOn: 'button',
            buttonImage: '/static/img/calendar.png',
            buttonImageOnly: true
        });
        // теперь инициализируем ckEditor
        _this.initTextEditor($box.find('textarea[name="Text"]:first'));
        $box.find('.close-btn:first').click(function(){ _this.dialog.close(); });
        $box.find('.save-btn:first').click(function(){ _this.saveNews(this.form); });
        $box.find('.del-btn:first').click(function(){ _this.deleteNews({ID:this.form.elements['ID'].value},true); });

        $box.find('.form-toolbar button').button();
    };

    _this.initTextEditor = function($elem){
        var d= new Date(), id = 'txtEdit-'+d.getTime(),editor;
        $elem.attr('id',id);
        $elem.css({width:'54.6em',height:'200px'});
        // CKEditor
//        $elem.ckeditor(_this.moduleData.texteditor);
//        if(CKEDITOR.instances[id]){
//            CKEDITOR.remove(CKEDITOR.instances[id]);
//        }
//        editor = CKEDITOR.replace(id,_this.moduleData.texteditor);

        // NicEditor
//        if(!editor) {
//            editor = new nicEditor({iconsPath : '/js/NicEdit/nicEditorIcons.gif',
////                fullPanel : true,
//                buttonList:['bold','italic','underline','left','center','right','justify','ol','ul','subscript','superscript','strikethrough','removeformat','indent','outdent','hr','forecolor','fontSize','fontFamily','fontFormat'],
//                onSave : function(content, id, instance) {
//                    $elem.val(content);
//                }
//            }).panelInstance(id,{hasPanel : true});
//        } else {
//            editor.removeInstance(id);
//            editor = null;
//        }

        //tinymce
        tinymce.init({
            selector:'#'+id,
            language:_this.langData.curLangCode
        });
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

        _this.dialog.init();
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
        _EvMan.subscribe('ClickGridRowToolbarBtn',_this.gridRowToolbarEvCatcher);
        _EvMan.subscribe('ToggleDirGridRowSelection',function(p){
            // {rowID:string,selected:boolean}
            // надо проверить есть ли выделенные строки
            var selRows = _this.Grid.getSelectedRows(),cnt=selRows.length,
                $tB = _this.Grid.getGridToolBarEl(),
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
        // надо загрузить данные для модуля
        $.post(_this.baseURL+'/getModuleData/',null,function(amd){ _this.moduleData = amd; _isInit = true;
            _this.dialog = _this.dialog({id:'pu-dialog'});
            _this.Grid = _this.Grid({id:'user-register'});
        },'json');
    }

    _c();
};
// теперь относледуемся
_jsUtils.inherit(_PortalUsersManagerCls,PageBlock);

// подключаем наш модуль по событию что приложение готово подключать модуль, так как аяксом запрашиваются данные о локализации
if(typeof void null!==typeof Desktop && null!==Desktop){
    Desktop.EvMan.subscribe('CanRegBlocks',function(p){
        if(typeof void null!==typeof Desktop.app && null!==Desktop.app){
            p['langData']['PortalUsers'].curLangCode = p.curLangCode;
            Desktop.app.registerBlock('PortalUsers1',_PortalUsersManagerCls,{langData:p['langData']['PortalUsers']});
        }
    });
}