(function(win,undefined){
    var wW, wH, wP, wPT, wPL;

    wW = win.width
    if(typeof void null!==typeof jQuery){
        (function($){
            // будем выставлять высоту контейнера если контента не хватает
            // сперва получим размеры окна
            // затем получим содержимо боди
            // определим какой элемент надо растягивать по высоте
            // считаем сумму внешних высот все элементов заисключением выбранного в предыдущем пункте
            // вычитаем из высоты окна
            // ************************************************************ //
            function setRelativeHeight2($parent, $child, exceptSiblings) {
                var pH, difH, setH, selfH;
                // если флаг выставлен в true значит ненадо вычитать высоту братьев
                // если
                if(typeof true !== typeof exceptSiblings
                   || typeof void null === typeof exceptSiblings
                   || null == exceptSiblings) {
                    exceptSiblings = false;
                }
                pH = $parent.height();
                // нужно сделать ветку для определения возможной высоты боди
                // так как иногда оно не растянуто по высоте
                if($('body').get(0) === $parent.get(0)){
                    wH = window.innerHeight;
                    if(pH < wH) {
                        pH = wH - ($parent.outerHeight()-pH);
                    }
                }
                setH = 0;
                difH = 0;
                // должно выполняться всегда
                if(!exceptSiblings) {
                    $parent.children().each(function(){
                        if($(this).get(0) != $child.get(0)) {
                            difH += $(this).outerHeight();
                        }
                    });
                }

                if(pH > difH) {
                    setH = pH + difH;
                }
                if(0 < setH) {
                    selfH = 0;
                    selfH = $child.outerHeight() - $child.height();
                    if(selfH < setH){
                        setH -= selfH;
                    }
                    $child.height(setH)
                }
            }
            $(function(){
                // будем инициировать изменение размера окна

                var $body, $pageContent, $parentViewBox, $viewBox;
                $body = $('body');
                $pageContent = $('body > div.container-fluid:first');
                if(0 < $pageContent.length){
                    setRelativeHeight2($body, $pageContent);
                    $viewBox = $pageContent.find('div.maincontent:first');
                    if(0 < $viewBox.length) {
                        // выбирем дополнительно для пересчета высоты в переменной - на всякий пожарный
                        $pageContent = $('body > div.container-fluid:first');
                        $parentViewBox = $viewBox.parent();
                        setRelativeHeight2($pageContent, $parentViewBox);
                        // перевыбираем для пересчета
                        $parentViewBox = $viewBox.parent();
                        // теперь изменим размер нужного контейнера
                        setRelativeHeight2($parentViewBox, $viewBox,true);
                    }
                }

            });
        })(jQuery);
    }else{
        alert('Main.js say: jQuery lib is not loaded');
    }
    if ('object' === typeof win && 'object' === typeof win.document) {  }
})(window);