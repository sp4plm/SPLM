(function(win,undefined){
    var Page = function(parent){
        var cls = function(p){
            var $this = this,
                _pageLoader = null,
                hasP = (typeof null===typeof p && null!==p);
            Page.superclass.constructor.call($this, p);
            $this.minPageWidth = 980;
            $this.minPageHeight = 768;
            $this.maxPageWidth = 1920;
            $this.maxPageHeight = 1080;
            $this.defWidth = (hasP && typeof void null!=typeof p.defWidth)? p.defWidth:'auto';
            $this.defHeight = (hasP && typeof void null!=typeof p.defHeight)? p.defHeight:'auto';
            $this._$pageBox = (hasP && typeof void null!=typeof p.pageBox)? p.pageBox:null;
            $this._pageBoxTmpl = '<div></div>';
            $this._pageBoxCls = (hasP && typeof void null!=typeof p.pageContainerCls)? p.pageContainerCls:'container';
            $this._pageBoxID = (hasP && typeof void null!=typeof p.pageContainerID)? p.pageContainerID:'page-container';
            $this.mainHeader = (hasP && typeof void null!=typeof p.header)? p.header:'';
            $this.Title = (hasP && typeof void null!=typeof p.title)? p.title:'';
            $this._layout = null;
            $this.layoutSettings = (hasP && typeof void null!=typeof p.layoutSettings)? p.layoutSettings:null;
            $this._lang = null; // код языка для страницы
            $this._template = (hasP && typeof void null!=typeof p.template)? p.template:null;
            $this._navi = null;
            $this.naviRoot = null;
            $this.naviBox = null;
            $this.EvMan = null; // менеджер событий
            $this.app = null; // бек линк на объект приложение работающее на странице
            $this.widgets = {}; // коллекция виджетов на странице
            $this.appBlocks = {}; // коллекция блоков на странице
            $this.user = null;
            $this.pageO = null;

            $this.showLoader = function(){
                _pageLoader.WFMLoader('show');
            }
            $this.hideLoader = function(){
                _pageLoader.WFMLoader('hide');
            }

            $this.logg = function(msg){
                if(typeof void null !== typeof console && typeof void null !== typeof console.log){
                    console.log(msg);
                }
            };

            $this.applyTemplate = function(){
                if($this.tofS===typeof $this._template && $this.emptyStr!==$this._template){
                    $this._$pageBox.html($this._template);
                    $this._$pageBox.find('h1.page-main-header').html($this.mainHeader);
                }
            };

            $this.createLayout = function(){
                if(!$this.isNull($this.layoutSettings)){
                   $this._$pageBox.layout($this.laytoutSettings);
                }
            };

            $this.createNavi = function(naviCfg){
                try{
                    $this._navi = new PageNavi(naviCfg);
                }catch(e){
                    throw new Error('Не удалось создать блок навигации для страницы -> '+e.toString());
                }
            };
            $this.getCurrMenuItem = function(){ var i=null; if($this.tofO===typeof $this._navi && null!==$this._navi){ i=$this._navi.getCurrent(); } return i; };

            $this.setSizesByRequiraments = function(){
                if($this.tofU!==typeof $this._$pageBox && null!==$this._$pageBox){
                        if(0<$this._$pageBox.length){
                            var dW,dH;
                            dW = $this._$pageBox.outerWidth(true)-$this._$pageBox.width();
                            dH = $this._$pageBox.outerHeight(true)-$this._$pageBox.height();
                            $this._$pageBox.css({width:'auto',height:'auto'});
                            if($(window).width()<$this.minPageWidth){
                                $this._$pageBox.width($this.minPageWidth-dW);
                            }
                            if($(window).width()>$this.maxPageWidth){
                                $this._$pageBox.width($this.maxPageWidth-dW);
                            }
                            if($(window).height()<$this.minPageHeight){
//                                $this._$pageBox.height($this.minPageHeight-dH);
                            }
                            if($(window).height()>$this.maxPageHeight){
//                                $this._$pageBox.height($this.maxPageHeight-dH);
                            }
                        }
                }
                // теперь нужно отцентрировать контейнер по ширине страницы
                $this.centeredPageBox();
            }
            $this.centeredPageBox = function(){
                if($this.tofU!==typeof $this._$pageBox && null!==$this._$pageBox){
                    if(0<$this._$pageBox.length){
                        if($this._$pageBox.width()==$this.maxPageWidth){
                            $this._$pageBox.css({'margin-left':'auto','margin-right':'auto'});
                        }
                    }
                }
            }
            $this.getLang = function(){
                return $this._lang;
            };
            $this.setLang = function(){
                var metaName = 'content-language';
                $('head').find('meta').each(function(){
                    if(!$(this).attr('http-equiv')){ return true; }
                    if($(this).attr('http-equiv').toLowerCase()===metaName){
                        $this._lang = $(this).attr('content');
                        return false;
                    }
                });
            };
            $this.resize = function(){
                $this.setSizesByRequiraments();
                // тепрь надо запустить цепочку ресайзов внутренних блоков
                // и начнем с раскладки страницы (layout)
                var p = {};
                if(null!==$this._$pageBox){
                    var dW,dH;
                    dW = $this._$pageBox.outerWidth(true) - $this._$pageBox.width();
                    dH = $this._$pageBox.outerHeight(true) - $this._$pageBox.height();
                    p = {boxW:$this._$pageBox.width()-dW,boxH:$this._$pageBox.height()-dH};
                }else{
                    p = {boxW:$(window).width(),boxH:$(window).height()}
                }
                $this.fireEvent('pageResize',p);
                _navi2center();
            };

            $this.regWidget = function(code,wgtO){
                if($this.tofS!==typeof code || ($this.tofS==typeof code && $this.emptyStr===code)){
                    throw new Error('Не указан код виджета!');
                }
                if($this.tofO!==typeof wgtO || $this.isNull(wgtO)){
                    throw new Error('Попытка зарегистрировать неизвестность с кодом "'+code+'"!');
                }
                if($this.tofU===typeof $this.widgets[code]){
                    $this.widgets[code] = wgtO;
                }
            };

            $this.fireEvent = function(evN,evP){
                if($this.tofU!==typeof $this.EvMan){
                    $this.EvMan.fire(evN,evP);
                }
            };

            $this.listenEvent = function(evN,callBack){
                if($this.tofU!==typeof $this.EvMan){
                    $this.EvMan.subscribe(evN,callBack);
                }
            };

            $this.setPagebox = function(div){
                $this._$pageBox = $(div);
            }

            $this.addScript = function(url){
                if($this.tofS===typeof url && $this.emptyStr!==url){
                    var scr = $('<script></script>');
                    scr.attr('type','text/javascript');
                    scr.attr('charset','UTF-8');
                    scr.attr('src',url);
                    if($('#jsscripts').length>0){
                        $('#jsscripts').append(scr);
                    }else{
                        $('head').append(scr);
                    }
                }
            };

            function _getNaviItemsWidthSumm(){
                var sum = 0;
                $this.naviBox.find('li').each(function(){
                    sum += parseInt($(this).outerWidth(true));
                });
                return sum;
            }

            function _navi2center(){
                if(null!=$this.naviRoot){
                    var pdW,pdH,sdW,sdH,mL,nW,pW,sW,summ=0;
                    $this.naviBox.find('li').each(function(){ summ += parseInt($(this).outerWidth(true)); });
//                    $this.naviRoot.width(summ);
                    pW = $this.naviBox.width();
                    sW = $this.naviRoot.width();
                    pdW = $this.naviBox.outerWidth(true)-pW;
                    pdH = $this.naviBox.outerHeight(true)-$this.naviBox.height();
                    sdW = $this.naviRoot.outerWidth(true)-sW;
                    sdH = $this.naviRoot.outerHeight(true)-$this.naviRoot.height();
                    // ситуация когда мы вписываемся
                    if($this.naviBox.outerWidth(true)>summ){
                        nW = $this.naviRoot.outerWidth(true)-sdW;
//                        $this.naviRoot.width(nW);
                        // теперь будем центрировать
                        mL = Math.ceil((($this.naviBox.width()-nW)/2));
                        $this.naviRoot.css({'margin-left':mL+'px'});
                    }else{
                        // ситуация когда мы не вписываемся
                        $this.naviRoot.width($this.naviBox.outerWidth(true)-pdW-sdW);
                        // теперь будем центрировать
                    }
                }
            }
            
            function _fixNaviItemWidth(){
                var baseW = $this.naviRoot.width(),summ=0,cnt,iW;
                cnt = $this.naviBox.find('li').length;
//                $this.naviBox.find('li').each(function(){ summ += parseInt($(this).outerWidth(true)); });
                summ = _getNaviItemsWidthSumm();
                if(summ>(baseW-10)){
                    iW = Math.floor(baseW/cnt);
                    iW = Math.floor((baseW/iW)*10)/10;
                    $this.naviBox.find('li').each(function(){ $(this).css({'width':iW+'%'}); });
                }
            }

            function _constructor(p){
                _pageLoader = $('body').WFMLoader({img:'/static/img/loader.gif'});
                $this.EvMan = new WFM.EventsManager(); // наш менеджер событий
                // навишиваем событие на вылогинивание пользователя
                $('#user-box a.logout-link').click(function(){ $(this).parent().find('form[name=userLogOut]').trigger('submit'); });
                // сперва соберем сведения о странице
                // определим текущий язык
                $this.setLang();
                /*****************************************************/
                if($this.tofU===typeof $this._$pageBox){
                    $this._$pageBox = $($this._pageBoxTmpl);
                    $('body').prepend($this._$pageBox);
                }
                $this._$pageBox.addClass($this._pageBoxCls);
                $this._$pageBox.attr('id', $this._pageBoxID);
//                $this.resize(); // на всякий пожарный
                // определим ее шаблон
                $this.applyTemplate();
                // определим ее раскладку (Layout)
                $this.createLayout();
                //$(window).resize(function(ev){ var wRTO = setTimeout(function(){ $this.resize(); clearTimeout(wRTO); },'600'); });
                if(hasP){
                    // создаем блок навигации
                    if(typeof void null!=typeof p.navi && null!=p.navi){ $this.createNavi(p.navi); }
                    if(typeof void null!=typeof p.naviRoot && null!=p.naviRoot){
                        $this.naviRoot = $(p.naviRoot); $this.naviBox = $this.naviRoot.parent();
                        _navi2center();
                        _fixNaviItemWidth();
                    }
                    if($this.tofF===typeof p.onComplete){ p.onComplete(); }
                }
                $this.hideLoader();
                /*****************************************************/
            };
            _constructor(p); // вызов конструктора
        };
        _jsUtils.inherit(cls, parent);
        return cls;
    }(_jsUtils.new() || function(){});
    if (typeof window === 'object' && typeof window.document === 'object') { window._webPageJS = Page; }
})(window);