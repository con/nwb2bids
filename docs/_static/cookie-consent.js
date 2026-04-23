// Disable Google Analytics until consent
window['ga-disable-G-XXXXXXXXXX'] = true;

// Load the library from CDN
(function() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/gh/orestbida/cookieconsent@v2.9.2/dist/cookieconsent.js';
    script.defer = true;
    script.onload = initCookieConsent;
    document.head.appendChild(script);

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/gh/orestbida/cookieconsent@v2.9.2/dist/cookieconsent.css';
    document.head.appendChild(link);
})();

function initCookieConsent() {
    const cc = initCookieConsent();
    cc.run({
        current_lang: 'en',
        autoclear_cookies: true,
        cookie_name: 'cc_cookie',

        gui_options: {
            consent_modal: {
                layout: 'cloud',
                position: 'bottom center',
                transition: 'slide'
            }
        },

        onAccept: function(cookie) {
            if (cc.allowedCategory('analytics')) {
                // Enable Google Analytics
                window['ga-disable-G-XXXXXXXXXX'] = false;
            }
        },

        onChange: function(cookie, changed_preferences) {
            if (!cc.allowedCategory('analytics')) {
                window['ga-disable-G-XXXXXXXXXX'] = true;
            }
        },

        languages: {
            'en': {
                consent_modal: {
                    title: 'We use cookies!',
                    description: 'This site uses cookies to analyze traffic and improve your experience. <button type="button" data-cc="c-settings" class="cc-link">Manage preferences</button>',
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
                    blocks: [
                        {
                            title: 'Cookie usage',
                            description: 'We use cookies to ensure basic functionality and to enhance your experience.'
                        },
                        {
                            title: 'Strictly necessary cookies',
                            description: 'These cookies are essential.',
                            toggle: {
                                value: 'necessary',
                                enabled: true,
                                readonly: true
                            }
                        },
                        {
                            title: 'Analytics cookies',
                            description: 'These cookies help us understand how visitors interact with our docs.',
                            toggle: {
                                value: 'analytics',
                                enabled: false,
                                readonly: false
                            }
                        }
                    ]
                }
            }
        }
    });
}
