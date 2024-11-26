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
    document.getElementById('scheduleDate').value = formattedWeek;
    loadSchedule();
    updateNotificationDot();
};

/// Print Page
function printPage() {
    window.print();
  }


/// Notifications
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

/// Loading schedule -- ISO Format!
document.getElementById('scheduleDate').addEventListener('change', function() {
    loadSchedule();
});

function loadSchedule() {
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
        updateScheduleGrid(shifts);
    })
    .catch(error => console.error("Error loading schedule:", error));
}

function updateScheduleGrid(scheduleSlots) {
    // Clear all cells to default styles
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.style.backgroundColor = 'white';
        cell.style.color = 'black';
        cell.innerText = '';
    });

    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    scheduleSlots.forEach(slot => {
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
                    cell.style.backgroundColor = '#6F4E37';  
                    cell.style.color = 'white';
                    cell.style.textAlign = 'center';
                    cell.style.display = 'flex'; 
                    cell.style.alignItems = 'center';
                    cell.style.justifyContent = 'center';
                    cell.innerText = `${formatTime(startDate)} - ${formatTime(endDate)}`;
                }
            }
        }
    });
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
}


// Helper function to format time as HH:MM
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}
