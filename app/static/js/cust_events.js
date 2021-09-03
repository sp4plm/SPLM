(function(win,undefined){
    /**
    * Ожидаем что уже есть объект по работе с типами win._jsTypes
    * если его нет то все рушится и мы прекращаем работу
    */
    if(undefined === win._jsTypes || typeof win._jsTypes !== typeof {}){
        return; // выходим из функции инициализации
    }
    var clsCustEvents = function(){
        var _self = this,
            _collect = {},
            _calls = {},
            _stack = [],
            _errors = {},
            _ExecuteFlg = 0,
            _ExecuteEv = '';

            _self.fire = function(eN, eArgs){
                var cals = 0, handlers = 0, iH;
                if(typeof void null === typeof _collect[eN]){ return ; }
                handlers = _collect[eN]['handlers'].length;
                if(0 === handlers){ return ; }
                for(iH=0;iH<handlers;iH++){
                    try{
                        if(win._jsTypes.isFunc(_collect[eN]['handlers'][iH])){
                            _collect[eN]['handlers'][iH](eN, eArgs);
                        }
                    }catch(err){ }
                }
            };

            _self.unsubscribe = function(eN, iH){
                if(typeof void null === typeof _collect[eN]){ return false; }
                if(iH > _collect[eN]['handlers'].length){ return false; }
                // не используем оператор delete для сохранения индексов массива
                _collect[eN]['handlers'][iH] = null;
            };

            _self.subscribe = function(eN, eH){
                var iH = -1;
                if(!win._jsTypes.isString(eN)){ return iH; }
                if(!win._jsTypes.isFunc(eH)){ return iH; }

                if(typeof void null === typeof _collect[eN]){
                    _collect[eN] = {'name': eN, 'handlers':[]};
                }

                _collect[eN]['handlers'].push(eH);
                iH = _collect[eN]['handlers'].length - 1;
                return iH;
            };
    };
    if ('object' === typeof win && 'object' === typeof win.document) { win._custEvents = clsCustEvents; }
})(window);