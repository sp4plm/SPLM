$(function(){
    var _$box, dialog, _base_url,
        _$lastOpenDlg = null;

    _$box = $('#page-content-marker').parent();
    _base_url = _$box.find('#js-base-url').val();

    function clickAddNaviLinks(){
        hideNaviBlocks();
        hideEditForm();
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
            };
            _1this.option = function(name, value){
//                if(typeof void null != _$dlg.dialog('instance')){
                    _$dlg.dialog('option', name, value);
//                }
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

    // нужен диалог
    // нужен шаблон диалога
    // метод получивший все доступные ссылки с рабитием по модулям

    function getLinkSelectorTmpl() {
        var html;
        html = _$box.find('#serve-conte #link-selector-dialog').html();
        $(html).find('#link-selector-variants table tbody').css({'overflow': 'auto'});
        return html;
    }

    function clickCloseLinkSelector(){ dialog.close(); }

    function clickChooseLinkSelector(){
        var $btn, $frm_selector, $frm_point, selected_data, $data_tr,
            roles=[], xi, cnt, role;
        selected_data = {'label':'', 'href': '', 'roles': ''};
        // this - это кнопка, второй родитель в ветке предков - форма
        if(null != _$lastOpenDlg){
        }
        $btn = $(this);
        $frm_selector = $btn.parent().parent();
        // собираем данные
        $data_tr = $frm_selector.find('.url-point-selector:checked').parent().parent();
        selected_data['label'] = $data_tr.find('.point-label').html();
        selected_data['href'] = $data_tr.find('.point-url').html();
        if(0 < $data_tr.find('.point-roles').length) {
            selected_data['roles'] = $data_tr.find('.point-roles').html();
        }
        // устанавливаем выбранные данные
        $frm_point = _$box.find('form[name="NaviItemEditForm"]:first');
        $frm_point.find('[name="NaviItemLink"]').val(selected_data['href']);
        $frm_point.find('[name="NaviItemName"]').val(selected_data['label']);
        if(''!=selected_data['roles']){
            $frm_point.find('[name="NaviItemRoles"]').val(selected_data['roles']);
            // теперь отметим те роли которые нам нужны
            roles = str2array(selected_data['roles']);
            cnt = roles.length;
            for(xi=0;xi<cnt;xi++) {
                role=roles[xi];
                $frm_point.find('.user-role[value="'+role+'"]').prop('checked', true);
            }
        }
        // close dialog
        $frm_selector.find('[name="CloseForm"]').trigger('click');
    }

    function clickSelectLink() {
        var url;
        // alert('Open link selector');
        url = '/portal/management/navigation/item/links';
        $.post(url, null, function(answ){
            var cnt, idx, rows;
            rows = [];
            if (typeof void null !== typeof answ && null != answ){
                if (typeof void null !== typeof answ.data){
                    rows = answ.data;
                }
            }
            cnt = rows.length;
            dialog.open(getLinkSelectorTmpl(),function($box){
                var $rowsParent, $td, $tr, links;
                _$lastOpenDlg = $box;
                $rowsParent = $box.find('#link-selector-variants table:first tbody:first');
                $box.find('[name="CloseForm"]').on('click', clickCloseLinkSelector);
                if (0<cnt){
                    $box.find('[name="SelectLink"]').on('click', clickChooseLinkSelector);
                    // {'name': '', 'label': '', 'links': []}
                    for(ix=0;ix<cnt;ix++){
                        has_links = (0<rows[ix]['links'].length);
                        if(!has_links){
                            continue;
                        }
                        $tr = $('<tr></tr>');
//                        $td = $('<td>&nbsp;</td>');
//                        $tr.append($td);
                        $td = $('<td></td>');
                        $td.html(rows[ix]['label'])
                        $tr.append($td);
                        $td = $('<td style="padding:0px;"></td>');
                        links = '';
                        links = _cookSelectorLinks(rows[ix]['links']);
                        $td.append(links);
                        $tr.append($td);
                        $rowsParent.append($tr);
                    }
                }
            });
            dialog.option('width', 600);
            dialog.option('height', 500);
        }, 'json');
    }

    function _cookSelectorLink(data){
        var html, roles_str;
        // {'label': '', 'href': '', 'roles': []}
        html = '';
        html += '<table border="0" style="border:none; margin:0px;">';
        html += '<tbody>';
        html += '<tr>';
        html += '<td style="border:none;">';
        html += '<input type="radio" class="url-point-selector" name="NewHref" />';
        html += '</td>';
        html += '<td style="border:none;">';
        html += '<span class="point-url">' + data['href'] + '</span>';
        html += '<hr style="border-bottom:1px solid #000;margin: 2px 0px 2px 0px;" /><span class="point-label">' + data['label'] + '</span>';
        if(0 < data['roles'].length) {
            roles_str = array2str(data['roles'])
            html += '<hr style="border-bottom:1px solid #000;margin: 2px 0px 2px 0px;" /><span class="point-roles">' + roles_str + '</span>';
        }
        html += '</td>';
        html += '</tr>';
        html += '</tbody>';
        html += '</table>';
        return html;
    }

    function array2str(ar, d) {
        var res;
        res = '';
        if (typeof void null == typeof d){
            d = ',';
        }
        if (0 < ar.length) {
            res = ar.join(d);
        }
        return res;
    }

    function str2array(str, d) {
        var res;
        res = [];
        if (typeof void null == typeof d) {
            d = ',';
        }
        if ('' != str) {
            res = str.split(d);
        }
        return res;
    }

    function _cookSelectorLinks(lst){
        var html, ix, cnt;
        html = '';
        cnt = lst.length;
        for(ix=0;ix<cnt;ix++){
            link_html = _cookSelectorLink(lst[ix]);
            html += '<li>';
            if(0 < ix) {
                html += '<hr style="border-bottom:1px solid #000;margin: 2px 0px 2px 0px;">';
            }
            html += link_html;
            html += '</li>';
        }
        html = '<ul style="padding-left:0px;">' + html + '</ul>';
        return html;
    }

    function clickSaveLink() {
        var $frm;
        $frm = $('#naviitem-edit-form').find('[name="NaviItemEditForm"]');
        $frm.attr('method', 'POST');
        $frm.attr('onsubmit', '');
    }

    function clickCloseLinkForm() {
        var url, blk_code;
        url = '/portal/management/navigation';
        blk_code = _$box.find('input[name="NaviCode"]').val();
        url += '/' + blk_code;
        window.location = url;
    }

    function clickAddNewLink(){
        var url, blk_code, item_code;
        url = '/portal/management/navigation';
        item_code = 'new'
        blk_code = _$box.find('input[name="NaviCode"]').val();
        url += '/' + blk_code;
        url += '/' + item_code;
        window.location = url;
    }

    function clickEditLink(linkData){
        var url, blk_code, item_code;
        url = '/portal/management/navigation';
        item_code = 'new'
        blk_code = _$box.find('input[name="NaviCode"]').val();
        url += '/' + blk_code;
        url += '/' + linkData['code'];
        window.location = url;
    }

    function clickSelectRole() {
        var $rolesParent, roles, _t;
        _t = [];
        $rolesParent = $(this).parents('ul:first');
        roles = '';
        $rolesParent.find('.user-role:checked').each(function(){
            _t.push($(this).val());
        });
        if(0 < _t.length) {
            roles = _t.join(',')
        }
        _$box.find('input[name="NaviItemRoles"]').val(roles);
    }

    function clickRemoveLink(linkData, $tr){
        var _data;
        _data = {'item': '', 'block': ''};
        _data['item'] = linkData['code'];
        _data['block'] = _$box.find('input[name="NaviCode"]').val();
        $.post('/portal/management/navigation/item/delete', _data, function(answ){
            if(answ){
                if (typeof void null != typeof answ.state && answ.state == 200) {
                    if(typeof void null != typeof $tr) {
                        $tr.remove();
                    }
                } else {
                    if (typeof 'z' == typeof answ.msg && '' != answ.msg) {
                        alert(answ.msg);
                    } else {
                        alert('Неизвестная ошибка на сервуре!');
                    }
                }
            }
        }, 'json');
    }

    function clickSortLink(linkData, direct, $tr){
        var _data, $otr;
        // сперва надо определиться можем ли мы двигаться дальше
        if (0 < direct) {
            // надо поменять текущую строку местами с последующей
            $otr = $tr.next();
            if (0 == $otr.length){
                alert('Навигационный пункт последний!');
                return;
            }
//            else {
//                $tr.insertAfter($otr);
//            }
        }
        // sort_up - движение в таблице вверх - уменьшение srtid
        if (0 > direct){
            // надо поменять текущую строку местами с предыдущей
            $otr = $tr.prev();
            if ( 0 == $otr.length){
                alert('Навигационный пункт первый');
                return;
            }
//            else{
//                $tr.insertBefore($otr);
//            }
        }
        _data = {'item': '', 'block': '', 'dir': 0};
        _data['item'] = linkData['code'];
        _data['block'] = _$box.find('input[name="NaviCode"]').val();
        _data['dir'] = direct;
        $.post('/portal/management/navigation/item/sort', _data, function(answ){
            if(answ){
                if (typeof void null != typeof answ.state && answ.state == 200) {
                    if(typeof void null != typeof $tr) {
                        // sort_down - движение в таблице вниз - увеличение srtid
                        if (0 < direct) {
                            // надо поменять текущую строку местами с последующей
                            $tr.insertAfter($otr);
                        }
                        // sort_up - движение в таблице вверх - уменьшение srtid
                        if (0 > direct){
                            // надо поменять текущую строку местами с предыдущей
                            $tr.insertBefore($otr);
                        }
                    }
                } else {
                    if (typeof 'z' == typeof answ.msg && '' != answ.msg) {
                        alert(answ.msg);
                    } else {
                        alert('Неизвестная ошибка на сервуре!');
                    }
                }
            }
        }, 'json');
    }

    function clickAddNewNavi(){
        hideNaviBlocks();
        viewEditForm();
        $(this).hide();
        $('#navi-edit-form').find('[name="CloseNaviForm"]').on('click', function(){
            hideEditForm();
            viewNaviBlocks();
            clearEditForm();
            _$box.find('[name="AddNewNavi"]').show();
        });
        $('#navi-edit-form').find('[name="SaveNavi"]').on('click', function(){
            var $frm;
            $frm = $('#navi-edit-form').find('[name="NaviEditForm"]');
            $frm.attr('method', 'POST');
            $frm.attr('onsubmit', '');
        });
    }

    function clickEditNavi(naviBlock){
        var codes;
        hideNaviBlocks();
        viewEditForm();
        codes = get_default_blocks();
        _$box.find('[name="AddNewNavi"]').hide();
        $('#navi-edit-form').find('[name="NaviCode"]').val(naviBlock['code']);
        $('#navi-edit-form').find('[name="NaviBlockName"]').val(naviBlock['label']);
        $('#navi-edit-form').find('[name="NaviBlockCode"]').val(naviBlock['code']);
        $('#navi-edit-form').find('[name="NaviBlockLink"]').val(naviBlock['href']);
        if(0 < codes.length) {
            if(-1 !== codes.indexOf(naviBlock['code'])) {
                $('#navi-edit-form').find('[name="NaviBlockCode"]').prop('readonly', true);
            } else {
                $('#navi-edit-form').find('[name="NaviBlockCode"]').prop('readonly', false);
                $('#navi-edit-form').find('[name="NaviBlockCode"]').removeProp('readonly');
            }
        }
        $('#navi-edit-form').find('[name="CloseNaviForm"]').on('click', function(){
            hideEditForm();
            viewNaviBlocks();
            clearEditForm();
            _$box.find('[name="AddNewNavi"]').show();
        });
        $('#navi-edit-form').find('[name="SaveNavi"]').on('click', function(){
            var $frm;
            $frm = $('#navi-edit-form').find('[name="NaviEditForm"]');
            $frm.attr('method', 'POST');
            $frm.attr('onsubmit', '');
        });
    }

    function clickDeleteNavi(_naviBlock, $tr) {
        var _data;
        _data = {'code': ''};
        _data['code'] = _naviBlock['code'];
        $.post('/portal/management/navigation/block/delete', _data, function(answ){
            if(answ){
                if (typeof void null != typeof answ.state && answ.state == 200) {
                    if(typeof void null != typeof $tr) {
                        $tr.remove();
                    }
                } else {
                    if (typeof 'z' == typeof answ.msg && '' != answ.msg) {
                        alert(answ.msg);
                    } else {
                        alert('Неизвестная ошибка на сервуре!');
                    }
                }
            }
        }, 'json');
    }

    function clickEditNaviLinks(_naviBlock) {
        var url;
        url = '/portal/management/navigation';
        url += '/' + _naviBlock['code'];
        window.location = url;
    }

    function clickRowToolbarBtn() {
        var $btn, $tr, _data, _act;
        // this - button in first cell of edit row
        $btn = $(this);
        _act = $btn.attr('action');
        $tr = $btn.parent().parent();
        _data = {'code': '', 'label': '', 'href': ''};
        _data['code'] = $($tr.find('td')[2]).html();
        _data['label'] = $($tr.find('td')[1]).html();
        _data['href'] = $($tr.find('td')[3]).html();
        switch(_act) {
            case "edit":
                clickEditNavi(_data);
                break;
            case "add_links":
                clickEditNaviLinks(_data);
                break;
            case "delete":
                if(confirm('Вы действительно хотите удалить навигационный блок "'+_data['label']+'"?')){
                    clickDeleteNavi(_data, $tr);
                }
                break;
        }
    }

    function clickItemRowToolbarBtn() {
        var $btn, $tr, _data, _act;
        // this - button in first cell of edit row
        $btn = $(this);
        _act = $btn.attr('action');
        $tr = $btn.parent().parent();
        _data = {'code': '', 'label': '', 'href': ''};
        _data['code'] = $($tr.find('td')[3]).html();
        _data['label'] = $($tr.find('td')[1]).html();
        _data['href'] = $($tr.find('td')[2]).html();
        _data['roles'] = $($tr.find('td')[4]).html();
        switch(_act) {
            case "edit":
                clickEditLink(_data);
                break;
            case "delete":
                if(confirm('Вы действительно хотите удалить пункт навигации "'+_data['label']+'"?')){
                    clickRemoveLink(_data, $tr);
                }
                break;
            case "sort_up":
                clickSortLink(_data, -1, $tr);
                break;
            case "sort_down":
                clickSortLink(_data, 1, $tr);
                break;
        }
    }

    function clearEditForm(){
        $('#navi-edit-form').find('[name="NaviCode"]').val('');
        $('#navi-edit-form').find('[name="NaviBlockName"]').val('');
        $('#navi-edit-form').find('[name="NaviBlockCode"]').val('');
        $('#navi-edit-form').find('[name="NaviBlockLink"]').val('');
        $('#navi-edit-form').attr('onsubmit', 'return false;');
    }

    function viewEditForm(){ $('#navi-edit-form').show(); }

    function hideEditForm(){ $('#navi-edit-form').hide(); }

    function viewNaviBlocks(){ $('#awailable-navigations').show(); }

    function hideNaviBlocks(){ $('#awailable-navigations').hide(); }

    function get_default_blocks() {
        var frm, s, lst = [];
        s = $('#navi-edit-form').find('[name="DefCodes"]').val();
        if(''!=s) {
            lst = s.split(',');
        }
        return lst;
    }

    // инициализация диалога для работы с окнами
    dialog.init();

    _$box.find('button').button();
    // blocks edit form
    _$box.find('[name="AddNewNavi"]').on('click', clickAddNewNavi);
    _$box.find('#awailable-navigations tr .act-btn').on('click', clickRowToolbarBtn);
    // block edit form
    _$box.find('#navi-content-form tr .act-btn').on('click', clickItemRowToolbarBtn);
    _$box.find('#add-new-link').on('click', clickAddNewLink);
    // item edit form
    _$box.find('#naviitem-edit-form [name="CloseForm"]').on('click', clickCloseLinkForm);
    _$box.find('#naviitem-edit-form [name="SaveItem"]').on('click', clickSaveLink);
    _$box.find('#link-selector').on('click', clickSelectLink);
    _$box.find('.user-role').on('click', clickSelectRole);
});