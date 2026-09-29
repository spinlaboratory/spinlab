// Open all external links in a new browser tab.
// "noopener noreferrer" prevents the new tab from accessing window.opener
// and avoids leaking the referrer URL to third-party sites.
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("a[href]").forEach(function (link) {
        var href = link.getAttribute("href");
        if (href && (href.startsWith("http://") || href.startsWith("https://"))) {
            link.setAttribute("target", "_blank");
            link.setAttribute("rel", "noopener noreferrer");
        }
    });
});
