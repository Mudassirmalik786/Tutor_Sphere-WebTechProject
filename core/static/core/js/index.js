$(document).ready(function () {

    // Make the value submit button visible only when a value is selected
    const submitButton = $('#values-submit-btn');
    const input = $('input[type="radio"]');
    input.change(function () {
        submitButton.addClass('value-btn-visible');
        submitButton.removeClass('value-btn-hidden');
    });

    // Transparent navbar when at the top of the page
    $('.navbar').removeClass('bg-body-tertiary');
    $('.navbar-container').removeClass('bg-body-tertiary');
    $(window).scroll(function () {
        if ($(this).scrollTop() == 0) {
            $('.navbar').removeClass('bg-body-tertiary');
            $('.navbar-container').removeClass('bg-body-tertiary');
        } else {
            $('.navbar').addClass('bg-body-tertiary');
            $('.navbar-container').addClass('bg-body-tertiary');
        }
    });

    // -> Credit for the aria-expanded attribute check: https://getbootstrap.com/docs/5.3/components/navbar/#scrolling
    $('.navbar-toggler').click(function () {
        if ($(this).attr('aria-expanded') === 'true') {
            $('.navbar').addClass('bg-body-tertiary');
            $('.navbar-container').addClass('bg-body-tertiary');
        } else {
            if ($(window).scrollTop() === 0) {
                $('.navbar').removeClass('bg-body-tertiary');
                $('.navbar').removeClass('bg-body-tertiary');
            }
        }
    });
});