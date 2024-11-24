function printPage() {
    window.print();
  }

function updateNotificationDot() {
    const notificationList = document.getElementById('notification-list');
    const notificationDot = document.querySelector('.notification-dot');
    if (notificationList.children.length > 0) {
        notificationDot.classList.add('active'); // Show the red dot
    } else {
        notificationDot.classList.remove('active'); // Hide the red dot
    }
}

function addNotification(text) {
    const notificationList = document.getElementById('notification-list');
    const listItem = document.createElement('li');
    listItem.textContent = text;
    notificationList.appendChild(listItem);
    updateNotificationDot();
}

document.getElementById('clear-notifications').addEventListener('click', () => {
    const notificationList = document.getElementById('notification-list');
    notificationList.innerHTML = '';
    updateNotificationDot();
});


updateNotificationDot();
