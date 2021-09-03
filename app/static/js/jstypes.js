(function(win,undefined){
    var clsTypes = function(){
        var _self = this;

        _self.emptyStr = '';
        _self.emptyFunc = function(){};
        _self.tofU = typeof undefined;
        _self.tofO = typeof {};
        _self.tofA = typeof [];
        _self.tofF = typeof _self.emptyFunc;
        _self.tofN = typeof 9;
        _self.tofS = typeof 'z';
        _self.tofB = typeof (1===1);

        _self.NaN = parseInt('z');

        function hasJsProp(v, propName){
            var flg = false;
            try{
                if(typeof void null !== typeof v[propName]){ flg = true; }
            }catch(err){ return false; }
            return flg;
        }

        _self.tof = function(z){ return typeof z; };

        _self.isUndefined = function(z){ return undefined === z; };

        _self.isObject = function(z){
            if(typeof z === _self.tofO){
                if(hasJsProp(z, '__proto__') && typeof z['__proto__'] === _self.tofO){
                    return true;
                }
            }
            return false;
        };

        _self.isArray = function(z){
            if(typeof z === _self.tofA){
                if(hasJsProp(z, 'length') && hasJsProp(z, 'values')){ return true; }
            }
            return false;
        };

        _self.isFunc = function(z){
            if(typeof z === _self.tofF){
                if(hasJsProp(z, 'name') && hasJsProp(z, 'arguments')){ return true; }
            }
            return false;
        };

        _self.isNumber = function(z){
            if(typeof z === _self.tofN){
                if(_self.NaN !== parseInt(z) || _self.NaN !== parseFloat(z)){ return true; }
            }
            return false;
        };

        _self.isString = function(z){
            if(typeof z === _self.tofS){
                if(hasJsProp(z, 'length') && hasJsProp(z, 'charAt')){ return true; }
            }
            return false;
        };

        _self.isBool = function(z){
            if(typeof z === _self.tofB){
                if(false === z || true === z){ return true; }
            }
            return false;
        };
    };
    if ('object' === typeof win && 'object' === typeof win.document) { win._jsTypes = new clsTypes(); }
})(window);