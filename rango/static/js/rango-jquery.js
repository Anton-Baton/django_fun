$(document).ready(function(){
    $('#about-btn').addClass('btn btn-warning').click(function(event){
        alert('JQ click')
    });
    $("p").hover( function() {
            $(this).css('color', 'red');
    },
    function() {
            $(this).css('color', 'blue');
    });
});