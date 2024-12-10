
let currentSchedule = null;

function updateSidebarMessage(startOfWeek) {
    const messageItem = document.getElementById("currentWeekMessageItem");

    const formattedDate = new Date(startOfWeek).toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
    });

    if (messageItem) {
        messageItem.querySelector("span").textContent = `Generating schedule for week starting ${formattedDate}`;
        messageItem.classList.remove("d-none");
    }
}

window.onload = function() {
    const today = new Date();
    const year = today.getFullYear();
    const startOfYear = new Date(year, 0, 1);
    const days = Math.floor((today - startOfYear) / (24 * 60 * 60 * 1000));
    
    let weekNumber = Math.ceil((days + 1) / 7); // use let instead of const here
    // weekNumber += 1; // now this is allowed since weekNumber is declared with let

    let nextWeekYear = year;
    if (weekNumber > 52) {
        weekNumber = 1;
        nextWeekYear += 1;
    }
    
    const formattedWeek = `${nextWeekYear}-W${weekNumber.toString().padStart(2, '0')}`;
    document.getElementById('adminDate').value = formattedWeek;
    loadNotifications()
    loadAdminSchedule()
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

document.getElementById('adminDate').addEventListener('change', function () {
    const approveButton = document.getElementById('approve-schedule-button');
    if (approveButton) {
        approveButton.classList.add("d-none"); // Hide the button
    }
    loadAdminSchedule();

});

function loadAdminSchedule() {
    const adminDate = document.getElementById('adminDate').value;
    if (!adminDate) {
        console.log("No admnin date selected.");
        return; // Don't proceed if no date is selected
    }
    fetch('/get_admin_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ adminDate })
    })
        .then(response => response.json())
        .then(data => {
            adminSlots = data.schedule;
            updateAdminGrid(adminSlots);
        })
        .catch(error => console.error("Error loading availability:", error));
}


function getISOWeek(date) {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const daysInYear = (date - firstDayOfYear) / (1000 * 60 * 60 * 24);
    return Math.ceil((daysInYear + firstDayOfYear.getDay() + 1) / 7);
}

function day_week_to_date(year, week, day) {
    const dayMap = {
        Monday: 0,
        Tuesday: 1,
        Wednesday: 2,
        Thursday: 3,
        Friday: 4,
        Saturday: 5,
        Sunday: 6
    };

    const jan4 = new Date(Date.UTC(year, 0, 4));

    const jan4DayOfWeek = jan4.getUTCDay();

    const isoWeekStart = new Date(jan4);
    isoWeekStart.setUTCDate(jan4.getUTCDate() - ((jan4DayOfWeek + 6) % 7));

    const desiredWeekStart = new Date(isoWeekStart);
    desiredWeekStart.setUTCDate(isoWeekStart.getUTCDate() + (week - 1) * 7);

    const desiredDate = new Date(desiredWeekStart);
    desiredDate.setUTCDate(desiredWeekStart.getUTCDate() + dayMap[day]);

    return desiredDate;
}

// Function to compare two weeks (returns negative if first week is earlier)
function compareWeeks(week1, week2) {
    const [year1, weekNum1] = week1.split('-W').map(Number);
    const [year2, weekNum2] = week2.split('-W').map(Number);

    // Compare the years first
    if (year1 !== year2) {
        return year1 - year2;
    }

    // If the years are the same, compare the week numbers
    return weekNum1 - weekNum2;
}

// Function to get the current week in 'YYYY-Www' format
function getNextWeek() {
    const today = new Date();
    const year = today.getFullYear();
    const startOfYear = new Date(year, 0, 1);
    const days = Math.floor((today - startOfYear) / (24 * 60 * 60 * 1000));
    let weekNumber = Math.ceil((days + 1) / 7);

    weekNumber += 1; // now this is allowed since weekNumber is declared with let

    let nextWeekYear = year;
    if (weekNumber > 52) {
        weekNumber = 1;
        nextWeekYear += 1;
    }

    // Format the value in YYYY-Www format
    return `${year}-W${weekNumber.toString().padStart(2, '0')}`;
}

function openGenerateScheduleModal() {
    const weekInput = document.getElementById('adminDate').value;
    const selectedWeek = compareWeeks(weekInput, getNextWeek());

    if (selectedWeek < 0) {
        alert("You cannot select a past week. Please select a week starting from next week.");
        return; // Prevent the modal from showing if the selected week is before next week
    }

    const [year, week] = weekInput.split('-W').map(Number);
    const startOfWeek = day_week_to_date(year, week, "Monday");

    const formattedDate = new Date(startOfWeek).toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
    });

    const modalMessage = document.getElementById("modalMessage");
    modalMessage.textContent = `Are you sure you want to generate a schedule for the week starting on ${formattedDate}?`;
    const generateScheduleModal = new bootstrap.Modal(document.getElementById('generateScheduleModal'), {
        backdrop: 'static', // Prevent closing by clicking outside the modal
        keyboard: false     // Disable closing the modal with the escape key
    });
    generateScheduleModal.show();

    const approveButton = document.getElementById('approve-schedule-button');
    if (approveButton) {
        console.log("Setting Approve Schedule button to visible");
        approveButton.style.display = 'show'; // Make the button visible
    } else {
        console.log("Approve Schedule button not found");
    }
}

function closeGenerateScheduleModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('generateScheduleModal'));
    modal.hide(); 
    document.getElementById('generate-schedule-button').focus();
}

function confirmGenerateSchedule() {
    const weekInput = document.getElementById('adminDate').value;
    const [year, week] = weekInput.split('-W').map(Number);
    const str_start_date = day_week_to_date(year, week, "Monday")
    const start_date = str_start_date.toISOString().split('T')[0];

    console.log('Request Body:', JSON.stringify({ start_date: start_date }));
    fetch('/generate_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ start_date: start_date }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            if (data.success) {
                console.log("This is schedule: ", data.schedule)
                updateAdminGrid(data.schedule); 
                currentSchedule = data.schedule
                approveButton = document.getElementById('approve-schedule-button');
                approveButton.classList.remove("d-none")
                alert('Schedule generated successfully!');
            } else {
                alert(data.message || 'Failed to generate schedule.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while generating the schedule.');
        });

    closeGenerateScheduleModal();
}




document.getElementById('approve-schedule-button').addEventListener('click', function () {
    const schedule = currentSchedule; 
    const weekInput = document.getElementById('adminDate').value;
    const [year, week] = weekInput.split('-W').map(Number);
    const str_start_date = day_week_to_date(year, week, "Monday")
    const start_date = str_start_date.toISOString().split('T')[0];

    if (schedule) {
        fetch('/approve_schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ schedule: schedule, start_date: start_date}),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert('Schedule approved successfully!');
                    approveButton = document.getElementById('approve-schedule-button');
                    approveButton.classList.add("d-none");

                    document.getElementById('generate-schedule-button').disabled = true;
                } else {
                    alert(data.message || 'Failed to approve schedule.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred while approving the schedule.');
            });
    } else {
        alert('No schedule data available to approve.');
    }
});

function approveSchedule() {
    console.log('Approve Schedule button clicked.');
    const schedule = getCurrentSchedule();

    if (schedule) {
        fetch('/approve_schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ schedule: schedule }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert('Schedule approved successfully!');
                approveButton = document.getElementById('approve-schedule-button');
                approveButton.classList.add("d-none");
                document.getElementById('generate-schedule-button').disabled = true;
            } else {
                alert(data.message || 'Failed to approve schedule.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while approving the schedule.');
        });
    } else {
        alert('No schedule data available to approve.');
    }
}

function updateWeek(offset) {
    const scheduleDateInput = document.getElementById('adminDate');
    const [year, weekString] = scheduleDateInput.value.split('-W');
    let yearNumber = parseInt(year, 10);
    let weekNumber = parseInt(weekString, 10) + offset;

    if (weekNumber < 1) {
        yearNumber -= 1;
        weekNumber = 52; 
    } else if (weekNumber > 52) {
        yearNumber += 1;
        weekNumber = 1;
    }

    const formattedWeek = `${yearNumber}-W${weekNumber.toString().padStart(2, '0')}`;
    scheduleDateInput.value = formattedWeek;
    

    loadAdminSchedule();
}

function getCurrentWeekMonday() {
    const today = new Date();
    const dayOfWeek = (today.getDay() + 6) % 7; 
    const monday = new Date(today);
    monday.setDate(monday.getDate() - dayOfWeek);
    return monday;
}

function getISOWeekNumber(date) {
    const tempDate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = tempDate.getUTCDay() || 7;
    tempDate.setUTCDate(tempDate.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(tempDate.getUTCFullYear(),0,1));
    return Math.ceil((((tempDate - yearStart) / 86400000) + 1)/7);
}

function updateAdminGrid(schedule) {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.innerHTML = '';
        cell.style.backgroundColor = 'white';
    });

    Object.keys(schedule).forEach(day => {
        const daySchedule = schedule[day];
        const slots = daySchedule.slots;

        const slotsByHour = {};
        slots.forEach(slot => {
            const time = slot.time;
            const employees = slot.employees;
            const [hourStr, minuteStr] = time.split(':');
            const hour = parseInt(hourStr, 10);

            if (!slotsByHour[hour]) {
                slotsByHour[hour] = [];
            }

            slotsByHour[hour].push({
                minute: minuteStr,
                employees: employees
            });
        });

        Object.keys(slotsByHour).forEach(hourStr => {
            const hour = parseInt(hourStr, 10);
            const cellId = `cell-${day}-${hour}`;
            const cell = document.getElementById(cellId);

            if (cell) {
                const hourSlots = slotsByHour[hour];
                hourSlots.sort((a, b) => parseInt(a.minute, 10) - parseInt(b.minute, 10));

                // Create a list inside the cell to hold the bubbles if it's the first time we add time slots
                let list = cell.querySelector('.time-list');
                if (!list) {
                    list = document.createElement('div');
                    list.className = 'time-list';
                    list.style.textAlign = 'center';
                    list.style.fontSize = '10px';
                    cell.appendChild(list);
                }

                // Loop over each slot for this hour
                hourSlots.forEach(slot => {
                    const bubble = document.createElement('div');
                    bubble.className = 'bubble';
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
                    if (slot.minute === '00') {
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

                    // Add employee names instead of time range
                    bubble.appendChild(icon);
                    bubble.appendChild(document.createTextNode(slot.employees.map(e => e.name).join(', ')));
                    list.appendChild(bubble);
                });
            } else {
                console.warn(`Cell not found: ${cellId}`);
            }
        });
    });
}
