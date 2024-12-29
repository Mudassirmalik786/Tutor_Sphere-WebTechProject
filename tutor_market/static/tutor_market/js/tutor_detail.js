/**
 * Checks if the given event is a Calendly event.
 * @param {Event} e - The event object.
 * @returns {boolean} - Returns true if the event is a Calendly event, otherwise false.
 */
function isCalendlyEvent(e) {
    return e.data.event && e.data.event.indexOf('calendly') === 0;
}

// -> Credit for posting a form using javascript: https://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
window.addEventListener('message', function (e) {
    if (isCalendlyEvent(e) && e.data.event === 'calendly.event_scheduled') {
        const eventUri = e.data.payload.event.uri;
        const inviteeUri = e.data.payload.invitee.uri;
        const form = document.getElementById('calendly_form_hidden');

        // -> Credit for submitting a form and setting values: https://www.w3schools.com/jsref/dom_obj_form.asp
        // Use form.elements to directly access the inputs by name
        form.elements.event_uri.value = eventUri;
        form.elements.invitee_uri.value = inviteeUri;

        // Submit the form
        form.submit();
    }
});

$('document').ready(function () {
    const tutorDetailData = JSON.parse(document.getElementById('tutor-detail-data').textContent);
    const calendlyEventUrl = tutorDetailData.calendly_event_url;
    const user = tutorDetailData.user;
    const email = tutorDetailData.email;

    const calendlyDiv = document.getElementById('calendly');

    if (!calendlyDiv) {
        return;
    }

    Calendly.initInlineWidget({
        url: `${calendlyEventUrl}?hide_event_type_details=1`,
        parentElement: calendlyDiv,
        prefill: {
            name: user,
            email: email,
        },
        utm: {},
        resize: true,
    });
});