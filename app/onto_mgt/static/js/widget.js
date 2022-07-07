if(typeof void null!=typeof jQuery){
    // открытие/скрытие таблицы по клику на +/-
    $(function() {
        $('.header-section-toggler').click(function(){
            var $elem, $welem, $wgt0;
            $elem = $(this);
            if ($elem.hasClass('xicon-close')) {
                $elem.removeClass('xicon-close');
                $elem.addClass('xicon-open');
                // теперь надо создать виджет если не создан
                if ($elem.next('.content-header').next().length > 0) {
                    $elem.next('.content-header').next().show()
                }
            } else {
                $elem.removeClass('xicon-open');
                $elem.addClass('xicon-close');
                // теперь просто скроем виджет
                if ($elem.next('.content-header').next().length > 0) {
                    $elem.next('.content-header').next().hide()
                }
            }
        }); 
    });(jQuery);
}