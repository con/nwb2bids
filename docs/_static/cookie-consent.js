// Using vanilla-cookieconsent v3 (free, GDPR-compliant)
document.addEventListener('DOMContentLoaded', function () {
    CookieConsent.run({
        guiOptions: {
            consentModal: { layout: 'box', position: 'bottom right' },
            preferencesModal: { layout: 'box' }
        },
        categories: {
            necessary: { enabled: true, readOnly: true },
            analytics: {
                enabled: false,
                autoClear: {
                    cookies: [
                        { name: /^_ga/ },
                        { name: '_gid' }
                    ]
                },
                services: {
                    ga4: {
                        label: 'Google Analytics 4',
                        onAccept: () => {
                            // Enable GA tracking
                            window[`ga-disable-G-KS7XCX3H2L`] = false;
                            if (typeof gtag === 'function') {
                                gtag('consent', 'update', {
                                    analytics_storage: 'granted'
                                });
                            }
                        },
                        onReject: () => {
                            window[`ga-disable-G-KS7XCX3H2L`] = true;
                        }
                    }
                }
            }
        },
        language: {
            default: 'en',
            translations: {
                en: {
                    consentModal: {
                        title: 'We use cookies',
                        description: 'This documentation uses Google Analytics to understand usage. You can accept or reject analytics cookies.',
                        acceptAllBtn: 'Accept all',
                        acceptNecessaryBtn: 'Reject all',
                        showPreferencesBtn: 'Manage preferences'
                    },
                    preferencesModal: {
                        title: 'Cookie preferences',
                        acceptAllBtn: 'Accept all',
                        acceptNecessaryBtn: 'Reject all',
                        savePreferencesBtn: 'Save preferences',
                        closeIconLabel: 'Close',
                        sections: [
                            {
                                title: 'Strictly necessary',
                                description: 'Required for the site to function.',
                                linkedCategory: 'necessary'
                            },
                            {
                                title: 'Analytics',
                                description: 'Helps us understand how the docs are used.',
                                linkedCategory: 'analytics'
                            }
                        ]
                    }
                }
            }
        }
    });
});
