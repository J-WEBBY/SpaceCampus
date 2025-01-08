let tasks = [];

// Fetch tasks from the backend on page load
window.onload = fetchTasks;

// Add event listeners
document.getElementById("add-task-button").addEventListener("click", addTask);
document.getElementById("filter-select").addEventListener("change", filterTasks);

function fetchTasks() {
    fetch('/get-tasks') // Only returns tasks for the current user (handled in backend)
        .then(response => response.json())
        .then(data => {
            tasks = data.tasks; // Fetch user-specific tasks
            renderTasks();
        })
        .catch(error => console.error("Error fetching tasks:", error));
}

function addTask(event) {
    event.preventDefault();

    const taskInput = document.getElementById("task-input");
    const taskDate = document.getElementById("task-date");
    const taskTime = document.getElementById("task-time");
    const taskType = document.getElementById("task-type");

    const taskDescription = taskInput.value.trim();
    const date = taskDate.value;
    const time = taskTime.value;
    const type = taskType.value;

    if (!taskDescription || !date || !time || !type) {
        alert("Please fill in all fields!");
        return;
    }

    const task = { description: taskDescription, date, time, type };

    fetch('/add-task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task),
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                fetchTasks(); // Refresh tasks after addition
                taskInput.value = "";
                taskDate.value = "";
                taskTime.value = "";
                taskType.value = "";
            } else {
                alert(data.error || "An error occurred.");
            }
        })
        .catch(error => console.error("Error adding task:", error));
}

function toggleTaskCompletion(taskId) {
    fetch(`/toggle-task/${taskId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                fetchTasks(); // Refresh tasks after toggling completion
            } else {
                alert(data.error || "An error occurred.");
            }
        })
        .catch(error => console.error("Error toggling task completion:", error));
}

function filterTasks() {
    const filter = document.getElementById("filter-select").value;

    let filteredTasks = [...tasks];
    const now = new Date();

    if (filter === "overdue") {
        filteredTasks = tasks.filter(task => new Date(`${task.date}T${task.time}`) < now && !task.completed);
    } else if (filter === "completed") {
        filteredTasks = tasks.filter(task => task.completed);
    } else if (filter === "remaining") {
        filteredTasks = tasks.filter(task => !task.completed);
    } else if (filter === "study-plan") {
        filteredTasks = tasks.filter(task => task.type === "Study Plan");
    } else if (filter === "assignment-planner") {
        filteredTasks = tasks.filter(task => task.type === "Assignment Planner");
    } else if (filter === "to-do-list") {
        filteredTasks = tasks.filter(task => task.type === "To-do List");
    }

    renderTasks(filteredTasks);
}

function renderTasks(filteredTasks = tasks) {
    const taskList = document.getElementById("task-list");
    taskList.innerHTML = "";

    const now = new Date();
    filteredTasks.forEach(task => {
        const taskDateTime = new Date(`${task.date}T${task.time}`);
        const isPastDeadline = taskDateTime < now;

        const listItem = document.createElement("li");
        listItem.className = isPastDeadline && !task.completed ? "past-deadline" : "";

        listItem.innerHTML = `
            <div class="task-content">
                <input type="checkbox" ${task.completed ? "checked" : ""} onclick="toggleTaskCompletion(${task.id})">
                <span>${task.description}</span>
                <span class="task-meta">(${task.type}) - ${task.date} at ${task.time}</span>
            </div>
        `;
        taskList.appendChild(listItem);
    });

    updateStats();
}

function updateStats() {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(task => task.completed).length;
    const remainingTasks = totalTasks - completedTasks;
    const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    document.getElementById("progress-percentage").textContent = `${progress}% Completed`;
    document.getElementById("tasks-remaining").textContent = `${remainingTasks} Remaining`;
}

document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
});