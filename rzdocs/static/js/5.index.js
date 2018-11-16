var font = new FontFaceObserver('nudista-web', {
    weight: 300
});

font.load().then(function () {
    document.documentElement.className += " fonts-loaded";
    console.log('Font is available');
}, function () {
    console.log('Font is not available');
});


var currency_block = $('#currency_block_outer');  
var currency_block_pos = 0;
if(currency_block && currency_block.offset()){
    currency_block_pos = currency_block.offset().top;
}

function change_currency(currency){
  var old_currency = '';
  if(!currency){
    var currency = $('select[name=purchase-currency]').val()
  }   

  if(currency == 'USD'){
    old_currency = "INR";
  }
  else if(currency == 'INR'){
    old_currency = "USD";
  }
  $('[data-product-currency="'+ currency + '"]').removeClass('hide');
  $('[data-product-currency="'+ old_currency + '"]').addClass('hide');
  setCookie('currency', currency);
} 
function setCookie(key, value) {  
    $.cookie(key, value, { path: '/' });
}  
function getCookie(key) {  
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');  
    return keyValue ? keyValue[2] : null;  
}  

$('#menu_toggle').on('click', function(){
    $(this).toggleClass('active');
    $('#menu_outer').toggleClass('active');
    $('body').toggleClass('modal-open');
});

var header_top = $('#header_top');
var PresentScrollPosition = 0;
$(window).on('load', function(){
    fixTopMenu();
});

$( window ).scroll(function() { 
    var currentScroll = $(window).scrollTop(); 
    fixTopMenu();
    if(currency_block && currentScroll >= currency_block_pos){
        currency_block.addClass('fixed');
    } else{
        currency_block.removeClass('fixed');
    }
    // $('#menu_toggle, #menu_outer').removeClass('active')
});

function fixTopMenu(){
    var scrollTop = $(window).scrollTop();
    $('.products-link.active').each(function(){
        $(this).removeClass('active');
    });
    if(scrollTop > 100){
        header_top.addClass('scrolled');
    } else{
        header_top.removeClass('scrolled');
    }
    var CurrentScrollPosition = $(this).scrollTop();
    if ((CurrentScrollPosition > PresentScrollPosition) || (scrollTop <= 0)) {
        header_top.removeClass('fixed-top');
    } else {
        header_top.addClass('fixed-top');
    }
    PresentScrollPosition = CurrentScrollPosition;
}

$('.products-link, .pages-link, .supports-link').on('click', function(){
    $('.products-link.active, .pages-link.active').not(this).each(function(){
        $(this).removeClass('active');
    });
    $(this).toggleClass('active');
});

$('.page-common-outer').on('click', function(e){
    var container = $(".links-list >li");

    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0) 
    {
        $('.supports-link.active, .pages-link.active, .products-link.active').not(this).each(function(){
            $(this).removeClass('active');
        });
    }
    
})
