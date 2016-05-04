/*jslint browser: true */
/*global window,define */


(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define("deeplink", factory(root));
    } else if (typeof exports === 'object') {
        module.exports = factory(root);
    } else {
        root.deeplink = factory(root);
    }
})(window || this, function (root) {

    "use strict";

    /**
     * Cannot run without DOM or user-agent
     */
    if (!root.document || !root.navigator) {
        return;
    }

    /**
     * Set up scope variables and settings
     */
    var timeout;
    var settings = {};
    var defaults = {
        iOS: {},
        android: {},
        delta: 500
    };

    /**
     * Merge defaults with user options
     * @private
     * @param {Object} defaults Default settings
     * @param {Object} options User options
     * @returns {Object} Merged values of defaults and options
     */
    var extend = function (defaults, options) {
        var extended = {};
        Object.keys(defaults).forEach(function (key) {
            extended[key] = defaults[key];
        });
        Object.keys(options).forEach(function (key) {
            extended[key] = options[key];
        });
        return extended;
    };

    /**
     * Check if the user-agent is Android
     *
     * @private
     * @returns {Boolean} true/false
     */
    var isAndroid = function () {
        return navigator.userAgent.match('Android');
    };

    /**
     * Check if the user-agent is iPad/iPhone/iPod
     *
     * @private
     * @returns {Boolean} true/false
     */
    var isIOS = function () {
        return navigator.userAgent.match('iPad') ||
            navigator.userAgent.match('iPhone') ||
            navigator.userAgent.match('iPod');
    };

    /**
     * Check if the user-agent is Windows Phone/Lumia
     *
     * @private
     * @returns {Boolean} true/false
     */
    var isWindows = function () {
        return navigator.userAgent.match('Windows\sPhone') ||
            navigator.userAgent.match('Lumia');
    };

    /**
     * Check if the user is on mobile
     *
     * @private
     * @returns {Boolean} true/false
     */
    var isMobile = function () {
        return isAndroid() || isIOS() || isWindows();
    };

    /**
     * Timeout function that tries to open the app store link.
     * The time delta comparison is to prevent the app store
     * link from opening at a later point in time. E.g. if the
     * user has your app installed, opens it, and then returns
     * to their browser later on.
     *
     * @private
     * @param {Integer} Timestamp when trying to open deeplink
     * @returns {Function} Function to be executed by setTimeout
     */
    var openAppStore = function (ts) {
        return function () {
            var link = settings[settings.platform].storeUrl;
            var wait = settings.delay + settings.delta;
            if (typeof link === "string" && (Date.now() - ts) < wait) {
                window.location = link;
            }
        };
    };

    /**
     * The setup() function needs to be run before deeplinking can work,
     * as you have to provide the iOS and/or Android settings for your app.
     *
     * @public
     * @param {object} setup options
     */
    var setup = function (options) {
        settings = extend(defaults, options);
        if (isAndroid()) {
            settings.platform = "android";
        }
        if (isIOS()) {
            settings.platform = "iOS";
            document.getElementById("store").innerText = "Visit Appstore";
        }
        if (isWindows()) {
            settings.platform = "windows";
            document.getElementById("store").innerText = "Visit Store";
        }
        if (isMobile() && settings.hasOwnProperty(settings.platform)) {
            document.getElementById("store").href = settings[settings.platform].storeUrl;
            document.getElementById("openapp").href = settings[settings.platform].deeplink;
        }
    };

    /**
     * Tries to open your app URI through a hidden iframe.
     *
     * @public
     * @param {String} Deeplink URI
     * @return {Boolean} true, if you're on a mobile device and the link was opened
     */
    var open = function (default_url) {
        if (!isMobile()) {
            if (default_url.length) {
                window.location.href = default_url;
            }
            document.getElementById("container").style.display = "none";
            return;
        }
        if (settings.delay <= 1000) {
            openAppStore(Date.now())();
            document.getElementById('openapp').style.display = "none";
            return;
        }
        document.getElementById("openapp").click();
        if (!settings[settings.platform].deeplink.length) {
             openAppStore(Date.now())();
             return;
        }
        timeout = setTimeout(openAppStore(Date.now()), settings.delay);
        var iframe = document.createElement("iframe");
        iframe.onload = function () {
            clearTimeout(timeout);
            iframe.parentNode.removeChild(iframe);
            window.location.href = settings[settings.platform].deeplink;
        };
        iframe.src = settings[settings.platform].deeplink;
        iframe.setAttribute("style", "display:none;");
        document.body.appendChild(iframe);
    };

    // Public API
    return {
        setup: setup,
        open: open
    };

});
