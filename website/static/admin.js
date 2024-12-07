
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
    weekNumber += 1; // now this is allowed since weekNumber is declared with let

    let nextWeekYear = year;
    if (weekNumber > 52) {
        weekNumber = 1;
        nextWeekYear += 1;
    }
    
    const formattedWeek = `${nextWeekYear}-W${weekNumber.toString().padStart(2, '0')}`;
    document.getElementById('availabilityDate').value = formattedWeek;
};


function printPage() {
    window.print();
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


function openGenerateScheduleModal() {
    const weekInput = document.getElementById('availabilityDate').value;
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
    const generateScheduleModal = new bootstrap.Modal(document.getElementById('generateScheduleModal'));
    generateScheduleModal.show();
}

function closeGenerateScheduleModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('generateScheduleModal'));
    modal.hide(); 
    document.getElementById('generate-schedule-button').focus();
}

function confirmGenerateSchedule() {
    const weekInput = document.getElementById('availabilityDate').value;
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
                displaySchedule(data.schedule); 
                currentSchedule = data.schedule
                document.getElementById('approve-schedule-button').style.display = 'inline-block';
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
    const weekInput = document.getElementById('availabilityDate').value;
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
                    document.getElementById('approve-schedule-button').style.display = 'none';
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

document.getElementById('approve-schedule-button').addEventListener('click', function () {
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
                document.getElementById('approve-schedule-button').style.display = 'none';
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


function updateWeek(offset) {
    const scheduleDateInput = document.getElementById('availabilityDate');
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
    const currentMonday = getCurrentWeekMonday();
    const currentWeekYear = currentMonday.getFullYear();
    const currentWeekNumber = getISOWeekNumber(currentMonday);

    if (yearNumber < currentWeekYear || (yearNumber === currentWeekYear && weekNumber <= currentWeekNumber)) {
        alert("You cannot schedule for a past week.");
        const revertWeek = `${currentWeekYear}-W${String(currentWeekNumber+1).padStart(2, '0')}`;
        scheduleDateInput.value = revertWeek;
    } else {
        scheduleDateInput.value = formattedWeek;
    }
    console.log("Selected week:", scheduleDateInput.value);
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


function displaySchedule(schedule) {
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

                cell.style.backgroundColor = '#6F4E37';
                cell.style.color = 'white';
                cell.style.textAlign = 'center';
                cell.style.display = 'flex';
                cell.style.flexDirection = 'column'; 
                cell.style.alignItems = 'stretch';
                cell.style.justifyContent = 'stretch'; 
                cell.style.padding = '0';

                cell.innerHTML = '';

                hourSlots.forEach(slot => {
                    const slotDiv = document.createElement('div');
                    slotDiv.style.flex = '1'; 
                    slotDiv.style.display = 'flex';
                    slotDiv.style.alignItems = 'center';
                    slotDiv.style.justifyContent = 'center';
                    slotDiv.style.borderBottom = '1px solid #fff';

                    slotDiv.innerText = slot.employees.map(e => e.name).join(', ');
                    cell.appendChild(slotDiv);
                });

                if (cell.lastChild) {
                    cell.lastChild.style.borderBottom = 'none';
                }
            } else {
                console.warn(`Cell not found: ${cellId}`);
            }
        });
    });
}
