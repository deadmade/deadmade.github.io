// Timeline Toggle Functionality

document.addEventListener('DOMContentLoaded', function() {
  // Alle Timeline-Items mit Toggle-Buttons versehen
  const timelineItems = document.querySelectorAll('.timeline-item');

  timelineItems.forEach(function(item) {
    const header = item.querySelector('.timeline-header');
    const body = item.querySelector('.timeline-body');
    const toggleBtn = item.querySelector('.timeline-toggle');

    if (header && body && toggleBtn) {
      // Initial state: eingeklappt (bereits im HTML gesetzt)
      // body.classList.add('collapsed');
      // toggleBtn.classList.add('collapsed');

      // Toggle Button Click Handler
      toggleBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleTimelineItem(item, body, toggleBtn);
      });

      // Header Click Handler (optional - ganzer Header klickbar)
      header.addEventListener('click', function() {
        toggleTimelineItem(item, body, toggleBtn);
      });

      // Accessibility: Enter/Space Key Support
      header.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleTimelineItem(item, body, toggleBtn);
        }
      });
    }
  });
});

function toggleTimelineItem(item, body, toggleBtn) {
  const isExpanded = body.classList.contains('expanded');

  if (isExpanded) {
    // Collapse
    body.classList.remove('expanded');
    body.classList.add('collapsed');
    toggleBtn.classList.remove('expanded');
    toggleBtn.classList.add('collapsed');
    item.setAttribute('aria-expanded', 'false');
  } else {
    // Expand
    body.classList.remove('collapsed');
    body.classList.add('expanded');
    toggleBtn.classList.remove('collapsed');
    toggleBtn.classList.add('expanded');
    item.setAttribute('aria-expanded', 'true');
  }
}
