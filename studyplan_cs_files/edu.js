
/*
 * Mark top navigation bar with current navSection
 */
function markTopNav(navSection) {
    if (navSection) {
        jQuery(document).ready(function () {
            jQuery('#'+navSection).addClass('current open');
            jQuery('#'+navSection).parents('li').addClass('inpath open');
        });
    }
}

function fixBreadCrumbs() {
    jQuery(document).ready(function () {
        jQuery('#breadcrumbs li:last').addClass('last')
    });
}

/*
 * Google Analytics
 */
function googleAnalytics() {
    ga('create', 'UA-42643897-1', 'auto');
    ga('set', 'anonymizeIp', true);
    ga('send', 'pageview');
}


