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
    document.getElementById('eventsDate').value = formattedWeek;
    loadEvents();
    loadNotifications()
};

let eventsSlots = [];

window.addEventListener('resize', () => {
    updateEventsGrid(eventsSlots);
});

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

/// Loading schedule -- ISO Format!
document.getElementById('eventsDate').addEventListener('change', function () {
    loadEvents();
});

function closeModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('eventsModal'));
    if (modal) modal.hide();
}

function loadEvents() {
    const eventsDate = document.getElementById('eventsDate').value;
    if (!eventsDate) {
        console.log("No events date selected.");
        return; // Don't proceed if no date is selected
    }
    
    fetch('/get_events', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ eventsDate })
    })
    .then(response => response.json())
    .then(data => {
        eventsSlots = data.events;

        if (eventsSlots.length === 0) {
            // Display a message when there are no events
            showNoEventMessage("eventsList");
            showNoEventMessage("assignList");
        } else {
            const eventsList = document.getElementById("eventsList");
            if (eventsList) {
                updateEventsList(eventsSlots);
            }
            updateAssignList(eventsSlots);
        }

        updateEventsGrid(eventsSlots);
    })
    .catch(error => console.error("Error loading events:", error));
}

// Helper function to display the "no events" message
function showNoEventMessage(listId) {
    const list = document.getElementById(listId);
    
    // Check if the list exists before attempting to update it
    if (list) {
        list.innerHTML = ''; // Clear existing content
        const noEventMessage = document.createElement('p');
        noEventMessage.id = 'no-event-message';
        noEventMessage.textContent = "Nothing to see here...";
        noEventMessage.classList.add('text-muted', 'text-center', 'py-2');
        list.appendChild(noEventMessage);
    } else {
        console.warn(`Element with ID '${listId}' not found.`);
    }
}


function addEvent(){
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
    console.log(startHour)
    console.log(endHour)

    // Validation: Ensure start time is before end time and not equal
    if (startDatetime >= endDatetime) {
        alert("Start time must be before end time.");
        return;
    }

    // Convert to ISO format w/o timezone info
    const startIso = startDatetime.toISOString().slice(0, -1);
    const endIso = endDatetime.toISOString().slice(0, -1);
    
    const hostName = document.getElementById('event-host').value;
    const eventName = document.getElementById('event-name').value;
    const eventDescription = document.getElementById('event-description').value;


    fetch('/add_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            eventHost: hostName,
            eventName: eventName, 
            eventStartTime: startIso,
            eventEndTime: endIso,
            eventDescription: eventDescription,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadEvents();
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

function deleteEvent(eventID) {
    fetch('/delete_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            eventID: eventID, 
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadEvents();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
}

function clearEvents() {
    const eventsDate = document.getElementById('eventsDate').value;
    if (!eventsDate) {
        return; 
    }

    fetch('/clear_events', {
        method: 'POST',
        body: new URLSearchParams({ eventsDate }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadEvents();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while clearing unavailability');
        });
}

function updateEventsGrid(eventsSlots) {
    // Clear all cells to default styles
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.style.background = 'white';
        cell.style.color = 'white';
        cell.innerHTML = ''; // Ensure no content is left behind
    });

    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    eventsSlots.forEach(slot => {
        const startDate = new Date(slot.start);
        const endDate = new Date(slot.end);

        // Extract the day, start hour, and end hour
        const day = dayNames[startDate.getDay()];
        const startHour = startDate.getHours();
        const endHour = endDate.getHours();

        // Get the cell ID for the start hour
        const cellId = `cell-${day}-${startHour}`;
        const cell = document.getElementById(cellId);

        if (cell) {
            // Set cell's background style
            cell.style.textAlign = 'center';
            cell.style.display = 'flex';
            cell.style.alignItems = 'center';
            cell.style.justifyContent = 'center';

            // Create a list inside the cell to hold time bubbles if it's the first time we add time slots
            let list = cell.querySelector('.time-list');
            if (!list) {
                list = document.createElement('div');
                list.className = 'time-list';
                list.style.textAlign = 'center';
                list.style.fontSize = '10px';
                cell.appendChild(list);
            }

            // Create the bubble for the current time slot
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.display = 'flex';
            bubble.style.alignItems = 'center';
            bubble.style.borderRadius = '5px';
            bubble.style.position = 'absolute'; // Position it absolutely for spanning

            // Icon inside the bubble
            const icon = document.createElement('i');
            icon.className = 'bi bi-dot';
            icon.style.fontSize = '14px';

            // Apply different styles based on whether it's the top of the hour or 30 minutes
            if (startDate.getMinutes() === 0) {
                // Style for top of the hour
                bubble.style.backgroundColor = 'white';
                bubble.style.color = '#6F4E37';
                icon.style.color = '#6F4E37';
                bubble.style.borderColor = '#6F4E37';
                bubble.style.borderWidth = '1px';
                bubble.style.borderStyle = 'solid';
            } else {
                // Style for 30 minutes past the hour
                bubble.style.backgroundColor = '#6F4E37';
                bubble.style.color = 'white';
                icon.style.color = 'white';
                bubble.classList.add('border', 'border-dark');
            }

            // Set the bubble text and append the icon
            bubble.appendChild(icon);
            bubble.appendChild(document.createTextNode(`${formatTime(startDate)}-${formatTime(endDate)}`));
            list.appendChild(bubble);

            // Calculate how much space the bubble should span horizontally
            const startCell = document.getElementById(`cell-${day}-${startHour}`);
            const endCell = document.getElementById(`cell-${day}-${endHour}`);

            if (startCell && endCell) {
                const startOffset = startCell.offsetLeft + 4; //handle padding
                const endOffset = endCell.offsetLeft + endCell.offsetWidth - 4;

                bubble.style.left = `${startOffset}px`;  // Start at the start hour
                bubble.style.width = `${endOffset - startOffset}px`; // Span across the cells

                const cellHeight = startCell.offsetHeight; // Get the height of the cell
                const bubbleHeight = bubble.offsetHeight; // Get the height of the bubble
                const verticalOffset = (cellHeight - bubbleHeight) / 2; // Calculate how much to offset for centering
                bubble.style.top = `${startCell.offsetTop + verticalOffset}px`;
            }
        }
    });
}

function updateEventsList(eventsSlots) {
    const list = document.getElementById("eventsList");
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    list.innerHTML = '';

    eventsSlots.forEach(slot => {
        const startDate = new Date(slot.start);
        const endDate = new Date(slot.end);
        const day = dayNames[startDate.getDay()];

        const listItem = document.createElement("a");
        listItem.className = "d-flex align-items-center justify-content-start p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
        listItem.href = "#";

        // Store the event ID as a data attribute on the list item
        listItem.dataset.eventId = slot.eventID;

        listItem.onclick = function (e) {
            e.preventDefault();
            deleteEvent(listItem.dataset.eventId);
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

function updateAssignList(eventsSlots) {
    const list = document.getElementById("assignList");
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    list.innerHTML = '';

    eventsSlots.forEach(slot => {
        const startDate = new Date(slot.start);
        const endDate = new Date(slot.end);
        const day = dayNames[startDate.getDay()];

        const listItem = document.createElement("a");
        listItem.className = "d-flex align-items-center justify-content-start p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
        listItem.href = "#";

        // Store the event ID as a data attribute on the list item
        listItem.dataset.eventId = slot.eventID;

        listItem.onclick = function (e) {
            e.preventDefault();
            claimEvent(listItem.dataset.eventId);
        };

        // HTML structure with a wrapper for the day and time
        listItem.innerHTML = `
        <i class="bi bi-plus-circle me-2"></i>
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
    const scheduleDateInput = document.getElementById('eventsDate');
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
    loadEvents();
}

// Helper function to format time as HH:MM
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

function claimEvent(eventID){
    fetch('/claim_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            eventID: eventID,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadEvents();
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
