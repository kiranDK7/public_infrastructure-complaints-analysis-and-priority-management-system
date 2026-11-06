/**
 * SMART CIVICCARE 2.0 - IN-APP REAL-TIME NOTIFICATIONS
 */

function pollUnreadNotifications() {
  const badge = document.getElementById('navNotificationBadge');
  if (!badge) return;

  fetch('/api/notifications/unread-count')
    .then(res => res.json())
    .then(data => {
      if (data.count > 0) {
        badge.innerText = data.count > 9 ? '9+' : data.count;
        badge.classList.remove('d-none');
      } else {
        badge.classList.add('d-none');
      }
    })
    .catch(err => console.debug("Notification poll idle."));
}

document.addEventListener('DOMContentLoaded', function() {
  pollUnreadNotifications();
  // Poll every 30 seconds
  setInterval(pollUnreadNotifications, 30000);
});

