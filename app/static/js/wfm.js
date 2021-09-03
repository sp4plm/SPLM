/*!
 * Регистрируем и описываем namespace для работы нашей административной части WFM (Web For Man)
 * Copyright 2013 PKF VNIIAES
 *
 * CreatDate: 2013-09-19T12:19Z
 * @author Anton Novikov
 */
(function( window, undefined ) {
    var WFM = {};

    WFM.EventsManager = function(){
        var cls = function(p){
            var _this = this,
            _collection = {},
            _calls = {},
            _stack = [],
            _errors = {},
            _ExecuteFlg = 0,
            _ExecuteEv = '';

            function _addEvent(eN, cF){
                if(typeof void null===typeof _collection[eN]){
                    _collection[eN] = [];
                }
                _collection[eN].push(cF);
                return _collection[eN].length-1;
            }

            function _addError(eN,i,p,er){
                if(typeof void null===typeof _errors[eN]){
                    _errors[eN] = [];
                }
                var t = new Date();
                _errors[eN].push({'hNum':i,'hP':p,'cE':err,'time':t.getTime()});
            }

            function _whoExecute(){ return _ExecuteEv; }
            function _isExecute(){ return _ExecuteFlg; }
            function _ev_startFire(eN){ _ExecuteFlg = 1; _ExecuteEv = eN; }
            function _ev_stopFire(){ _ExecuteFlg = 0; _ExecuteEv = ''; _stackReader(); }
            function _stackReader(){
                var kx,cnt=0;
                cnt = _stack.length;
                if(cnt>0){
                    // всегда выполняем событие в порядке поступления очередности
                    _this.fire(_stack[0][0],_stack[0][1]);
                    // а теперь почистим то что отправили на выполнение
                    _stack[0] = null; delete _stack[0];
                }
            }


            function _endSubsExecution(evN,subsID){
                if(typeof void null===typeof _calls[evN]){ return ; }
                _calls[evN].cntAnsC--;
                if(0===_calls[evN].cntAnsC){ _calls[evN] = null; delete _calls[evN]; }
            }

            _this.subscribe = function(eN,cF){
                if(typeof 'z'!==typeof eN || (typeof 'z'===typeof eN && ''===eN)){
                    throw new Error('Не указано имя события для подписки!');
                }
                if(typeof function(){}!==typeof cF){
                    throw new Error('Не указана функция-триггер для вызова при возникновении события "'+eN+'"!');
                }
                return _addEvent(eN, cF);
            };
            _this.unsubscribe = function(eN,i){
                if(typeof 'z'===typeof eN && ''!==eN && typeof []===typeof _collection[eN]){
                    if(typeof void null!==typeof _collection[eN][i]){
                        // не используем оператор delete чтобы не сбросить индексацию массива
                        _collection[eN][i] = null;
                    }
                }
            };
            _this.fire = function(eN,p){
                if(typeof []!==typeof _collection[eN]){ return ; }
                if(typeof void null===typeof _calls[eN]){
                    _calls[eN] = {'flg':false,'cntC':_collection[eN].length,'cntAnsC':_collection[eN].length};
                }else{
//                    if(_calls[eN].cntAnsC>0){ return ; }
                }
                if(_whoExecute()!==eN){
                    if(_isExecute()!==1){
                        _ev_startFire(eN);
                        var cnt = _collection[eN].length;
                        if(cnt>0){
                            var kx;
                            for(kx=0;kx<cnt;kx++){
                                if(typeof function(){}!==typeof _collection[eN][kx]) continue;
                                try{
                                    _collection[eN][kx](p,function(){
                                        // здесь мы будем посчитывать флаги для выполнения события
                                        // то есть пока все подписчики не скажут нам что они выполнились
                                        // это событие исполняться не будет !!!!
                                        _endSubsExecution(eN,kx);
                                    });
                                }catch(err){
    //                                _addError(eN,kx,p,err); // будем складывать ошибки выполнения отработки на событиях
                                    // далее можно будет выдавать эти ошибки по контексту
                                }
                            }
                        }
                        _ev_stopFire();
                    }else{
                        // кладываем в стек очередности событий
                        _stack.push([eN,p]);
                    }
                }else{
                    // защита от повторного запуска события
                }
            };

            function _constructor(p){};
            _constructor(p);
        };
        return cls;
    }();

    if (typeof window === 'object' && typeof window.document === 'object') { window.WFM = WFM; }
})(window);