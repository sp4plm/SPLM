if(typeof void null!=typeof jQuery){
    (function($){
        function startverify(){
            var url, localvar;
            localvar = window.location.pathname.replace("/datanav","");
            url="/datanav/getver";
            url+=localvar+window.location.search;
            $(this).button( "disable" );
            $.get(url,null,function(answer){
                if (typeof void null !== answer){
                    $(answer).insertAfter("#ver-mark");
                }
            },"html");
        }
        $('#startverifybutton').on('click',startverify);
        function startrules(){
            var url, localvar;
            localvar = window.location.pathname.replace("/datanav","");
            url="/datanav/rules";
            url+=localvar+window.location.search;
            $(this).button( "disable" );
            $.get(url,null,function(answer){
                if (typeof void null !== answer){
                    $(answer).insertAfter("#rule-mark");
                }
            },"html");
        }
        $('#startrulesbutton').on('click',startrules);
        $("input[type='button']").button();
    })(jQuery);
}else{
    alert('datanavigation.js say: jQuery is not loaded');
}