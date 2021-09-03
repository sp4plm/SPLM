/*!
 * _jsUtils v0.0.1
 *
 * Copyright 2013 Anton Novikov
 *
 * CreatDate: 2013-09-18T12:43Z
 * @author Anton Novikov
 */
(function( window, undefined ) {

    var tofU = typeof undefined,
        tofO = typeof {},
        tofA = typeof [],
        tofF = typeof function(){},
        tofN = typeof 9,
        tofS = typeof 'z',
        tofB = typeof (1===1),
        emptyStr = '',
        _jsUtils = function(){
            // описание свойств и методов объекта
            var _self = { '#Garbage':{} };
            _self.tofU = tofU;
            _self.tofO = tofO;
            _self.tofA = tofA;
            _self.tofF = tofF;
            _self.tofN = tofN;
            _self.tofS = tofS;
            _self.tofB = tofB;
            _self.emptyStr = emptyStr;
            _self.emptyFunc = function(){ };
            _self.isNull = function(o){ return _self.tofO === typeof o && null===o; };
            _self.isUndefined = function(o){ return _self.tofU === typeof o; };
            _self.isEmptyObj = function (o){ if(!_self.isUndefined(o) && !_self.isNull(o)) for(var kI in o){ return _self.isUndefined(o[kI]); } return true };
            _self.ocount = function(obj){
                if(_self.isUndefined(obj) || _self.isNull(obj)){ return obj; }
                var k,z = 0;
                if(typeof obj === typeof {})
                    for(k in obj)
                        if(obj.hasOwnProperty(k))
                            z++;
                return parseInt(z);
            };
            _self.isArray = function(a){ return !_self.isUndefined(a) && !_self.isNull(a) && !_self.isUndefined(a.length); };
            _self.inArray = function(arr,par){
                var answer = 0;
                if(arr && null!==arr && arr.length>0){
                    var z=0,cnt = arr.length;
                    for(z=0;z<cnt;z++){
                        if(arr[z] === par){ answer=1; break; }
                    }
                }
                return answer;
            };
            _self.arraySearch = function(arr,par){
                var answer = 0;
                if(arr && null!==arr && arr.length>0){
                    var z=0,cnt = arr.length;
                    for(z=0;z<cnt;z++){
                        if(arr[z] === par){ answer=z; break; }
                    }
                }
                return answer;
            };
            _self.eval = function(toEval,context){
                if(_self.isUndefined(context)){ context = 1; }
                if(!_self.isUndefined(toEval) && typeof 'z'===typeof toEval && ''!==toEval && '()'!==toEval){
                    try{
                        if(context===1){
                            toEval = eval(toEval);
                        }else if(typeof {}===typeof context){
                            with(context){
                                toEval = eval(toEval);
                            }
                        }else{
                            toEval = (1,eval)(toEval); // подсмотрено на хабре (изменение контекста функции eval на глобальный)
                        }
                    }catch(e){ alert('Не удалось интерпретировать значение "'+toEval+'"! '+e.toString()); }
                }
                return toEval;
            };
            _self.rand = function(){ return Math.floor(Math.random()*10000); };
            _self.genHash = function(){
                var hash,time,cntS,
                    t=[],
                    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
                    symbols = ['`','!','@','#','$','%','^','&','*','(',')','-','+','=','_','[',']','{','}',':',';','/','?','<','>','\'','"','\\'],
                    numbers = ['0','1','2','3','4','5','6','7','8','9'],
                    group = 8,
                    delim = '-',
                    kx =0, step=0,cnt=0,diff=0,
                    d = new Date();
                    time = ''+d.getTime();
                    cnt = Math.ceil(time.length/group);
                    cntS = letters.length;

                function _randSymb(){
                    var i = Math.floor(Math.random()*(0-(cntS-1)))+0;
                    if(i<0){ i = i*-1; }
                    return letters[i].toUpperCase();
                }

                function _randStr(l){
                    if(typeof void null==typeof l || typeof 9 !==typeof l){ l=group; }
                    var str='',x =0;
                    for(x=0;x<l;x++){ str += _randSymb(); }
                    return str;
                }

                for(kx=0;kx<cnt;kx++){
                    if((step+group)>(time.length-1)){
                        if(kx==0){
                            t.push(time);
                        }else{
                            // сохраняем последний элемент - так как его длина меньше чем шаг
                            t.push(time.substr(step,(time.length-step)));
                        }
                        break;
                    }
                    t.push(time.substr(step,group));
                    step += group;
                }
                // теперь нам надо дополнить последний элемент, если он меньше шага
                cnt = t.length;
                if(group>t[cnt-1].length){
                    var last = cnt-1;
                    t[last] += _randStr(group-t[last].length);
                }
                // добавляем еще один элемент в массив - часть переменной :)
                t.push(_randStr());
                hash = t.join(delim);
                return hash;
            };
            _self.toBoolean = function(v){ return (v)? true: false; };
            _self.dateToISO_8601 = function(strNormDate){
                var mas=[],str = '';
                if(str===strNormDate){ return strNormDate; }
                mas = strNormDate.split('.').reverse();
                mas[0] = mas[0].substr(2,2);
                return mas.join('-');
            };
            _self.dateToDateObj = function(strNormDate){
                var str = '';
                if(_self.isUndefined(strNormDate)){ return str; }
                if(str===strNormDate){ return strNormDate; }
                var mas=[];
                mas = strNormDate.split('.').reverse();
                mas[1]--;
                return new Date(mas[0], mas[1],mas[2], 0, 0, 0, 0);
            },
            _self.sqlDateToNormal = function(sqlDateStr){
                var str = '';
                if(_self.isUndefined(sqlDateStr)){ return str; }
                if(_self.isNull(sqlDateStr)){ return str; }
                if(str===sqlDateStr){ return str; }
                return sqlDateStr.split('-').reverse().join('.');
            },
            _self.inherit = function(o,p){ function z(){}; z.ptototype = p.prototype; o.prototype = new z(); o.prototype.constructor = o; o.superclass = p.prototype; };
            _self.extend = function(o){
                var i,prop,cnt=0,exts = Array.prototype.slice.call(arguments, 1); cnt = exts.length;
                for (i = 0; i < cnt; ++i) {
                    for (prop in exts[i]) {
                        if('new'===prop) continue;
                        if (typeof void null===typeof prop) { continue; }
                        o[prop] = exts[i][prop];
//                        o[prop] = function (ext, prop) { return function () { ext[prop].apply(this, arguments); }; }(exts[i], prop);
                    }
                }
            };
            _self.mixin = function(o){
                var i,prop,cnt=0,mixins = Array.prototype.slice.call(arguments, 1); cnt = mixins.length;
                for (i = 0; i < cnt; ++i) {
                    for (prop in mixins[i]) {
                        if('new'===prop) continue;
                        if (typeof void null===typeof prop) { continue; }
                        o.prototype[prop] = function (mixin, prop) { return function () { mixin[prop].apply(this, arguments); }; }(mixins[i], prop);
//                        bindMethod = function (mixin, prop) { return function () { mixin[prop].apply(this, arguments); }; };
//                        o.prototype[prop] = bindMethod(mixins[i], prop);
                    }
                }
            };
            _self.toString = function(f){
                var o;
                if(tofU!==typeof f && null!=f){
                    var kx; o={};
                    for(kx in f){
                        if(!f.hasOwnProperty(kx)){ continue; }
                        o[kx]=f[kx];
                    }
                }else{ o = this; }
                return _self.oJSON.make(o);
            };
            _self.objectToString = function(cObj,propDelim){
                if(_self.isUndefined(propDelim)){ propDelim = ';'; }
                var k = null,str = '';
                if(!_self.isEmptyObj(cObj)){
                    for(k in cObj){
                        str += (''===str)? k+':'+cObj[k]:propDelim+k+':'+cObj[k];
                    }
                }
                return str;
            };
            _self.gc = function(_myobj){
                if(!_self.isEmptyObj(_myobj)){
                    var _kk1, _kk2=0,_nObj= new Array(), _chMyObj = _myobj.childNodes, _chMyObj_l = _chMyObj.length;
                    for(_kk1=0;_kk1<_chMyObj_l;_kk1++){
                        if(_chMyObj[_kk1].nodeType===1){
                            _nObj[_kk2]=_chMyObj[_kk1];
                            _kk2++;
                        }
                    }
                    return _nObj;
                }
                return null;
            };
            _self.fToObj = function(_myF){
                var val,_kk, _myNobj = new Object(), _myFch = _myF.elements, _myFch_l = _myFch.length,_val='#!null!#';
                for(_kk=0;_kk<_myFch_l;_kk++){
                    val=_val;
                    if(_self.isUndefined(_myFch[_kk].name)){ continue; } // если нет имени в объект не должно попасть
                    if (_myFch[_kk].type==='checkbox' || _myFch[_kk].type==='radio'){
                        if (_myFch[_kk].checked){
//                            _myNobj[_myFch[_kk].name] = _myFch[_kk].value;
                            val = _myFch[_kk].value;
                        }
                    }else{
//                        _myNobj[_myFch[_kk].name] = _myFch[_kk].value;
                        val = _myFch[_kk].value;
                    }
                    if(val!==_val){
                        if(_myFch[_kk].name.match(/\[\]$/)){
                            // значит это массив
                            if(_self.tofU===typeof _myNobj[_myFch[_kk].name]){
                                _myNobj[_myFch[_kk].name] = [];
                            }
                            _myNobj[_myFch[_kk].name].push(val);
                        }else{
                            _myNobj[_myFch[_kk].name] = val;
                        }
                    }
                }
                return _myNobj;
            };
            _self.clone = function(o){
                if(_self.isUndefined(o) || _self.isNull(o)){ return o; }
                var k, newO={};
                for(k in o){ if(o.hasOwnProperty(k)){ newO[k] = _self.clone(o[k]); } }
                return newO;
            };
            /******************** JSON [ ****************************************/
            _self.oJSON = new function(){
                var _jO = this;
                var escapee = { '"': '"', '\\': '\\', '/': '/', b: '\b', f: '\f', n: '\n', r: '\r', t: '\t' };
                function o2s(o){
                    var json = '', kk = null;
                    if(o===null){ return o; }
                    json += '{';
                    for(kk in o){
                        // выходим из пустого объкта
                        if(typeof void null===typeof kk) break;
                        json += '"'+kk+'":'+v2j(o[kk]);
                        json += ',';
                    }
                    if(json.length>1){ json = json.substr(0,json.length-1); }
                    json += '}';
                    return json;
                }
                function a2s(a){
                    var json = '', cnt = 0,k = 0;
                    cnt=a.length;
                    json += '[';
                    if(cnt>0){
                        for(k=0;k<cnt;k++){
                            if(typeof void null=== typeof a[k]) continue;
                            json += v2j(a[k]);
                            if(k<(cnt-1)){
                                json += ',';
                            }
                        }
                    }
                    json += ']';
                    return json;
                }
                function v2j(v){
                    var json = '', typeofV = null;
                    typeofV = typeof v;
                    if(typeofV===_self.tofO){
                        if(v!==null && typeof void null !== typeof v.length){ typeofV = 'array'; }
                    }
                    switch(typeofV){
                        case 'function': json = v.toString(); break;
                        case 'string': json = '"'+escStr(v)+'"'; break;
                        case 'int':
                        case 'integer':
                        case 'number': json = v; break;
                        case 'boolean': json = (v)? 'true':'false'; break;
                        case 'array': json = a2s(v); break;
                        case 'object': json = o2s(v); break;
                    }
                    return json;
                }
                function escStr(str){
                    var nS = '', kx=0, cnt = str.length, ch = '';
                    for(kx=0;kx<cnt;kx++){
                        ch = str.charAt(kx);
                        nS += (('"'===ch)? '\\'+ch:ch);
        //                nS += ((typeof void null!==typeof escapee[ch])? '\\'+ch:ch);
                    }
                    return nS;
                }
                _jO.make = function(collect){
                    var json = '', typeOfCollect = null;
                    typeOfCollect = typeof collect;
                    if(typeOfCollect===_self.tofO){
                        if(typeof void null !== typeof collect.length && collect!==null){ typeOfCollect = 'array'; }
                    }
                    switch(typeOfCollect){
                        case 'array': json = a2s(collect); break;
                        case 'object': json = o2s(collect); break;
                    }
                    return json;
                };
                _jO.parse = function(jsonStr){ var o = {};
                    try{
                        o = _self.eval('('+jsonStr+')');
                    }catch(err){ o=''; }
                    if('()'===o){ o=''; }
                    return o; };
                _jO.jsonToArray = function(massStr){};
                _jO.jsonToObj = function(objStr){};
                _jO.normValueForStructure = function(val,type){};
            };
            // метод для конструирования класса из объекта
            _self.new = function(me){ return function(){ var cls = function(){ var kx; for(kx in me){ if('new'===kx) continue; this[kx] = me[kx]; } }; return cls; }; }(_self);

            /**
             * метод получения данных из переменной которая представленна строкой
             * только для текущего window
             * @param {string} varname - имя переменной в json-notation
             * @returns {mixed} - значение переменной по имени varname
             */
            _self.castEval = function(varname){
                var path = varname.split('.'), 
                    cnt=path.length,
                    kx, key, _var, val;
                for(kx=0;kx<cnt;kx++){
//                    key =path[kx];
                    key = (typeof parseInt(path[kx])==typeof parseInt('zn'))? path[kx]:parseInt(path[kx]);
                    val = (kx==0)? window[key]: val[key]
                }
                return val;
            };

            return _self;
        }();

    if (typeof window === 'object' && typeof window.document === 'object') { window._jsUtils = _jsUtils; }
})(window);