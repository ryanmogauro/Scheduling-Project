let availabilitySlots = [];

function openModal() {
    document.getElementById("availabilityModal").style.display = "block";
}

function closeModal() {
    document.getElementById("availabilityModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    loadAvailability();
});

function loadAvailability() {
    fetch('/get_unavailability')
        .then(response => response.json())
        .then(data => {
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
                listItem.innerHTML = `<i class="bi bi-trash3-fill me-2"></i> ${slot.day}: ${slot.startTime} - ${slot.endTime}`;

                list.appendChild(listItem);
            });

            updateScheduleGrid();
        })
        .catch(error => console.error("Error loading availability:", error));
}

function addAvailability() {
    const day = document.getElementById("day-select").value;
    const startTime = document.getElementById("start-time").value;
    const endTime = document.getElementById("end-time").value;

    if (startTime && endTime) {
        const slot = { day, startTime, endTime };

        fetch('/add_availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(slot)
        }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    availabilitySlots.push(slot);

                    const list = document.getElementById("availabilityList");
                    const listItem = document.createElement("a");
                    listItem.href = "#";
                    listItem.className = "d-flex align-items-center justify-content-between p-2 mb-2 bg-brown text-white rounded small-font text-decoration-none";
                    listItem.onclick = function (e) {
                        e.preventDefault();
                        deleteAvailability(slot, listItem);
                    };
                    listItem.innerHTML = `<i class="bi bi-trash3-fill me-2"></i> ${slot.day}: ${slot.startTime} - ${slot.endTime}`;

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
    fetch('/delete_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(slot)
    }).then(response => response.json())
        .then(data => {
            if (data.success) {
                availabilitySlots = availabilitySlots.filter(s => !(s.day === slot.day && s.startTime === slot.startTime && s.endTime === slot.endTime));
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
    fetch('/clear_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
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