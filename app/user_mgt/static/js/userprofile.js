$(function(){
    var user = function(cp){
        var _cls = function(){
            var _this = this,_isInit;
            _this.moduleData = {};
            _this.passFrmName = 'UPass';
            _this.baseURL = '/users'
            _this.chgPassUrl = _this.baseURL+'/changePass/';
            _this.saveUInfUrl = _this.baseURL+'/save/';
            _this._$passFrm = $('form[name='+_this.passFrmName+']:first');
            _this.changePass = function(){
                var chgPassData = _this._getFrmData(_this.passFrmName),error='';
                // нужна проверка на не пустые поля
                if(_jsUtils.emptyStr==chgPassData.PasswordOld){
                    error = _this.moduleData.Errors['104'].replace(/#{field}/,_this.moduleData.interface.password);
                }
                if(_jsUtils.emptyStr==error && _jsUtils.emptyStr==chgPassData.NewPassword){
                    error = _this.moduleData.Errors['104'].replace(/#{field}/,_this.moduleData.interface.newpassword);
                }
                // проверка соответствия нового пароля и его подтверждения
                if(_jsUtils.emptyStr==error && chgPassData.NewPasswordCheck!=chgPassData.NewPassword){
                    error = _this.moduleData.Errors['110'].replace(/#{field}/,_this.moduleData.interface.newpassword);
                }
                // проверка соответсвия нового пароля правилам портала
                if(_jsUtils.emptyStr==error && _this.moduleData.minPaswdLength>chgPassData.NewPassword.length){
                    error = _this.moduleData.Errors['106']+' ('+_this.moduleData.minPaswdLength+')!';
                }
                if(_jsUtils.emptyStr!==error){
                    alert(error);
//                            _this.toggleLockFrmButtons(1);
                    return;
                }
//                        alert(chgPassData.Password);

                // теперь отправим данные и получим ответ
                $.post(_this.chgPassUrl,chgPassData,function(answ){
                    if(typeof void null!=typeof answ){
                        if(answ.state == 200){
                            alert(_this.moduleData.Msgs.chgPass);
                            _this._clearForm(_this._$passFrm);
                        }else{
                            alert(answ.msg);
                        }
                    }
                },'json');
            };

            _this.toggleDBGMode = function(){
                // this- is a pointer of button
                var $btn = $(this),flg=0,url='';
                flg = $btn.attr('mode');
                url = _this.baseURL+'/toggleDebugMode/'+((flg=='0')? 1:0);
                $.get(url,function(){
                    switch(flg){
                        case '0':
                            // послать запрос чтобы в сессию положили ключик и могли исп
                            $btn.attr('mode',1);
                            $btn.button('option','label',$btn.attr('oflabel'));
                            break;
                        case '1':
                            $btn.attr('mode',0);
                            $btn.button('option','label',$btn.attr('onlabel'));
                            break;
                    }
                });
            };

            _this._clearForm = function($f){
                if(0<$f.length){
                    $f.get(0).reset();
                }
            };

            _this._getFrmData = function(frmName){
                var $frm = $('form[name='+frmName+']'),odata;
                odata = _jsUtils.fToObj($frm.get(0));
                return odata;
            };

            _this.init = function(){
                // запросить интерфейсные и конфигурационные данные

                // навесить события
                $('form[name='+_this.passFrmName+']').find('button').click(function(){
                    _this.changePass();
                });

                $('button[name="ToggleBDGMode"]').click(_this.toggleDBGMode);
            };

            function __construct(pd){
                _this._clearForm(_this._$passFrm);
                // надо загрузить данные для модуля
                $.post(_this.baseURL+'/getModuleData/',null,function(amd){
                    _this.moduleData = amd;
                    _isInit = true;

                    _this.init();
                },'json');
            }
            _$box = $('#page-content-marker').parent();
            _this.baseURL = _$box.find('#js-base-url').val();
            _this.chgPassUrl = _this.baseURL+'/changePass/';
            _this.saveUInfUrl = _this.baseURL+'/save/';
            __construct(cp);

        };
        return new _cls(cp);
    }();
    $('.content-cols button').button();
});