/// On Page Load
window.onload = function () {
    const today = new Date();
    const year = today.getFullYear();
    const startOfYear = new Date(year, 0, 1);
    const days = Math.floor((today - startOfYear) / (24 * 60 * 60 * 1000));
    const weekNumber = Math.ceil((days + 1) / 7);

    // Format the value in YYYY-Www format
    const formattedWeek = `${year}-W${weekNumber.toString().padStart(2, '0')}`;

    // Set the value of the input field to the current week
    document.getElementById('unavailabilityDate').value = formattedWeek;
    loadUnavailability();
    loadNotifications()
};

function printPage() {
    window.print();
}

/// Notifications
function loadNotifications() {
    fetch('/get_notifications', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            const notifications = data.notifications;
            const notificationList = document.getElementById('notification-list');
            notificationList.innerHTML = ''; // Clear existing notifications
            if (notifications.length == 0) {
                // Display a message when no notifications are available
                const noNotifications = document.createElement('li');
                noNotifications.textContent = "Nothing to see here...";
                noNotifications.classList.add('text-muted', 'text-center', 'py-2');
                notificationList.appendChild(noNotifications);
            } else {
                notifications.forEach(notification => {
                    addNotification(notification.message, notification.hasRead, notification.sendTime);
                    updateNotificationDot();
                });
            }
        })
        .catch(error => console.error("Error loading notifications:", error));
}

function addNotification(text, hasRead = false, timestamp = null) {
    const notificationList = document.getElementById('notification-list');

    const listItem = document.createElement('li');
    listItem.classList.add('d-flex', 'align-items-start', 'align-items-center', 'gap-2', 'py-2', 'border-bottom');

    if (!hasRead) {
        listItem.classList.add('unread'); // Add the 'unread' class for unread notifications
    }

    const icon = document.createElement('i');
    icon.classList.add('m-2', 'bi', hasRead ? 'bi-envelope-open' : 'bi-envelope-fill');
    icon.style.color = '#6F4E37';
    listItem.appendChild(icon);

    const content = document.createElement('div');
    content.classList.add('d-flex', 'flex-column', 'w-100', 'small');

    const message = document.createElement('span');
    message.textContent = text;
    message.classList.add('text-wrap', 'text-truncate');
    if (!hasRead) {
        message.classList.add('fw-bold'); // Bold for unread notifications
    }
    content.appendChild(message);

    if (timestamp) {
        const time = document.createElement('span');
        time.textContent = new Date(timestamp).toLocaleString();
        time.classList.add('text-muted', 'mt-1', 'timestamp');
        content.appendChild(time);
    }

    listItem.appendChild(content);
    notificationList.appendChild(listItem);

    updateNotificationDot();
}

function clearNotifications() {
    fetch('/clear_notifications', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const notificationList = document.getElementById('notification-list');
                notificationList.innerHTML = ''; // Clear notifications from the UI
                console.log(data.message); // Log success message
            } else {
                console.error("Error clearing notifications:", data.error);
            }
        })
        .catch(error => console.error("Error clearing notifications:", error));
}

// Mark notifications as read
document.getElementById('notificationsDropdown').addEventListener('show.bs.dropdown', function () {
    fetch('/mark_notifications_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(data.message);

                // Remove 'unread' class from all notifications in the dropdown
                const unreadItems = document.querySelectorAll('#notification-list .unread');
                unreadItems.forEach(item => item.classList.remove('unread'));
                updateNotificationDot();
            } else {
                console.error("Error marking notifications as read:", data.error);
            }
        })
        .catch(error => console.error("Error marking notifications as read:", error));
});

// Change envelope icons to "open" and unbold text after the dropdown is closed
document.getElementById('notificationsDropdown').addEventListener('hide.bs.dropdown', function () {
    // Change the envelope icons to "open"
    const envelopeIcons = document.querySelectorAll('#notification-list .bi-envelope-fill');
    envelopeIcons.forEach(icon => {
        icon.classList.remove('bi-envelope-fill');
        icon.classList.add('bi-envelope-open'); // Change icon to "open"
    });

    // Remove the bold style from the message text (unbold unread notifications)
    const boldNotifications = document.querySelectorAll('#notification-list .fw-bold');
    boldNotifications.forEach(notification => {
        const message = notification;
        if (message) {
            message.classList.remove('fw-bold'); // Remove the bold style
        }
    });
});


function updateNotificationDot() {
    const notificationDot = document.querySelector('.notification-dot');
    const unreadNotifications = document.querySelectorAll('#notification-list .unread'); // Select unread notifications
    if (unreadNotifications.length > 0) {
        notificationDot.classList.add('active'); // Show the red dot
    } else {
        notificationDot.classList.remove('active'); // Hide the red dot
    }
}

function closeModal() {
    document.querySelector('button.btn-close').click();
}

function loadUnavailability() {
    const unavailabilityDate = document.getElementById('unavailabilityDate').value;
    if (!unavailabilityDate) {
        console.log("No unavailability date selected.");
        return; // Don't proceed if no date is selected
    }
    fetch('/get_unavailability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ unavailabilityDate })
    })
        .then(response => response.json())
        .then(data => {
            unavailabilitySlots = data.unavailability;
            if (unavailabilitySlots.length == 0) {
                // Display a message when there is no unavailability
                const list = document.getElementById("unavailabilityList");
                list.innerHTML = '';
                const noUnavailability = document.createElement('p');
                noUnavailability.id = 'no-availability-message';
                noUnavailability.textContent = "Nothing to see here...";
                noUnavailability.classList.add('text-muted', 'text-center', 'py-2');
                list.appendChild(noUnavailability);
            } else {
                updateUnavailabilityList(unavailabilitySlots);
            }
            updateUnavailabilityGrid(unavailabilitySlots);
        })
        .catch(error => console.error("Error loading availability:", error));
}

function addUnavailability() {
    const selectedDate = document.getElementById('unavailability-date').value;
    const startHour = document.getElementById('unavailability-start-hour').value;
    const endHour = document.getElementById('unavailability-end-hour').value;

    // Ensure that the required fields are filled
    if (!selectedDate || !startHour || !endHour) {
        alert("Please fill out all fields.");
        return;
    }

    // Create a new Date object for the start and end date-time
    const startDatetime = new Date(selectedDate);
    const endDatetime = new Date(selectedDate);
    startDatetime.setUTCHours(startHour, 0, 0, 0);
    endDatetime.setUTCHours(endHour, 0, 0, 0);

    // Validation: Ensure start time is before end time and not equal
    if (startDatetime >= endDatetime) {
        alert("Start time must be before end time.");
        return;
    }

    // Convert to ISO format w/o timezone info
    const startIso = startDatetime.toISOString().slice(0, -1);
    const endIso = endDatetime.toISOString().slice(0, -1);

    fetch('/add_unavailability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            unavailableStartTime: startIso,
            unavailableEndTime: endIso,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUnavailability();
                closeModal();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
}

function deleteUnavailability(unavailabilityID) {
    fetch('/delete_unavailability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            unavailabilityID: unavailabilityID,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUnavailability();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
}

function clearUnavailability() {
    const unavailabilityDate = document.getElementById('unavailabilityDate').value;
    if (!unavailabilityDate) {
        console.log("No unavailability date selected.");
        return; // Don't proceed if no date is selected
    }
    // Send the request to the server
    fetch('/clear_unavailability', {
        method: 'POST',
        body: new URLSearchParams({ unavailabilityDate }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUnavailability();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while clearing unavailability');
        });
}

function autofillUnavailability() {
    const unavailabilityDate = document.getElementById('unavailabilityDate').value;
    if (!unavailabilityDate) {
        console.log("No unavailability date selected.");
        return; // Don't proceed if no date is selected
    }
    // Send the request to the server
    fetch('/autofill_unavailability', {
        method: 'POST',
        body: new URLSearchParams({ unavailabilityDate }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUnavailability();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while clearing unavailability');
        });
}

function updateUnavailabilityGrid(unavailabilitySlots) {
    // Clear all cells to default styles
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.style.background = 'white'
        cell.style.color = 'white'
        cell.innerHTML = '';
    });

    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    unavailabilitySlots.forEach(slot => {
        const startDate = new Date(slot.start);
        const endDate = new Date(slot.end);

        // Extract the day, start hour, and end hour
        const day = dayNames[startDate.getDay()];
        const startHour = startDate.getHours();
        const endHour = endDate.getHours();

        // Iterate over the hours in the shift and update the grid
        for (let hour = startHour; hour < endHour; hour++) {
            if (hour >= 7 && hour <= 18) {
                const cellId = `cell-${day}-${hour}`;
                const cell = document.getElementById(cellId);
                if (cell) {                
                    cell.style.background = 'linear-gradient(135deg, #7A5E47, #6F4E37)';
                    cell.style.textAlign = 'center';
                    cell.style.display = 'flex';
                    cell.style.alignItems = 'center';
                    cell.style.justifyContent = 'center';
                    
                    // Add time range as styled content
                    cell.innerHTML = `
                        <div style="text-align: center; font-size: 12px;">
                            <span style="font-weight: bold;">${formatTime(startDate)}</span>
                            <br />
                            <span>to</span>
                            <br />
                            <span style="font-weight: bold;">${formatTime(endDate)}</span>
                        </div>
                    `;

                    // Optionally add a tooltip for detailed information
                    cell.setAttribute('title', `Unavailable from ${formatTime(startDate)} to ${formatTime(endDate)}`);
                }
            }
        }
    });
}

function updateUnavailabilityList(unavailabilitySlots) {
    const list = document.getElementById("unavailabilityList");
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    list.innerHTML = '';

    unavailabilitySlots.forEach(slot => {
        const startDate = new Date(slot.start);
        const endDate = new Date(slot.end);
        const day = dayNames[startDate.getDay()];

        const listItem = document.createElement("a");
        listItem.className = "d-flex align-items-center justify-content-start p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
        listItem.href = "#";

        // Store the unavailability ID as a data attribute on the list item
        listItem.dataset.unavailabilityId = slot.unavailabilityID;

        listItem.onclick = function (e) {
            e.preventDefault();
            deleteUnavailability(listItem.dataset.unavailabilityId);
        };

        // HTML structure with a wrapper for the day and time
        listItem.innerHTML = `
        <i class="bi bi-trash3-fill me-2 d-flex align-items-center"></i>
        <div class="d-flex flex-column align-items-center w-100">
            <span class="text-center">${day}</span>
            <span class="fw-bold text-center">${formatTime(startDate)} <span>to</span> ${formatTime(endDate)}</span>
        </div>
        `;
    

        list.appendChild(listItem);
    });
}

/// Increment / Decrement Week
function updateWeek(offset) {
    const scheduleDateInput = document.getElementById('unavailabilityDate');
    const [year, weekString] = scheduleDateInput.value.split('-W');
    let yearNumber = parseInt(year, 10);
    let weekNumber = parseInt(weekString, 10) + offset;

    // Handle week/year rollover
    if (weekNumber < 1) {
        yearNumber -= 1;
        weekNumber = 52; // Last week of previous year
    } else if (weekNumber > 52) {
        yearNumber += 1;
        weekNumber = 1;
    }

    const formattedWeek = `${yearNumber}-W${weekNumber.toString().padStart(2, '0')}`;
    scheduleDateInput.value = formattedWeek;
    console.log(scheduleDateInput)
    loadUnavailability();
}

// Helper function to format time as HH:MM
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}