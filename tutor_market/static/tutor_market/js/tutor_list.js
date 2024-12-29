const radio_btns = document.querySelectorAll('.btn-check');
const form = document.querySelector('form');

radio_btns.forEach((btn) => {
    btn.addEventListener('click', () => {
        form.submit();
    });
});