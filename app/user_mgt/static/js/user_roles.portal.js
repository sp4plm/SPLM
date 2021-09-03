(function(win,undefined){
    if(typeof void null!==typeof jQuery){
        (function($){
            UserRolesManager = function(parent){
                var cls = function(p){
                    var _this = this,
                        _$box = null,
                        _boxID = '';
                    cls.superclass.constructor.call(_this,p);

                    _this.langData = null;
                    if(typeof void null!=typeof p && null!==p){
                        _this.langData = (typeof void null!=typeof p.langData && null!==p.langData)? p.langData:null;
                    }
                    _this.blkBox = null;
                    _this.header = '';
                    _this.viewTmpl = '';
                    _this._roles = [];

                    _this.baseUrl = '/users/roles';
                    _this.loader = null;
                    _this.listBox = null;
                    _this.itemsList = null;
                    _this.listBoxCls = 'editItems-list-box';
                    _this.itemsListCls = 'editItems-list';
                    _this.listItemCls = 'edit-item';
                    _this.listItemIDpref = 'rld-';
                    _this.listItemToolbarCls = 'listItem-toolbar';
                    _this.listItemToolbar = '<div></div>';
                    _this.viewBox = null;
                    _this.viewBoxCls = 'item-viewer-box';
                    _this.viewerCls = 'item-viewer';
                    _this.editorCls = 'item-editor';
                    _this.viewBoxLoader = null;
                    _this.tmplViewObj = '<fieldset>\
                        <legend></legend>\
                        <table>\
                            <tbody>\
                                <tr field="Name">\
                                    <td class="form-field-label">'+_this.langData.interface.roleName+':&nbsp;&nbsp;</td><td class="form-field-data"></td>\
                                </tr>\
                                <tr field="Pages" style="display:none;">\
                                    <td class="form-field-label">'+_this.langData.interface.avalablePages+'</td><td class="form-field-data"></td>\
                                <tr field="Users">\
                                    <td class="form-field-label">'+_this.langData.interface.users+':&nbsp;&nbsp;</td><td class="form-field-data"></td>\
                                </tr>\
                            </tbody>\
                        </table>\
                    </fieldset>';
                    _this.tmplEditObjForm = '\
                    <form name="PageEditForm" class="edit-form" method="post" onsubmit="return false;">\
                        <input type="hidden" name="ID" value="" />\
                        <input type="hidden" name="TYPE" value="role" />\
                        <input type="hidden" name="Code" value="" />\
                        <input type="hidden" name="Pages[]" value="" />\
                        <input type="hidden" name="Users[]" value="" />\
                        <fieldset>\
                            <legend></legend>\
                            <table class="form-tbl">\
                                <tbody>\
                                    <tr field="Name">\
                                        <td class="form-field-label">'+_this.langData.interface.roleName+':&nbsp;&nbsp;</td>\
                                        <td class="form-field-data">\
                                            <div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp">\
                                                <input type="text" class="input-text" name="Name" value="" />\
                                            </div>\
                                        </td>\
                                    </tr>\
                                    <tr field="Pages" style="display:none;">\
                                        <td class="form-field-label">'+_this.langData.interface.avalablePages+'</td>\
                                        <td class="form-field-data"><div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp" style="width:90%;height:120px;overflow:auto;"></div></td>\
                                    <tr field="Users" style="display:none;">\
                                        <td class="form-field-label">'+_this.langData.interface.users+'</td>\
                                        <td class="form-field-data"><div class="ui-widget ui-widget-content ui-corner-all field-ui-wrp" style="width:90%;height:120px;overflow:auto;"></div></td>\
                                    </tr>\
                                </tbody>\
                            </table>\
                        </fieldset>\
                        <div class="toolbar form-toolbar">\
                            <button name="CloseRoleFormBtn" class="toolbar-btn close-btn role-close-btn">'+_this.langData.interface.close+'</button>\
                            <button name="SaveRoleDataBtn" class="toolbar-btn save-btn role-save-btn">'+_this.langData.interface.save+'</button>\
                            <button name="DeleteRoleBtn" class="toolbar-btn del-btn role-del-btn">'+_this.langData.interface.delete+'</button>\
                        </div>\
                    </form>';
                    _this.resize = function(){
                        if(null!==_$box){
                            // теперь надо установить такой размер для страницы чтобы на него могли положиться вычисления для самой страницы
                            var wD = _$box.outerWidth(true)-_$box.width();
                            var hD = _$box.outerHeight(true)-_$box.height();
                            _$box.width(_this.blkBox.width()-wD);
                            _$box.height(_this.blkBox.height()-hD);
                        }
                    };
                    _this._pages = [];
                    _this._users = [];

                    _this.exportRoles = function(point,sync,callback){
                        if(!win._jsTypes.isArray(point) && win._jsTypes.tofF!==typeof callback){
                            throw new Error(_this.langData.Errors['100']);
                        }
                        var url,func,format='json';
                        if(win._jsTypes.tofU===typeof sync){
                            sync = false;
                        }
                        url = _this.baseUrl + '/getList';
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
                        $.post(_this.baseUrl + '/getList',{},function(ans){
                            if(!win._jsTypes.isUndefined(ans)){
                                if(ans.state==200){
                                    var kx=0,cnt=0;
                                    cnt = ans.data.length;
                                    if(cnt>0){
                                        for(kx=0;kx<cnt;kx++){
                                            _this._roles.push({ID:ans.data[kx].id,Name:ans.data[kx].name});
                                        }
                                    }
                                    _this.buildRolesList();
                                }else{
                                    alert(ans.msg);
                                }
                            }
                        },'json');
        //                _this._roles.push({ID:3,Name:'Role 2'});
                    };
                    _this.clearRolesList = function(){ _this.itemsList.find('li.'+_this.listItemCls).remove(); };
                    _this.getRoleItemFromList = function(id){ return _this.itemsList.find('#'+_this.listItemIDpref+id); };
                    _this.buildRolesList = function(){
                        var kx,cnt=0;
                        _this.clearRolesList();
                        cnt = _this._roles.length;
                        if(0<cnt){
                            for(kx=0;kx<cnt;kx++){
                                _this.addRole(_this._roles[kx]);
                            }
                        }
                    };
                     _this.toggleViewBoxMod = function(m){
                        _this.viewBox.removeClass('action-edit').removeClass('action-view');
                        switch(m){
                            case 'view':
                                _this.viewBox.removeClass('action-edit').addClass('action-view');
                                break;
                            case 'edit':
                                _this.viewBox.removeClass('action-view').addClass('action-edit');
                                break;
                        }
                    };
                    _this.hideViewBox = function(){
                        _this.toggleFormButtons();
                        _this.viewBox.removeClass('action-edit').removeClass('action-view');
                        _this.viewBox.find('.'+_this.editorCls+' fieldset legend').html('');
                        _this.viewBox.find('.'+_this.viewerCls+' fieldset legend').html('');
                        _this.toggleFormButtons(1);
                    }
                    _this.toggleFormButtons = function(act){
                        act = (win._jsTypes.tofU===typeof act || null===act)? 'disable':'enable';
//                        if(!_this.viewBox.find('.'+_this.editorCls+' .form-toolbar .toolbar-btn').hasClass('ui-button')){
//                            _this.viewBox.find('.'+_this.editorCls+' .form-toolbar .toolbar-btn').button();
//                        }
                        _this.viewBox.find('.'+_this.editorCls+' .form-toolbar .toolbar-btn').button(act);
                    };
                    _this.addRole = function(data){
                        var li, itemTmpl = '<li><a class="view-role" href="javascript:void(0)">#{label}</a></li>';
                        li = $(itemTmpl.replace(/#{label}/g, data.Name));
                        li.addClass(_this.listItemCls);
                        li.attr('id', _this.listItemIDpref+data.ID);
                        _this.addListItemToolbar(li);
                        _this.itemsList.append(li);
                    };
                    _this.addListItemToolbar = function(li){
                        var toolbar = $(_this.listItemToolbar);
                        toolbar.addClass(_this.listItemToolbarCls);
                        toolbar.append('<span class="act-btn ui-state-default ui-corner-all"><span class="edit-role ui-icon ui-icon-pencil"></span></span>');
                        toolbar.append('<span class="act-btn ui-state-default ui-corner-all"><span class="del-role ui-icon ui-icon-trash"></span></span>');
                        $(li).prepend(toolbar);
                    };
                    _this.viewRole = function(lnk){
                        var pID,li;
                        _this.viewBoxLoader.WFMLoader().show();
                        li = $(lnk).parents('li:first');
                        pID = li.attr('id').replace(new RegExp(_this.listItemIDpref),'');
                        $.post(_this.baseUrl + '/getInfo',{ID:pID},function(ans){
                            if(!win._jsTypes.isUndefined(ans)){
                                if(ans.state==200){
                                    _this.setSelectedPage(li);
                                    _this.viewBox.show();
                                    _this.toggleViewBoxMod('view');
                                    _this.viewBox.find('.'+_this.viewerCls+' fieldset legend').html('&nbsp;'+_this.langData.interface.role+'::'+ans.data.name+'&nbsp;');
                                    _this.viewBox.find('.'+_this.viewerCls+' tr[field="Name"] .form-field-data').html(ans.data.name);
                                    if(!win._jsTypes.isUndefined(ans.data.myLinks)){
                                        var df,kk,kx,cnt=0,str = '',fld='';
                                        for(kk in ans.data.myLinks){
                                            cnt = 0;
                                            cnt = ans.data.myLinks[kk].length;
                                            str = fld = '';
                                            fld = kk.substr(0,1).toUpperCase()+kk.substr(1,kk.length-1);
                                            df = _this.viewBox.find('.'+_this.viewerCls+' tr[field="'+fld+'"] .form-field-data');
                                            df.html('');
                                            for(kx=0;kx<cnt;kx++){
                                                str += ans.data.myLinks[kk][kx].name;
                                                if(kx<(cnt-1)){
                                                    str += '<br />';
                                                }
                                            }
                                            df.html(str);
                                        }
                                    }
                                    _this.viewBoxLoader.WFMLoader().hide();
                                }else{
                                    alert(ans.msg);
                                }
                            }
                        },'json');
                    };
                    _this.editRole = function(btn){
                        _this._pages = [];
                        //Desktop.PagesManager.exportPages(_this._pages,true);
                        _this._users = [];
                        //Desktop.UsersManager.exportUsers(_this._users,true);
                        var rID,li,plTI,ulTI,label='';
                        //_this.viewBoxLoader.WFMLoader().show();
                        _this.viewBox.show();
                        if(win._jsTypes.tofU!==typeof btn){
                            li = $(btn).parents('li:first');
                            rID = li.attr('id').replace(new RegExp(_this.listItemIDpref),'');
                            _this.setSelectedPage(li);
                            label = li.find('a').html();
                        }else{
                            _this.setSelectedPage();
                            rID=-1;label=_this.langData.interface.newRole;
                        }
        //                plTI = setInterval(function(){
//                            if(win._jsTypes.isArray(_this._pages)){
//                                var ul,kx=0,cnt=0;
//                                cnt = _this._pages.length;
//                                if(cnt>0){
//                                    if(0===_this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="Pages"] .link-items-list').length){
//                                        ul = $('<ul class="link-items-list items-edit-list" style="margin:10px;"></ul>');
//                                        _this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="Pages"] .form-field-data .field-ui-wrp').append(ul);
//                                    }else{
//                                        ul = _this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="Pages"] .form-field-data .field-ui-wrp .link-items-list');
//                                        ul.html('');
//                                    }
//                                    for(kx=0;kx<cnt;kx++){
//                                        ul.append('<li class="link-item"><input class="input-checkbox" type="checkbox" name="Pages[]" value="'+_this._pages[kx]._tbl+'-'+_this._pages[kx].ID+'"/><span class="link-item-label">'+_this._pages[kx].Name+'</span></li>');
//                                    }
//        //                            clearInterval(plTI);
//                                }
//                            }
        //                },'1');
        //                ulTI = setInterval(function(){
//                            if(win._jsTypes.isArray(_this._users)){
//                                var ul,kx=0,cnt=0;
//                                cnt = _this._users.length;
//                                if(cnt>0){
//                                    if(0===_this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="Users"] .link-items-list').length){
//                                        ul = $('<ul class="link-items-list items-edit-list" style="margin:10px;"></ul>');
//                                        _this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="Users"] .form-field-data .field-ui-wrp').append(ul);
//                                    }else{
//                                        ul = _this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="Users"] .form-field-data .field-ui-wrp .link-items-list');
//                                        ul.html('');
//                                    }
//                                    for(kx=0;kx<cnt;kx++){
//                                        ul.append('<li class="link-item"><input class="input-checkbox" type="checkbox" name="Users[]" value="'+_this._users[kx]._tbl+'-'+_this._users[kx].ID+'"/><span class="link-item-label">'+_this._users[kx].Name+'</span></li>');
//                                    }
//        //                            clearInterval(ulTI);
//                                }
//                            }
        //                },'1');
                        _this.viewBox.find('.'+_this.editorCls+' fieldset legend').html('&nbsp;'+_this.langData.interface.role+'::'+label+'&nbsp;');
                        _this.viewBox.find('.'+_this.editorCls+' .edit-form input[name="ID"]').val(rID);
                        _this.viewBox.find('.'+_this.editorCls+' .edit-form input[name="Name"]').val('');
                        // сперва нам надо нарисовать если не нарисованы редактилки пользователей и страниц
                        if(0<rID){
                            $.post(_this.baseUrl + '/getInfo',{ID:rID},function(role){
                                if(!win._jsTypes.isUndefined(role)){
                                    if(role.state===200){
                                        _this.viewBox.find('.'+_this.editorCls+' .edit-form input[name="ID"]').val(rID);
                                        _this.viewBox.find('.'+_this.editorCls+' .edit-form input[name="Name"]').val(role.data.name);
                                        if(!win._jsTypes.isUndefined(role.data.myLinks)){
                                            var kk,kx,cnt=0,fld='';
                                            for(kk in role.data.myLinks){
                                                if(win._jsTypes.tofU===typeof kk){ continue; }
                                                cnt = 0;
                                                cnt = role.data.myLinks[kk].length;
                                                fld = '';
                                                fld = kk.substr(0,1).toUpperCase()+kk.substr(1,kk.length-1);
                                                for(kx=0;kx<cnt;kx++){
                                                    _this.viewBox.find('.'+_this.editorCls+' .edit-form tr[field="'+fld+'"] .form-field-data .link-item .input-checkbox[value="'+kk+'-'+role.data.myLinks[kk][kx].id+'"]').prop('checked',true);
                                                }
                                            }
                                        }
                                        _this.toggleViewBoxMod('edit');
                                        _this.viewBoxLoader.WFMLoader().hide();
                                    }else{
                                        alert(role.msg);
                                    }
                                }
                            },'json');
                        }else{
                            _this.toggleViewBoxMod('edit');
                            //_this.viewBoxLoader.WFMLoader().hide();
                        }
                        _this.toggleFormButtons(1);
                    };
                    _this.fillEditData = function(data){};
                    _this.fillViewData = function(data){
                        var box,users,pages;
                        box = _this.viewBox.find('.'+_this.viewerCls);
                        box.find('tr[field="Name"] .form-field-data').html(data.Name);
                        if(win._jsTypes.tofU!==typeof data.Pages && win._jsTypes.isArray(data.Pages)){
                            var kx,cnt=0;

                        }
                        box.find('tr[field="Pages"] .form-field-data').html(pages);
                        if(win._jsTypes.tofU!==typeof data.Users && win._jsTypes.isArray(data.Users)){
                            var kx,cnt=0;

                        }
                        box.find('tr[field="Users"] .form-field-data').html(users);
                    };
                    _this.delRole = function(btn){
                        var fromForm,label='',ID=0;
                        fromForm = $(btn).hasClass('role-del-btn');
                        if(fromForm){ _this.toggleFormButtons(); }
                        label = (fromForm)? $(btn).get(0).form.elements['Name'].value:$(btn).parents('li:first').find('a').html();
                        ID = (fromForm)? $(btn).get(0).form.elements['ID'].value:$(btn).parents('li:first').attr('id').replace(new RegExp(_this.listItemIDpref),'');
                        if(confirm(_this.langData.Msgs.del+' "'+label+'"?')){
                            if(0<ID){
                                //_this.viewBoxLoader.WFMLoader().show();
                                $.post(_this.baseUrl + '/delete',{ID:ID},function(ans){
                                    if(!win._jsTypes.isUndefined(ans)){
                                        if(ans.state==200){
                                            if(fromForm){
                                                _this.hideViewBox();
                                            }
                                            _this.itemsList.find('#'+_this.listItemIDpref+ID).remove();
                                        }else{
                                            alert(ans.msg);
                                        }
                                    }
                                    //_this.viewBoxLoader.WFMLoader().hide();
                                },'json');
                            }
                        }
                        if(fromForm){ _this.toggleFormButtons(1); }
                    };
                    _this.saveRoleData = function(btn){
                        var li,data,label='',ID=0,code='';
                        _this.toggleFormButtons();
                        data = _this.getEditFormData($(btn).get(0).form);
                        label = $(btn).get(0).form.elements['Name'].value;
                        ID = $(btn).get(0).form.elements['ID'].value;
        //                code = $(btn).get(0).form.elements['Code'].value;
        //                alert(win._jsUtils.oJSON.make(data));
                        $.post(_this.baseUrl + '/save',data,function(ans){
                                if(!win._jsTypes.isUndefined(ans)){
                                    if(ans.state==200){
                                        if(0<parseInt(ID)){
                                            li = _this.getRoleItemFromList(ID);
                                            li.find('a:first').html(label);
                                        }else{
                                            // новый добавляем :)
                                            data.ID = win._jsUtils.rand();
                                            _this.addRole({'ID':ans.data.id,'Name':ans.data.name});
                                        }
                                        _this.hideViewBox();
                                    }else{
                                        alert(ans.msg);
                                    }
                                }
                                _this.toggleFormButtons(1);
                            },'json');
                    };
                    _this.getEditFormData = function(frm){
                        var o={};
                        o = win._jsUtils.fToObj($(frm).get(0));
                        return o;
                    };
                    _this.setSelectedPage = function(li){
                        _this.itemsList.find('li.'+_this.listItemCls).removeClass('current-edit-item');
                        if(win._jsTypes.tofU!==typeof li){ $(li).addClass('current-edit-item'); }
                    };

                    _this.run = function(iO){
                        _this.header = iO.pageLabel;
                        _this.blkBox = iO.place;
                        _this.hideBrothers(_this.blkBox);
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
                            var toolbar = $('<div></div>');
                            toolbar.addClass('toolbar');
                            toolbar.addClass('panel-toolbar');
                            toolbar.append('<button name="addNewRoleBtn" class="toolbar-btn" id="addNewRoleBtn">'+_this.langData.interface.addRole+'</button>');
                            _$box.append(toolbar);
                            toolbar.find('.toolbar-btn').button();
                            toolbar.find('#addNewRoleBtn').click(function(){ _this.editRole(); });
                            _this.resize();
                        }
                        _$box.show();
                        //if(null===_this.loader){
                        //    _this.loader = $(_$box).WFMLoader({img:'/img/loader.gif',runOnCreate: false});
                        //}
                        //_this.loader.WFMLoader().show();
                        if(null===_this.itemsList){
                            var listBox = $('<div></div>');
                            listBox.addClass('cln');
                            listBox.addClass(_this.listBoxCls);
                            _this.itemsList = $('<ul></ul>');
                            _this.itemsList.addClass(_this.itemsListCls);
                            listBox.append(_this.itemsList);
                            _$box.append(listBox);
                            listBox.width(_$box.width()*0.3-2);
                            listBox.height(_$box.height()-_$box.find('.header-footer').outerHeight(true)-_$box.find('.panel-toolbar').outerHeight(true)-_$box.find('.content-header').outerHeight()-6);
                            listBox.css({overflow:'auto'});
                            // теперь надо навесить события для редактирования и просмотра страниц
                            _this.itemsList.on('click','.edit-role',function(){ _this.editRole(this); });
                            _this.itemsList.on('click','.view-role',function(){ _this.viewRole(this); });
                            _this.itemsList.on('click','.del-role',function(){ _this.delRole(this); });
                        }
                        _this.getRoles();
                        if(null===_this.viewBox){
                            var viewer,editor,frm;
                            _this.viewBox = $('<div></div>');
                            _this.viewBox.addClass('cln');
                            _this.viewBox.addClass(_this.viewBoxCls);
                            viewer = $('<div></div>'); editor = $('<div></div>');
                            viewer.addClass(_this.viewerCls);
                            editor.addClass(_this.editorCls);
                            _this.viewBox.append(viewer);
                            _this.viewBox.append(editor);
                            _$box.append(_this.viewBox)
                            viewer.html(_this.tmplViewObj);
                            editor.addClass('form-box');
                            editor.html(_this.tmplEditObjForm);
                            _this.viewBox.width(_$box.width()*0.68-2);
                            _this.viewBox.height(_$box.height()-_$box.find('.header-footer').outerHeight(true)-_$box.find('.panel-toolbar').outerHeight(true)-_$box.find('.content-header').outerHeight()-6);
                            _this.viewBox.css({float:'right'});
                            _this.viewBoxLoader = _this.viewBox.WFMLoader({img:'/static/img/loader.gif',runOnCreate: false});
                            _this.viewBox.hide();
                            frm = editor.find('.edit-form');
                            frm.find('.form-toolbar .toolbar-btn').button();
                            frm.on('click','.role-close-btn',function(){ _this.hideViewBox(); });
                            frm.on('click','.role-save-btn',function(){ _this.saveRoleData(this); });
                            frm.on('click','.role-del-btn',function(){ _this.delRole(this); });
                        }
                        //_this.loader.WFMLoader().hide();
                    };
                    // конструктор класса !!!!
                    function _constructor(p){
                        //Desktop.EvMan.subscribe('pageResize', function(p){ _this.resize(); });
                    }// конструктор класса
                    _constructor(p);
                };
                _jsUtils.inherit(cls,parent);
                //return new cls({'langData':Desktop.app.langData['UserRoles']});
                return cls;
            }(PageBlock || _jsUtils.emptyFunc);
            $('body').find('div.maincontent:first').attr('id', 'NaviPageBox');
            // теперь надо дождаться когда загрузятся данные по интерфейсу
            Desktop.EvMan.subscribe('CanRegBlocks', function(evName, args){
                // теперь можно создавать экземпляр класса
                UserRolesManager = new UserRolesManager({'langData':args.langData['UserRoles']});
                UserRolesManager.run({'place':$('body').find('div.maincontent:first'),
                    'label': 'Roles',
                    'lang': 'ru',
                    'code': 'UserRoles',
                    'targetBlkID': ''
                });
            });
        })(jQuery);
    }else{
        alert('jQuery portal administrative user roles tool say: jQuery lib is not loaded');
    }
})(window);