if(typeof void null!=typeof jQuery){
    (function($){
        var dN = 'WFMLoader'; // имя переменной для хранения данных об инициализированном плагине
        var cls = function(p){
            var _this = this; // ссылка на самого себя
            var $el, _initO;
            var _boxTmpl = '<div style="">&nbsp;</div>';
            var _$me = null;

            _this.img = '';

            _this.show = function(){
                _$me.show();
            };

            _this.hide = function(){
                _$me.hide();
            };
            // описываем метот инициализации
            function _constructor(p){
                $el = $(p.el);
                _initO = p.o;
                _$me = $(_boxTmpl);
                if(typeof void null!==typeof _initO.img){
                    _this.img = _initO.img;
                }
                if(''!==_this.img){
                    var img = '<img src="'+_this.img+'" />';
                    _$me.append(img);
                }
                _$me.width($el.width());
                _$me.height($el.height());
                _$me.css({position: _initO.position, 'background-color': _initO.bgcolor, 'text-align':'center'});
                var eP = $el.offset();
                _$me.offset({ top: eP.top, left: eP.left });
                _this.hide();
                $('body').append(_$me);
                if(_initO.runOnCreate){
                    _this.show();
                }
            };
            _constructor(p); // вызываем инициализирующий метод
            delete p;
            $.data(p.el, dN, _this); // сохраняем на елементе данные
        };
        var dS = {
            pvn: '0.0.1',
            bgcolor: '#FFFFFF',
            position: 'absolute',
            runOnCreate: true
        };
        $.fn.WFMLoader = function(p,cp){
            var o; // заготовка экземпляра объекта
            if(typeof {} === typeof p && null!==p){
                $.extend(dS,p);
            }
            this.each(function(i){
                o = $.data(this, dN);
                if(typeof {}===typeof o && null!==o){
                    if(typeof 'z'===typeof p && ''!==p){
                        if(typeof void null!==typeof o[p]){
                            o[p](cp);
                        }
                    }
                    return false; // переходим к объекту со следующей итерацией
                }
                dS.myInd = i;
                new cls({el:this,o:dS});
            });
            return o || this;
        };
    })(jQuery);
}else{
    alert('jQuery plugin "WFMLoader" say: jQuery lib is not loaded');
}