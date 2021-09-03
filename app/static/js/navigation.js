$(function(){
    $('#useLongLabels').click(function(){
        if($(this).prop('disabled')){ return; }
        var attName = ($(this).prop('checked')==true)? 'longl':'shortl';
        $(this).prop('disabled',true);
        $('.searh-data-label').each(function(){
            var val = (attName=='longl')? '&lt;'+$(this).attr(attName)+'&gt;':$(this).attr(attName);
            $(this).html(val);
        });
        $(this).prop('disabled',false).removeProp('disabled');
    });
    $('.predicate-so-list').each(function(){
        if($(this).children().length>$(this).attr('show')){
            var spm = $('<span class="show-more-in-list">Show more</span>'),
            spl = $('<span class="show-less-in-list">Show less</span>'),
            step = parseInt($(this).attr('step')),
            show = parseInt($(this).attr('show')),
            ul=$(this);
            ul.attr('countchilds',ul.find('li').length);
            spl.css({visibility:'hidden'});
            spm.insertAfter(this);
            spl.insertAfter(spm);
            /*****************************************************************/
            function getCount(){ return parseInt(ul.attr('countchilds')); }
            function allVisible(){ return ul.find('li:visible').length===getCount(); }
            function allHidden(){ return ul.find('li:hidden').length===getCount(); }
            function canShowLess(){}
            function canShowMore(){}
            function isMoreVisibleThenShow(){ return ul.find('li:visible').length>show; }
            function isMoreHiddenThenShow(){ return ul.find('li:hidden').length>show; }
            /*****************************************************************/
            spm.click(function(){
                var kx =0,cnt=step;
                for(kx=0;kx<cnt;kx++){
                   $(ul).find('li:visible:last').next('li:hidden').show();
                }
                if(isMoreVisibleThenShow()){
                    spl.css({visibility:'visible'});
                }
                if(allVisible()){
                    spm.css({visibility:'hidden'});
                }
            });
            spl.click(function(){
                var kx =0,cnt=step;
                if(allVisible()){
                    $(ul).find('li:last').hide();
                    cnt--;
                    spm.css({visibility:'visible'});
                }
                // надо проверить если осталось меньше чем 2хshow то надо вычесть разницу из того что осталось от возможного шага
                // то есть если осталось 17 то мы не можем скрыть 10, так как должно остаться столько, значит мы должны скрыть 7
                var isVis = ul.find('li:visible').length;
                if(isVis<(2*show)){
                    cnt = isVis - show;
                }
                for(kx=0;kx<cnt;kx++){
                   $(ul).find('li:hidden:first').prev('li:visible').hide();
                }
                if(!isMoreVisibleThenShow()){
                    spl.css({visibility:'hidden'});
                }
            });
        }
    });
});