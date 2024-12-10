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
    document.getElementById('scheduleDate').value = formattedWeek;
    loadSchedule();
    loadNotifications();
    getShiftTrades(); 
};

/// Print Page
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
document.getElementById('scheduleDate').addEventListener('change', function () {
    loadSchedule();
    getShiftTrades(); 
});

function loadSchedule(forModal = false) {
    const scheduleDate = document.getElementById('scheduleDate').value;
    if (!scheduleDate) {
        console.log("No schedule date selected.");
        return; // Don't proceed if no date is selected
    }

    fetch('/get_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ scheduleDate })
    })
        .then(response => response.json())
        .then(data => {
            const shifts = data.shifts;
            if (forModal) {
                populateShiftTradeModal(shifts); // Populate the modal
            } else {
                updateScheduleGrid(shifts); // Update the regular schedule
                calculateTotalWageAndHours(shifts);
            }
        })
        .catch(error => console.error("Error loading schedule:", error));
}


function exportSchedule() {
    const scheduleDate = document.getElementById('scheduleDate').value;
    if (!scheduleDate) {
        console.log("No schedule date selected.");
        return; // Don't proceed if no date is selected
    }

    fetch('/export_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            scheduleDate,
        })
    })
        .then(response => response.blob())
        .then(data => {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(data);
            a.download = 'schedule.ics'; // Provide a default filename
            a.click();
        })
        .catch(error => console.error("Error loading schedule:", error));
}

function updateScheduleGrid(scheduleSlots) {
    // Clear all cells to default styles
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.style.background = 'white';
        cell.style.color = 'white';
        cell.innerHTML = ''; // Ensure no content is left behind
    });

    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    scheduleSlots.forEach(slot => {
        const startDate = new Date(slot.start);
        const endDate = new Date(slot.end);

        // Extract the day, start hour, and end hour
        const day = dayNames[startDate.getDay()];
        const startHour = startDate.getHours();

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
            bubble.className = 'bubble'
            bubble.style.display = 'flex';
            bubble.style.alignItems = 'center';
            bubble.style.marginBottom = '4px';
            bubble.style.marginTop = '4px';
            bubble.style.paddingRight = '4px';
            bubble.style.borderRadius = '5px';

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

            bubble.appendChild(icon);
            bubble.appendChild(document.createTextNode(`${formatTime(startDate)}-${formatTime(endDate)}`));
            list.appendChild(bubble);
        }
    });
}

/// Get Hours Worked
function calculateTotalHours(shifts) {
    // Sort the shifts by start time
    const sortedShifts = shifts.map(shift => ({
        start: new Date(shift.start),
        end: new Date(shift.end)
    })).sort((a, b) => a.start - b.start);

    let totalHours = 0;
    let currentShift = null;

    // Loop through each shift and calculate total hours
    sortedShifts.forEach(shift => {
        if (!currentShift) {
            // If no current shift, just set the first one
            currentShift = shift;
        } else {
            // If there's an overlap, merge the shifts
            if (shift.start < currentShift.end) {
                // There is overlap, so we extend the current shift's end time
                currentShift.end = new Date(Math.max(currentShift.end, shift.end));
            } else {
                // No overlap, so add the previous shift's hours and start a new shift
                totalHours += (currentShift.end - currentShift.start) / (1000 * 60 * 60);  // Convert ms to hours
                currentShift = shift;  // Update to the current shift
            }
        }
    });

    // Add the last shift's hours
    if (currentShift) {
        totalHours += (currentShift.end - currentShift.start) / (1000 * 60 * 60);  // Convert ms to hours
    }

    return totalHours.toFixed(2); // Round to 2 decimal places for total hours
}

function calculateTotalWageAndHours(shifts) {
    const totalHoursWorked = calculateTotalHours(shifts);
    document.getElementById('totalHours').innerText = totalHoursWorked
    console.log(document.getElementById('hourlyWage').innerText)
    const hourlyWage = parseFloat(document.getElementById('hourlyWage').innerText.replace('$', ''));
    const totalWage = totalHoursWorked * hourlyWage;
    document.getElementById('totalWage').innerText = '$' + totalWage.toFixed(2);
}

/// Increment / Decrement Week
function updateWeek(offset) {
    const scheduleDateInput = document.getElementById('scheduleDate');
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
    loadSchedule();
    getShiftTrades(); 
}


// Helper function to format time as HH:MM
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

function submitTradeRequest() {
    const selectedShift = document.querySelector('input[name="shift"]:checked');
    if (!selectedShift) {
        alert('Please select a shift to trade.');
        return;
    }

    const shiftId = selectedShift.value;
    console.log("This is shiftID: ", shiftId)
    fetch('/trade_shift', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shift_id: shiftId})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                document.getElementById('shiftTradeModal').querySelector('.btn-close').click(); // Close modal
            } else {
                alert('Failed to request shift trade.');
            }
        })
        .catch(error => console.error('Error submitting trade request:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    const modalElement = document.getElementById('shiftTradeModal');
    if (modalElement) {
        modalElement.addEventListener('show.bs.modal', function () {
            loadSchedule(true); // Load schedule for modal
        });
    } else {
        console.error('shiftTradeModal element not found.');
    }
});

function populateShiftTradeModal(shifts) {
    console.log("Populate shifts has been called");
    const shiftList = document.getElementById('shiftList');
    shiftList.innerHTML = '';

    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    console.log("This is shifts ", shifts)
    shifts.forEach(shift => {
        const startDate = new Date(shift.start);
        const endDate = new Date(shift.end);
        const day = daysOfWeek[startDate.getDay()];



        if (!shift.shiftID) {
            console.log('Missing shiftID for shift:', shift);
            return; // Skip this iteration if shiftID is missing
        }


        const listItem = document.createElement('li');
        listItem.classList.add('list-group-item');
        listItem.innerHTML = `
            <input type="radio" name="shift" value="${shift.shiftID}" id="shift-${shift.shiftID}">
            <label for="shift-${shift.shiftID}">
                ${day}: ${formatTime(startDate)} - ${formatTime(endDate)}
            </label>
        `;
        shiftList.appendChild(listItem);
    });
}


function getShiftTrades() {
    const scheduleDate = document.getElementById('scheduleDate').value;
    fetch('/available_shifts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ week: scheduleDate })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(data.shifts); // Display the retrieved shifts
                updateTradeList(data.shifts)
            } else {
                alert('Failed to retrieve available shifts.');
            }
        })
        .catch(error => console.error('Error retrieving shifts:', error));
}

function updateTradeList(shifts) {
    const list = document.getElementById("assignList");
    if (!list) {
        console.error("assignList element not found.");
        return;
    }

    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    list.innerHTML = ''; // Clear the list

    shifts.forEach(shift => {
        const startDate = new Date(shift.shiftStartTime);
        const endDate = new Date(shift.shiftEndTime);
        const day = dayNames[startDate.getDay()];

        const listItem = document.createElement("a");
        listItem.className = "d-flex align-items-center justify-content-start p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
        listItem.href = "#";

        // Store the shift ID as a data attribute on the list item
        listItem.dataset.shiftId = shift.shiftID;

        // Add a click event to handle claiming the shift
        listItem.onclick = function (e) {
            e.preventDefault();
            console.log(`Claiming shift ID: ${listItem.dataset.shiftId}`);
            claimShift(listItem.dataset.shiftId);
        };

        // Populate the inner HTML of the list item
        listItem.innerHTML = `
            <div class="d-flex flex-column align-items-center w-100">
                <span class="text-center">${day}</span>
                <span class="fw-bold text-center">${formatTime(startDate)} <span>to</span> ${formatTime(endDate)}</span>
            </div>
        `;

        list.appendChild(listItem);
    });
}

function claimShift(shiftId) {
    fetch('/claim_shift', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shift_id: shiftId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Shift ${shiftId} claimed successfully!`);

                const shiftElement = document.querySelector(`[data-shift-id="${shiftId}"]`);
                if (shiftElement) {
                    shiftElement.remove(); // Remove the element from the DOM
                } else {
                    console.warn(`Shift element with ID ${shiftId} not found in the list.`);
                }
            } else {
                alert(`Failed to claim shift ${shiftId}: ${data.error}`);
            }
        })
        .catch(error => console.error('Error claiming shift:', error));
}
