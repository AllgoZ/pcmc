(function () {
    function init() {
        var btn = document.getElementById('hamburgerBtn');
        var nav = document.getElementById('navMenu');
        var overlay = document.getElementById('navOverlay');
        var closeBtn = document.getElementById('navCloseBtn');

        if (!btn || !nav) {
            return;
        }

        function openNav() {
            nav.classList.add('nav-open');
            btn.classList.add('is-active');
            btn.setAttribute('aria-expanded', 'true');
            if (overlay) {
                overlay.classList.add('nav-overlay-open');
            }
            document.body.style.overflow = 'hidden';
        }

        function closeNav() {
            nav.classList.remove('nav-open');
            btn.classList.remove('is-active');
            btn.setAttribute('aria-expanded', 'false');
            if (overlay) {
                overlay.classList.remove('nav-overlay-open');
            }
            document.body.style.overflow = '';
        }

        function toggleNav() {
            if (nav.classList.contains('nav-open')) {
                closeNav();
            } else {
                openNav();
            }
        }

        btn.addEventListener('click', function (event) {
            event.stopPropagation();
            toggleNav();
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', function (event) {
                event.stopPropagation();
                closeNav();
            });
        }

        if (overlay) {
            overlay.addEventListener('click', closeNav);
        }

        nav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', closeNav);
        });

        document.addEventListener('click', function (event) {
            if (nav.classList.contains('nav-open') && !nav.contains(event.target) && !btn.contains(event.target)) {
                closeNav();
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                closeNav();
            }
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 991) {
                closeNav();
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
