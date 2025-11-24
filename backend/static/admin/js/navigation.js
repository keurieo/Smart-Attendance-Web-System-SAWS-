/**
 * Navigation JavaScript
 * Handles sidebar toggle, mobile menu, and user dropdown
 */

(function() {
  'use strict';

  // Wait for DOM to be ready
  document.addEventListener('DOMContentLoaded', function() {
    initSidebarToggle();
    initUserMenu();
    initMobileBackdrop();
    initSearchFocus();
  });

  /**
   * Initialize sidebar toggle functionality
   */
  function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('adminSidebar');
    const backdrop = document.getElementById('mobileBackdrop');

    if (!sidebarToggle || !sidebar) return;

    // Toggle sidebar on button click
    sidebarToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      toggleSidebar();
    });

    // Close sidebar when clicking backdrop
    if (backdrop) {
      backdrop.addEventListener('click', function() {
        closeSidebar();
      });
    }

    // Close sidebar on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && sidebar.classList.contains('active')) {
        closeSidebar();
      }
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function() {
        // Close sidebar on desktop
        if (window.innerWidth >= 1024) {
          closeSidebar();
        }
      }, 250);
    });
  }

  /**
   * Toggle sidebar open/closed
   */
  function toggleSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const backdrop = document.getElementById('mobileBackdrop');
    const toggle = document.getElementById('sidebarToggle');

    if (!sidebar) return;

    const isActive = sidebar.classList.toggle('active');
    
    if (backdrop) {
      backdrop.classList.toggle('active', isActive);
    }
    
    if (toggle) {
      toggle.classList.toggle('active', isActive);
      toggle.setAttribute('aria-expanded', isActive);
    }

    // Prevent body scroll when sidebar is open on mobile
    if (window.innerWidth < 1024) {
      document.body.style.overflow = isActive ? 'hidden' : '';
    }
  }

  /**
   * Close sidebar
   */
  function closeSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const backdrop = document.getElementById('mobileBackdrop');
    const toggle = document.getElementById('sidebarToggle');

    if (!sidebar) return;

    sidebar.classList.remove('active');
    
    if (backdrop) {
      backdrop.classList.remove('active');
    }
    
    if (toggle) {
      toggle.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
    }

    // Restore body scroll
    document.body.style.overflow = '';
  }

  /**
   * Initialize user menu dropdown
   */
  function initUserMenu() {
    const userMenu = document.getElementById('userMenu');
    if (!userMenu) return;

    const trigger = userMenu.querySelector('.user-menu__trigger');
    if (!trigger) return;

    // Toggle dropdown on click
    trigger.addEventListener('click', function(e) {
      e.stopPropagation();
      userMenu.classList.toggle('active');
      
      const isExpanded = userMenu.classList.contains('active');
      trigger.setAttribute('aria-expanded', isExpanded);
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!userMenu.contains(e.target)) {
        userMenu.classList.remove('active');
        trigger.setAttribute('aria-expanded', 'false');
      }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && userMenu.classList.contains('active')) {
        userMenu.classList.remove('active');
        trigger.setAttribute('aria-expanded', 'false');
        trigger.focus();
      }
    });

    // Handle keyboard navigation in dropdown
    const dropdownItems = userMenu.querySelectorAll('.dropdown-item');
    if (dropdownItems.length > 0) {
      dropdownItems.forEach(function(item, index) {
        item.addEventListener('keydown', function(e) {
          if (e.key === 'ArrowDown') {
            e.preventDefault();
            const nextItem = dropdownItems[index + 1] || dropdownItems[0];
            nextItem.focus();
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const prevItem = dropdownItems[index - 1] || dropdownItems[dropdownItems.length - 1];
            prevItem.focus();
          }
        });
      });
    }
  }

  /**
   * Initialize mobile backdrop
   */
  function initMobileBackdrop() {
    const backdrop = document.getElementById('mobileBackdrop');
    if (!backdrop) return;

    // Prevent clicks from propagating
    backdrop.addEventListener('click', function(e) {
      e.stopPropagation();
    });
  }

  /**
   * Initialize search input focus behavior
   */
  function initSearchFocus() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;

    // Add keyboard shortcut (Ctrl/Cmd + K) to focus search
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
      }
    });

    // Clear search on escape
    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        searchInput.value = '';
        searchInput.blur();
      }
    });
  }

  /**
   * Highlight active navigation item based on current URL
   */
  function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(function(link) {
      const linkPath = link.getAttribute('href');
      const navItem = link.closest('.nav-item');

      if (!navItem) return;

      // Remove active class from all items first
      navItem.classList.remove('nav-item--active');

      // Add active class if paths match
      if (linkPath && currentPath.includes(linkPath) && linkPath !== '/admin/') {
        navItem.classList.add('nav-item--active');
      } else if (linkPath === '/admin/' && currentPath === '/admin/') {
        navItem.classList.add('nav-item--active');
      }
    });
  }

  // Call on page load
  highlightActiveNav();

  /**
   * Add smooth scroll behavior for anchor links
   */
  function initSmoothScroll() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(function(link) {
      link.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href').substring(1);
        if (!targetId) return;

        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  initSmoothScroll();

  /**
   * Handle notification badge updates (placeholder for future implementation)
   */
  function updateNotificationBadge(count) {
    const badge = document.querySelector('.header-action .badge');
    if (!badge) return;

    if (count > 0) {
      badge.textContent = count > 99 ? '99+' : count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  // Expose functions to global scope if needed
  window.AdminNavigation = {
    toggleSidebar: toggleSidebar,
    closeSidebar: closeSidebar,
    updateNotificationBadge: updateNotificationBadge,
    highlightActiveNav: highlightActiveNav
  };

})();
