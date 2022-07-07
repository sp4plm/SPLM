if(typeof void null!=typeof jQuery){
    (function($){
        var _$grid;
        var _grids = 0;

        function _2HtmlLink_frmt(cellvalue, options, rowObject) {
            return $(cellvalue);
        }

        $('.jqgrid-box').each(function(){
            var _jsdata,
                _$grid,
                cfgObj, $jqTbl,
                _gid = 'grid-' + String(_grids);

            _jsdata = JSON.parse($(this).find('.json-source:first').html());
            // если передали имя переменой
            if (typeof "z" === typeof _jsdata) {
                _jsdata = window[_jsdata];
            }
            if (typeof void null != typeof _jsdata['colModel']){
                // считаем что таблица получилась
                // назначаем специализированный форматтер для  первой колонки
                _jsdata['pager'] =  _gid+'-pager';

                $jqTbl = $('<table></table>');
                $(this).append($jqTbl);
                $(this).append('<div id="' + _gid+'-pager"></div>');
                $jqTbl.attr('id', _gid);

                _$grid = $jqTbl.jqGrid(_jsdata);
                // добавляем поиск по колонкам
                $jqTbl.jqGrid('filterToolbar',{searchOperators : true});
                // добавляем пагинатор
                $jqTbl.jqGrid('navGrid','#'+_gid+'-pager',{edit:false,add:false,del:false});
            }

            _grids++;
    })(jQuery);
}else{
    alert('themes_mgt/main.js say: jQuery is not loaded');
}