/// On Page Load
window.onload = function() {
    const today = new Date();
    const year = today.getFullYear();
    const startOfYear = new Date(year, 0, 1);
    const days = Math.floor((today - startOfYear) / (24 * 60 * 60 * 1000));
    const weekNumber = Math.ceil((days + 1) / 7);

    // Format the value in YYYY-Www format
    const formattedWeek = `${year}-W${weekNumber.toString().padStart(2, '0')}`;

    // Set the value of the input field to the current week
    document.getElementById('availabilityDate').value = formattedWeek;
    loadAvailability();
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
        notifications.forEach(notification => {
            addNotification(notification.message, notification.hasRead, notification.sendTime);
            updateNotificationDot();
        });
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
        time.classList.add('text-muted', 'mt-1','timestamp');
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


function getISOWeek(date) {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const daysInYear = (date - firstDayOfYear) / (1000 * 60 * 60 * 24);
    return Math.ceil((daysInYear + firstDayOfYear.getDay() + 1) / 7);
}

let availabilitySlots = [];

function openModal() {
    document.getElementById("availabilityModal").style.display = "block";
}

function closeModal() {
    document.getElementById("availabilityModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    const availabilityDateInput = document.getElementById('availabilityDate');
    const savedWeek = localStorage.getItem('selectedWeek');
    
    if (savedWeek) {
        availabilityDateInput.value = savedWeek;
    } else {
        const today = new Date();
        const currentYear = today.getFullYear();
        const currentWeek = getISOWeek(today);
        availabilityDateInput.value = `${currentYear}-W${currentWeek}`;
    }

    loadAvailability();

    availabilityDateInput.addEventListener('change', () => {
        const weekInput = availabilityDateInput.value;
        localStorage.setItem('selectedWeek', weekInput); 
        loadAvailability(); 
    });
});




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





function loadAvailability() {
    const weekInput = document.getElementById('availabilityDate').value;
    const [year, week] = weekInput.split("-W").map(Number);
    const startOfWeek = day_week_to_date(year, week, "Monday")
    console.log("loading avail for : ", startOfWeek)
    fetch('/get_unavailability', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({ startOfWeek : startOfWeek})
    })
        .then(response => response.json())
        .then(data => {
            console.log("Loaded availability slots:", data.availability);
            availabilitySlots = data.availability;

            const list = document.getElementById("availabilityList");
            list.innerHTML = "";

            availabilitySlots.forEach(slot => {
                const list = document.getElementById("availabilityList");
                const listItem = document.createElement("a");
                listItem.className = "d-flex align-items-center justify-content-between p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
                listItem.href = "#";
                listItem.onclick = function (e) {
                    e.preventDefault();
                    deleteAvailability(slot, listItem);
                };
                listItem.innerHTML = `<i class="bi bi-trash3-fill me-2"></i> ${slot.day}: &nbsp;&nbsp;${slot.startTime} - ${slot.endTime}`;

                list.appendChild(listItem);
            });

            updateScheduleGrid();
        })
        .catch(error => console.error("Error loading availability:", error));
    }



function addAvailability() {
    const weekInput = document.getElementById('availabilityDate').value;
    const [year, week] = weekInput.split("-W").map(Number);
    const day = document.getElementById("day-select").value;
    const date = day_week_to_date(year, week, day)
    const startTime = document.getElementById("start-time").value;
    const endTime = document.getElementById("end-time").value;

    if (startTime && endTime) {
        const slot = { day, date, startTime, endTime };

        fetch('/add_availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(slot)
        }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (!Array.isArray(availabilitySlots)) {
                        availabilitySlots = []; 
                    }
                    availabilitySlots.push(slot);

                    const list = document.getElementById("availabilityList");
                    const listItem = document.createElement("a");
                    listItem.href = "#";
                    listItem.className = "d-flex align-items-center justify-content-between p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
                    listItem.onclick = function (e) {
                        e.preventDefault();
                        deleteAvailability(slot, listItem);
                    };
                    listItem.innerHTML = `<i class="bi bi-trash3-fill me-2"></i> ${slot.day}: &nbsp;&nbsp;${slot.startTime} - ${slot.endTime}`;

                    list.appendChild(listItem);

                    updateScheduleGrid();

                    closeModal();
                } else {
                    alert("Failed to add availability.");
                }
            })
            .catch(error => console.error("Error adding availability:", error));
    } else {
        alert("Please select both start and end times.");
    }
}

function deleteAvailability(slot, listItem) {

    console.log("Deleting this slot ", slot)
    const dataToDelete = {
        date: slot.date,  
        startTime: slot.startTime,
        endTime: slot.endTime  
    };

    fetch('/delete_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToDelete)
    }).then(response => response.json())
        .then(data => {
            if (data.success) {
                availabilitySlots = availabilitySlots.filter(s => !(s.date === slot.date && s.startTime === slot.startTime && s.endTime === slot.endTime));
                listItem.remove();
                updateScheduleGrid();
            } else {
                alert("Failed to delete availability.");
            }
        })
        .catch(error => console.error("Error deleting availability:", error));
}

function updateScheduleGrid() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.style.backgroundColor = 'white';
    });

    availabilitySlots.forEach(slot => {
        const day = slot.day;
        const startHour = parseInt(slot.startTime.split(":")[0]);
        const endHour = parseInt(slot.endTime.split(":")[0]);

        for (let hour = startHour; hour < endHour; hour++) {
            if (hour >= 7 && hour <= 18) {
                const cellId = `cell-${day}-${hour}`;
                const cell = document.getElementById(cellId);
                if (cell) {
                    cell.style.backgroundColor = '#6F4E37';  
                    cell.style.color = 'white';
                    
                    cell.style.textAlign = 'center';
                    cell.style.display = 'flex'; 
                    cell.style.alignItems = 'center';
                    cell.style.justifyContent = 'center';
                    cell.innerText = `${slot.startTime} - ${slot.endTime}`;
                }
            }
        }
    });
}

function clearAvailability() {
    const weekInput = document.getElementById('availabilityDate').value;
    const [year, week] = weekInput.split("-W").map(Number);
    const startOfWeek = day_week_to_date(year, week, "Monday")
    console.log("sending start of week ", startOfWeek)
    const formattedStartOfWeek = startOfWeek.toISOString().split('T')[0]
    fetch('/clear_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({startOfWeek: formattedStartOfWeek})
    }).then(response => response.json())
        .then(data => {
            if (data.success) {
                availabilitySlots = [];
                document.getElementById("availabilityList").innerHTML = "";
                updateScheduleGrid();
            } else {
                alert("Failed to clear availability.");
            }
        })
        .catch(error => console.error("Error clearing availability:", error));
}

/// Increment / Decrement Week
function updateWeek(offset) {
    const scheduleDateInput = document.getElementById('availabilityDate');
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
    loadAvailability();
}