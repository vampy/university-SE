$(document).ready(function () {
    "use strict";
    console.log("main loaded");

    // set datepicker options
    $('.datepicker').datepicker({
        format: 'mm/dd/yyyy'
    });

    // set tooltip options
    $('[data-toggle="tooltip"]').tooltip()
});
