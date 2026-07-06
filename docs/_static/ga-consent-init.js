// Google Consent Mode v2 — deny until user opts-in
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}

// vanilla-cookieconsent persists choices in the 'cc_cookie' cookie; read it
// here (before gtag loads) so returning visitors who already accepted
// analytics are tracked from the very first hit of the page load.
function nwb2bidsHasAnalyticsConsent() {
    try {
        var match = document.cookie.match(/(?:^|;\s*)cc_cookie=([^;]*)/);
        if (!match) return false;
        var consent = JSON.parse(decodeURIComponent(match[1]));
        return Array.isArray(consent.categories) && consent.categories.indexOf('analytics') !== -1;
    } catch (error) {
        return false;
    }
}

var nwb2bidsAnalyticsGranted = nwb2bidsHasAnalyticsConsent();

gtag('consent', 'default', {
    'analytics_storage': nwb2bidsAnalyticsGranted ? 'granted' : 'denied',
    'ad_storage': 'denied',
    'wait_for_update': 500
});

// Disable GA until consent given. gtag fires its page_view while this flag is
// set, so cookie-consent.js re-sends it after a first-time accept (tracked
// via the flag below).
window['ga-disable-G-KS7XCX3H2L'] = !nwb2bidsAnalyticsGranted;
window['nwb2bids-ga-pageview-suppressed'] = !nwb2bidsAnalyticsGranted;
