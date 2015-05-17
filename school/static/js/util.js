"use strict";

/**
 * Load the content of the url into an element
 *
 * @param {jQuery} $content jQuery object that will contain the page result
 * @param {string} url the url to get
 * @param {object} params containing GET or POST params
 * @param {function} [callback] function that is called after the content was loaded
 * @param {string} [request_type] the type of request, GET or POST, default is GET
 */
function loadContent($content, url, params, callback, request_type) {
    request_type = request_type || "GET";
    callback = callback || function() {};

    // define callback
    function onCompleteCallback(response, status, xhr) {
        if (status === "error") {
            console.error("Error on loadContent");
            console.error(response, status, xhr);
            $content.html("Sorry there was an error " + xhr.status + " " + xhr.statusText);
        } else {
            callback();
        }
    }

    if (request_type === "GET") {
        $content.load(url + "?" + $.param(params), onCompleteCallback);
    } else if (request_type === "POST") {
        $content.load(url, params, onCompleteCallback);
    } else {
        console.error("request_type: ", request_type);
        console.error("request type is invalid")
    }
}

/**
 * Handle event when there is form submit
 *
 * @param {string} form_identifier string representing the form unique identifier, usually id, eg: #main-bugs
 * @param {function} callback_success function that is called on form submit success
 * @param {jQuery} $container a jQuery object representing a parent of the form
 * @param {string} url the url to submit to
 * @param {object} [data_type] additional parameters to add to the request
 * @param {string} [request_method] POST or GET, default is GET
 */
function onFormSubmit(form_identifier, callback_success, $container, url, data_type, request_method) {
    if (!_.isFunction(callback_success)) {
        throw "callback parameter is not a function";
    }

    // make defaults
    request_method = request_method || "POST";
    data_type = data_type || {};

    // unregister previous event handler
    $container.off("submit", form_identifier);

    $container.on("submit", form_identifier, function() {
        // put all values in array
        var data = $(form_identifier).serializeArray();

        // populate with our data type
        $.each(data_type, function(name, value) {
            data.push({name: name, value: value});
        });

        $.ajax({
            type   : request_method,
            url    : url,
            data   : $.param(data),
            success: callback_success,
            error  : function(xhr, ajaxOptions, thrownError) {
                console.error("Error onFormSubmit");
                console.error(xhr, ajaxOptions, thrownError);
            }
        }).fail(function() {
            console.error("onFormSubmit post request failed");
        });

        return false;
    });
}

/**
 * Alias for getElementById
 *
 * @param {string} id the element id
 *
 * @return {Element} html element
 */
function getByID(id) {
    return document.getElementById(id);
}

/**
 * Parse a json string
 *
 * @param {string} raw_string the json string
 *
 * @return {object} the parsed json data, or empty object if there was an error, and message written to the console
 */
function parseJSON(raw_string) {
    var jData = {}; // silently fail on the client side

    try {
        jData = JSON.parse(raw_string);
    } catch (e) {
        console.error("Parson JSON error: ", e);
        console.error("Raw string: ", raw_string);
    }

    return jData;
}

/**
 * Redirect the current page with delay
 *
 * @param {string} url the destination
 * @param {float|int} [seconds] delay in redirection, default is 0
 */
function redirectTo(url, seconds) {
    seconds = seconds || 0;

    var timeout = setTimeout(function() {
        window.location = url;
        clearTimeout(timeout);
    }, seconds * 1000);
}

/**
 * Refresh the current page
 */
function refreshPage() {
    redirectTo(window.location.href, 0);
}

/**
 * Read a page's GET URL variables and return them as an hash map
 *
 * @param {string} [url] default is the current page
 *
 * @return {object} hash map of all vars
 */
function getUrlVars(url) {
    url = url || window.location.href;

    var vars = {}, hash, slice_start = url.indexOf('?');

    // url does not have any GET params
    if (slice_start === -1) {
        return vars;
    }

    var hashes = url.slice(slice_start + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars[hash[0]] = hash[1];
    }

    return vars;
}

// Extend string. Eg "{0} is {1}".format("JS", "nice") will output "JS is nice"
if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/\{\{|\}\}|\{(\d+)\}/g, function(curlyBrack, index) {
            return ((curlyBrack == "{{") ? "{" : ((curlyBrack == "}}") ? "}" : args[index]));
        });
    };
}
