/**
 * Updates the copyright notice on the webpage.
 */
function updateCopyrightNotice() {
    let getYear = new Date().getFullYear();
    let yearID = document.getElementById('year');
    if (getYear == 2024) {
        yearID.innerHTML = getYear;
    } else {
        yearID.innerHTML = `2024 - ${getYear}`;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(function(toastElement) {
        var toast = new bootstrap.Toast(toastElement);
        toast.show();
    });

    updateCopyrightNotice();
});

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

if (typeof module !== "undefined") module.exports = {
    updateCopyrightNotice
};