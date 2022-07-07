if(typeof void null!=typeof jQuery){
    (function($){
        var _jqDialog = function(){
            var _cls = function(p){
                var _this = this,
                    _$dlg=null,
                    _$parent;

                _this.id = '';
                _this.id = p.id;
                _this._events = {
                    'open': function(){},
                    'beforeClose': function(){},
                    'close': function(){}
                };
                _this._$dlg = null;

                _this.build = function(){
                    if(0==_$parent.find('#'+_this.id).length){
                        _$dlg = $('<div></div>');
                        _$dlg.attr('id',_this.id);
                        //                    _$dlg.hide();
                        _$parent.append(_$dlg);
                    }
                    _this._$dlg = _$dlg.dialog({
                        title:'',
                        autoOpen: false,
                        modal: false,
                        open:function(){
                            //_EvMan.fire('FMDialogOpen',{content:$(this),_skey:_selfCode});
                            if(typeof function(){} === typeof _this.open){
                                try{ _this.open(); } catch(err) { alert(err); }
                            }
                        },
                        beforeClose:function(){
                            //_EvMan.fire('FMDialogBeforeClose',{content:$(this),_skey:_selfCode});
                            if(typeof function(){} === typeof _this.beforeClose){
                                try{ _this.beforeClose(); } catch(err) { alert(err); }
                            }
                        },
                        close:function(){
                            //_EvMan.fire('FMDialogClose',{content:$(this),_skey:_selfCode});
                            if(typeof function(){} === typeof _this.close){
                                try{ _this.close(); } catch(err) { alert(err); }
                            }
                        }
                    });
                };
                _this.destroy = function(){
                    if(typeof void null!=typeof _$dlg && null!==_$dlg){
                        _this._$dlg.dialog('destroy');
                    }
                };
                _this.clearContent=function(){
                    if(typeof void null!=typeof _$dlg && null!==_$dlg){
                        _$dlg.html('');
                    }
                };
                _this.open = function(tmpl, cB){
                    if(_this._$dlg.dialog('isOpen')){
                        //_this.close();
                    }
                    //_this.clearContent();
                    _$dlg.html(tmpl);
                    if(typeof function(){} === typeof cB){
                        cB(_this._$dlg);
                    }
                    _this._$dlg.dialog('open');
                };
                _this.close = function(){
                    if(_this._$dlg.dialog('isOpen')){
                        _this._$dlg.dialog('close');
                    }
                };
                _this.init = function(){
                    if(typeof void null == typeof p.parent){
                        p['parent'] = $('body');
                    }
                    _$parent = $(p.parent);
                    _this.build();
                };

                function _c(){
                    _this.id = p.id;
                    if(typeof function(){} === typeof p.open){
                        _this._events['open'] = p.open;
                    }
                    if(typeof function(){} === typeof p.beforeClose){
                        _this._events['open'] = p.open;
                    }
                    if(typeof function(){} === typeof p.close){
                        _this._events['open'] = p.open;
                    }
                }
                _c();
            };
            return _cls;
        }();
        /* uiDialog для работы с формами в диалогах */
        if (typeof window === 'object' && typeof window.document === 'object') { window._jqDialog = _jqDialog; }
    })(jQuery);
}else{
    alert('jquery.dialog.js say: jQuery is not loaded');
}