// ==========================================================================
// Cookie Consent for Read the Docs
// Blocks Google Analytics until the user consents.
// ==========================================================================

// --- STEP 1: Disable Google Analytics BEFORE it loads ---------------------
// This must run as early as possible. RTD injects GA automatically,
// and this flag tells GA not to send any data.
window['ga-disable-G-XXXXXXXXXX'] = true;

// --- STEP 2: Load the cookie consent library -----------------------------
(function () {
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = 'https://cdn.jsdelivr.net/gh/orestbida/cookieconsent@v2.9.2/dist/cookieconsent.css';
    document.head.appendChild(cssLink);

    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/gh/orestbida/cookieconsent@v2.9.2/dist/cookieconsent.js';
    script.defer = true;
    script.onload = initConsent;
    document.head.appendChild(script);
})();

// --- STEP 3: Initialize the consent modal --------------------------------
function initConsent() {
    const cc = initCookieConsent();

    cc.run({
        current_lang: 'en',
        autoclear_cookies: true,
        page_scripts: true,
        cookie_name: 'cc_cookie',
        cookie_expiration: 182, // days

        // Fired after consent is stored (first time or after update)
        onAccept: function (cookie) {
            if (cc.allowedCategory('analytics')) {
                enableAnalytics();
            } else {
                disableAnalytics();
            }
        },

        // Fired when the user changes preferences
        onChange: function (cookie, changed_preferences) {
            if (cc.allowedCategory('analytics')) {
                enableAnalytics();
            } else {
                disableAnalytics();
                clearGACookies();
            }
        },

        languages: {
            en: {
                consent_modal: {
                    title: 'We use cookies 🍪',
                    description:
                        'This documentation site uses cookies to analyze traffic and improve your experience. ' +
                        'You can accept all cookies, reject non-essential ones, or manage your preferences. ' +
                        '<button type="button" data-cc="c-settings" class="cc-link">Manage preferences</button>',
                    primary_btn: {
                        text: 'Accept all',
                        role: 'accept_all'
                    },
                    secondary_btn: {
                        text: 'Reject all',
                        role: 'accept_necessary'
                    }
                },
                settings_modal: {
                    title: 'Cookie preferences',
                    save_settings_btn: 'Save settings',
                    accept_all_btn: 'Accept all',
                    reject_all_btn: 'Reject all',
                    close_btn_label: 'Close',
                    cookie_table_headers: [
                        { col1: 'Name' },
                        { col2: 'Domain' },
                        { col3: 'Expiration' },
                        { col4: 'Description' }
                    ],
                    blocks: [
                        {
                            title: 'Cookie usage 📢',
                            description:
                                'We use cookies to ensure the basic functionality of this site and to enhance your experience. ' +
                                'You can choose to opt in or opt out of each category at any time.'
                        },
                        {
                            title: 'Strictly necessary cookies',
                            description:
                                'These cookies are essential for the proper functioning of the site. Without them, the site would not work correctly.',
                            toggle: {
                                value: 'necessary',
                                enabled: true,
                                readonly: true
                            }
                        },
                        {
                            title: 'Analytics cookies',
                            description:
                                'These cookies (Google Analytics) help us understand how visitors interact with the documentation so we can improve it.',
                            toggle: {
                                value: 'analytics',
                                enabled: false,
                                readonly: false
                            },
                            cookie_table: [
                                {
                                    col1: '^_ga',
                                    col2: 'google.com',
                                    col3: '2 years',
                                    col4: 'Google Analytics tracking cookie.',
                                    is_regex: true
                                },
                                {
                                    col1: '_gid',
                                    col2: 'google.com',
                                    col3: '1 day',
                                    col4: 'Google Analytics tracking cookie.'
                                }
                            ]
                        },
                        {
                            title: 'More information',
                            description:
                                'For any questions about our cookie policy, please <a class="cc-link" href="mailto:you@example.com">contact us</a>.'
                        }
                    ]
                }
            }
        }
    });
}

// --- STEP 4: Helper functions --------------------------------------------
function enableAnalytics() {
    window['ga-disable-G-XXXXXXXXXX'] = false;
    // If GA is already loaded but was disabled, send a pageview now
    if (typeof gtag === 'function') {
        gtag('event', 'page_view');
    }
}

function disableAnalytics() {
    window['ga-disable-G-XXXXXXXXXX'] = true;
}

function clearGACookies() {
    // Remove GA cookies when consent is withdrawn
    const gaCookies = ['_ga', '_gid', '_gat'];
    const domain = window.location.hostname.replace(/^www\./, '');

    document.cookie.split(';').forEach(function (c) {
        const name = c.split('=')[0].trim();
        if (name.startsWith('_ga') || gaCookies.includes(name)) {
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.${domain}`;
            document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
        }
    });
}
