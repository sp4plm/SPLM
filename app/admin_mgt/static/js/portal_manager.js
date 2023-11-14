/*!
 * Основной файл отвечающий за работу клиентской части административного интерфейса портала
 *
 * Используется файл jsutils.js - набор функций-утиллит на нативном javascript
 * @author Anton Novikov
 */
var Desktop, appAdmin, PageBlock, PageNavi, Page, MainPage;

Desktop = new Object({ _garbage:{} });

_jsUtils.extend(Desktop, _jsUtils);

PageBlock = function(){
    var cls = function(p){
        var _this = this;
        _this._tmpl = '<div></div>';
        _this.cls = 'BlockBox';
        _this.blkHeaderTpl = '<div class="header-footer ui-state-default ui-corner-all" style="padding: 3px 5px 5px; text-align: left; margin-bottom: 0.7em;line-height:normal;font-weight:bold;">#{label}</div>';
        _this.storage = null;
        _this.exists = function(){};
        _this._init = function(){
            // здесь будем производить настройки - аля конструктор, запускаем при
            // запуске блока
        };
        _this.run = function(iO){
            // запуск псевдо-конструктора
        };
        _this.hideBrothers = function(box){
            if(null!==box){
                $(box).find('.'+_this.cls).hide();
            }
        };
        _this.resize = function(){ };
        function _constructor(p){}
        _constructor(p);
    };
    return cls;
}();

/******** Блок приложения ***********************************/
appAdmin = function(sett){
    var _func = this; // в данном случае это window
    var _sO = new Object();
    _jsUtils.extend(_sO,_jsUtils);
    _sO.registerBlock = function(blkKey,blkCls,p){
        _sO[blkKey] = new blkCls({container:_sO,eventBus:'EvMan',constructorParams:p});
        _sO.regBlocks[blkKey] = null;
    };
    // инициализация блоков
    _sO.UsersManager = _sO.emptyFunc;
    _sO.PagesManager = _sO.emptyFunc;
    _sO.UserRolesManager = _sO.emptyFunc;
    _sO.lang = '';
    _sO.EvMan = new window._custEvents(); // наш менеджер событий
    _sO.regBlocks = {};
    // метод отвечает за выбор отображаемого блока
    _sO.init = function(mItemO){
        // устанавливаем язык приложения
        _sO.lang = mItemO.lang;
        switch(mItemO.code){
            case 'PortalPages':
                _sO.PagesManager.run(mItemO);
                break;
            case 'UserRoles':
                _sO.UserRolesManager.run(mItemO);
                break;
            default:
                _sO.EvMan.fire('SelectMenuItem',mItemO);
        }
        Desktop.EvMan.subscribe('pageResize',function(p){
            // организовываем проброс события для нашего приложения
            _sO.EvMan.fire('pageResize',p);
        });
    };
    return _sO;
};
/******** Блок приложения ***********************************/

PageNavi = function(){
    var cls = function(p){
        var $this = this,
        _$currItem = null,
        _currItemO = null,
        _loadFirstTO = '100',
        _loadTO = -1;
        $this.$container = null;
        $this.$menu = null;
        $this.tmpl = '<ul></ul>';
        $this.itmTmpl = '<li><a href="">!{#label}!</a></li>';
        $this.items = [];
        $this.cls = '';
        $this.ID = 'main-menu';
        $this.itmCls = '';
        $this.currItemCls = 'current-item';
        $this.langData = (typeof void null!=typeof p.langData)? p.langData:null;

        $this.checkMenu = function(){
            return ($this.$container.find($this.$menu).length===1);
        };
        $this.isEmpty = function(){
            return ($this.$menu.find('li').length===0);
        };
        $this.getItemObj = function(iC){
            var iT=null,kx,cnt=0;
            cnt = $this.items.length;
            for(kx=0;kx<cnt;kx++){
                if(iC===$this.items[kx].code){ iT = $this.items[kx]; break; }
            }
            if(null===iT){ throw new Error('Не существует пункта с указанным кодом '+iC+'!'); }
            return iT;
        };
        $this.cssSetCurrentItem = function(li){
            $this.$menu.find('li').removeClass($this.currItemCls);
            $(li).addClass($this.currItemCls);
        }
        $this.clickPoint = function(item){
            var _pC = $(item).attr('code');
            try{
                _currItemO = $this.getItemObj(_pC);
                // а теперь мы передаем функции управления приложению а уже оно само знает что делать с пунктом меню
                _currItemO.place = $('#'+_currItemO.targetBlkID);
                _currItemO.lang = Desktop.currPage.getLang();
                $this.cssSetCurrentItem(item);
                Desktop.app.init(_currItemO);
            }catch(e){ alert(e.toString()); }
        };
        $this.getCurrent = function(){ return _currItemO; };

        function _constructor(p){
            if(typeof void null===typeof p.menuContainer) throw new Error('Не указан контейнер для навигационного блока!');
            if(_jsUtils.tofS===typeof p.menuContainer){
                // предполагаем что мы передаем сюда идентификатор
                $this.$container = $('#'+p.menuContainer);
            }else{
                // либо уже сам элемент
                $this.$container = $(p.menuContainer);
            }
            if($this.$container.length<1){ throw new Error('Не удалось определить контейнер для блока навигации!'); }

            if(_jsUtils.tofU!==typeof p.menuID && _jsUtils.tofS===typeof p.menuID && ''!==p.menuID){ $this.ID = p.menuID; }
            if(_jsUtils.tofU!==typeof p.menuCls && _jsUtils.tofS===typeof p.menuCls && ''!==p.menuCls){ $this.cls = p.menuCls; }
            if(_jsUtils.tofU!==typeof p.itemCls && _jsUtils.tofS===typeof p.itemCls && ''!==p.itemCls){ $this.itmCls = p.itemCls; }
            // сперва инициализируем само меню
            if(!$this.checkMenu()){
                $this.$menu = $($this.tmpl);
                if(''!==$this.ID) $this.$menu.attr('id',$this.ID);
                $this.$container.prepend($this.$menu);
            }else{
                if(''===$this.ID){
                    throw new Error('Не известно из чего стряпать навигационный блок!');
                }else{
                    $this.$menu = $('#'+$this.ID);
                }
            }
            if(''!==$this.cls) $this.$menu.addClass($this.cls);
            // теперь создаем пункты навигации
            if(_jsUtils.tofU!==typeof p.items && _jsUtils.tofA==typeof p.items && 0<p.items.length){
                $this.items = p.items;
            }
            var kx,li = null,cnt=0;
            if($this.isEmpty()){
                cnt = $this.items.length;
                for(kx=0;kx<cnt;kx++){
                    li = $($this.itmTmpl.replace(/!{#label}!/,$this.items[kx].label));
                    li.attr('code',$this.items[kx].code);
                    li.find('a:first').attr('href','javascript:void(0)').click(function(){ $this.clickPoint($(this).parent()); });
                    $this.$menu.append(li);
                    $this.items[kx]['html'] = li;
                }
            }else{
                $this.$menu.find('li').each(function(){
                    var iO,li = this,code='';
                    $(li).find('a:first').attr('href','javascript:void(0)').click(function(){ $this.clickPoint($(this).parent()); });
                    code = $(li).attr('code');
                    if(_jsUtils.tofS===typeof code && _jsUtils.emptyStr!==code){
                        iO = $this.getItemObj(code);
                        iO['html'] = li;
                    }
                });
            }

            // теперь посмотрим с какого пункта следует начать загрузку :)
            cnt = $this.items.length;
            for(kx=0;kx<cnt;kx++){
                if(_jsUtils.tofU!==typeof $this.items[kx].isStarted && $this.items[kx].isStarted){
                    if(_jsUtils.tofU!==typeof $this.items[kx].html && 0<$($this.items[kx].html).length){
                        _loadTO = setTimeout(function(){
                            $($this.items[kx].html).find('a:first').trigger('click');
                            clearTimeout(_loadTO);
                        },_loadFirstTO);
                        break; // этим мы гарамнтируем что загрузим первый попавшийся :)
                    }
                }
            }
        } // end of the constructor
        _constructor(p);
    };
    return cls;
}();

Page = function(parent){
    var cls = function(p){
        var _this = this;
        var _pageLoader = null;
        var hasP = (typeof null===typeof p && null!==p);
        Page.superclass.constructor.call(_this, p);
        _this.minPageWidth = 1024;
        _this.minPageHeight = 768;
        _this.maxPageWidth = 1900;
        _this.maxPageHeight = 1200;
        _this.defWidth = (hasP && typeof void null!=typeof p.defWidth)? p.defWidth:'auto';
        _this.defHeight = (hasP && typeof void null!=typeof p.defHeight)? p.defHeight:'auto';
        _this._$pageBox = null;
        _this._pageBoxTmpl = '<div></div>';
        _this._pageBoxCls = (hasP && typeof void null!=typeof p.pageContainerCls)? p.pageContainerCls:'container';
        _this._pageBoxID = (hasP && typeof void null!=typeof p.pageContainerID)? p.pageContainerID:'page-container';
        _this.mainHeader = (hasP && typeof void null!=typeof p.header)? p.header:'';
        _this.Title = (hasP && typeof void null!=typeof p.title)? p.title:'';
        _this._layout = null;
        _this.layoutSettings = (hasP && typeof void null!=typeof p.layoutSettings)? p.layoutSettings:{applyDemoStyles: true};
        _this._lang = null;
        _this.langData = (typeof void null!==typeof p.langData)? p.langData:null;
        _this._template = (hasP && typeof void null!=typeof p.template)? p.template:null;
        _this._navi = null;

        _this.showLoader = function(){
            //_pageLoader.WFMLoader('show');
        }
        _this.hideLoader = function(){
            //_pageLoader.WFMLoader('hide');
        }

        _this.applyTemplate = function(){
            if(_this.tofS===typeof _this._template && _this.emptyStr!==_this._template){
                //_this._$pageBox.html(_this._template);
                _this._$pageBox.find('h1.page-main-header').html(_this.mainHeader);
            }
        };

        _this.createLayout = function(){
            if(!_this.isNull(_this.layoutSettings)){
                _this._$pageBox.layout(_this.laytoutSettings);
             }
        };

        _this.createNavi = function(naviCfg){
            try{
                _this._navi = new PageNavi(naviCfg);
            }catch(e){
                throw new Error('Не удалось создать блок навигации для страницы -> '+e.toString());
            }
        };
        _this.getCurrMenuItem = function(){ var i=null; if(_this.tofO===typeof _this._navi && null!==_this._navi){ i=_this._navi.getCurrent(); } return i; };

        _this.setSizesByRequiraments = function(){
            if(_this.tofU!==typeof _this._$pageBox && null!==_this._$pageBox){
                    if(0<_this._$pageBox.length){
                        _this._$pageBox.css({width:'100%',height:'100%'});
                        if($(window).width()<_this.minPageWidth){
                            _this._$pageBox.width(_this.minPageWidth);
                        }
                        if($(window).height()<_this.minPageHeight){
                            _this._$pageBox.height(_this.minPageHeight);
                        }
                        if($(window).width()>_this.maxPageWidth){
                            _this._$pageBox.width(_this.maxPageWidth);
                        }
                        if($(window).height()>_this.maxPageHeight){
                            _this._$pageBox.height(_this.maxPageHeight);
                        }
                    }
            }
            // теперь нужно отцентрировать контейнер по ширине страницы
            _this.centeredPageBox();
        }
        _this.centeredPageBox = function(){
            if(_this.tofU!==typeof _this._$pageBox && null!==_this._$pageBox){
                if(0<_this._$pageBox.length){
                    if(_this._$pageBox.width()===_this.maxPageWidth){
                        _this._$pageBox.css({margin:'0 auto'});
                    }
                }
            }
        }
        _this.getLang = function(){
            return _this._lang;
        };
        _this.setLang = function(){
            var metaName = 'content-language';
            $('head').find('meta').each(function(){
                if(!$(this).attr('http-equiv')){ return true; }
                if($(this).attr('http-equiv').toLowerCase()===metaName){
                    _this._lang = $(this).attr('content');
                    return false;
                }
            });
        };
        _this.resize = function(){
            _this.setSizesByRequiraments();
            // тепрь надо запустить цепочку ресайзов внутренних блоков
            // и начнем с раскладки страницы (layout)
            var p = {};
            if(null!==_this._$pageBox){
                p = {boxW:_this._$pageBox.width(),boxH:_this._$pageBox.height()};
            }else{
                p = {boxW:$(window).width(),boxH:$(window).height()}
            }
            Desktop.EvMan.fire('pageResize',p);
        };

        function _constructor(p){
            //_pageLoader = $('body').WFMLoader({img:'/img/loader.gif'});
            // создаем наше приложение
            // проверим если длина окна меньше минимальной ширины страницы,
            //  то выставляем бодику ширину минимальную
            //_this.resize();
            // определим текущий язык
            _this.setLang();
            // сперва соберем сведения о странице
            _this._$pageBox = $('.maincontent:first'); // _this._$pageBox = $(_this._pageBoxTmpl);
            //_this._$pageBox.addClass(_this._pageBoxCls);
            _this._$pageBox.attr('id', _this._pageBoxID);
            //$('body').prepend(_this._$pageBox);
            //_this.resize(); // на всякий пожарный
            // определим ее шаблон
            _this.applyTemplate();
            // определим ее раскладку (Layout)
            //_this.createLayout();
            if(hasP && typeof void null!=typeof p.navi && null!=p.navi){
                // создаем блок навигации
                //_this.createNavi(p.navi);
            }
            _this.hideLoader();
            window.onresize = function(){
                var wRTO = setTimeout(function(){
                    //_this.resize();
                    clearTimeout(wRTO);
                },'400');
            };
            if(_this.tofF===typeof p.onComplete){
                p.onComplete();
            }
        };

        _constructor(p); // вызов конструктора
    };
    _jsUtils.inherit(cls, parent);
    return cls;
}(_jsUtils.new() || function(){});

Desktop.EvMan = new window._custEvents(); // наш менеджер событий
// когда весь ДОМ якобы загрузился начинаем работу
$(function(){
    var lng, _url_pref, metaName = 'content-language';
    _url_pref = ''; // TODO: как заполнять переменную из шаблона, либо переписать административный интерфейс!
    if($('#app-base-pref').length>0){
        _url_pref = $('#app-base-pref').val();
        if('/' == _url_pref[_url_pref.length -1]) {
            _url_pref = _url_pref.substring(0, _url_pref.length -1);
        }
    }
    $('head').find('meta').each(function(){
        if(!$(this).attr('http-equiv')){ return true; }
        if($(this).attr('http-equiv').toLowerCase()===metaName){
            lng = $(this).attr('content');
            return false;
        }
    });
    $.post(_url_pref + '/portal/management/interfaceData/?lng='+lng,null,function(answ){
        if(typeof void null!==typeof answ && null!==answ){
            var r = 0;
            Desktop.app = appAdmin({'langData':answ.Pages});
            // вызываем событие что можно регистрировать на странице блоки
            Desktop.EvMan.fire('CanRegBlocks',{'langData':answ.Pages,'curLangCode':lng});
            // создаем нашу новую страницу в нашем Приложении Desktop и онаже является текущей
            Desktop.currPage = new Page({
                pageContainerCls:'container',
                pageContainerID:'main-page-box',
                template:'<div class="pane ui-layout-north"><h1 class="page-main-header"></h1><div class="lang-switch-pane"></div>\
                    </div>\
                    <div class="pane ui-layout-west" id="navi-box"><div id="user-info-box"><a href="javascript:void(0)" onclick="">'+answ.logoutBtn+'</a></div></div>\
                    <div class="pane ui-layout-center" id="NaviPageBox"></div>',
                header:answ.header,
                title:answ.title,
                langData:answ,
                navi:{
                        menuContainer:'navi-box',
                        menuID:'main-menu',
                        menuCls:'',
                        itmCls:'',
                        items:answ.navMenu,
                        langData:{Errors:answ.Errors.navi}
                    },
                onComplete: function(){
                    /*
                    $('#user-info-box a').click(function(){ $.post('/portal/man/logout/',{},function(ans){
                            if(typeof void null!=typeof ans){
                               // document.write('Для получения доступа авторизуйтесь пожалуйста, <a href="'+window.location.href+'">войти</a>!');
                               // document.write(answ.authPhrase.replace(/#{href}/,window.location.href));
                               // window.location.reload(window.location.href);
                            }
                        },'json');
                    });
                    */
                }
            });
        }
    },'json');
});