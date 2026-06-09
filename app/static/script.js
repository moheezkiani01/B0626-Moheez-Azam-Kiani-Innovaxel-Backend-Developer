const messageBox = document.getElementById("message");
const eventsTableBody = document.getElementById("eventsTableBody");

function showMessage(text, type = "success") {
  messageBox.innerHTML = `<div class="message-${type}">${text}</div>`;

  setTimeout(() => {
    messageBox.innerHTML = "";
  }, 4000);
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const errorMessage = data?.detail || "Something went wrong";
    throw new Error(errorMessage);
  }

  return data;
}

function localDateTimeToIso(value) {
  return value;
}

async function loadEvents() {
  const sortByDate = document.getElementById("sortByDate").checked;
  const upcomingOnly = document.getElementById("upcomingOnly").checked;

  const params = new URLSearchParams({
    sort_by_date: sortByDate,
    upcoming_only: upcomingOnly,
  });

  try {
    const events = await requestJson(`/events?${params.toString()}`);

    if (events.length === 0) {
      eventsTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="empty">No events found.</td>
        </tr>
      `;
      return;
    }

    eventsTableBody.innerHTML = events
      .map((event) => {
        const readableDate = new Date(event.event_date).toLocaleString();

        return `
          <tr>
            <td>${event.id}</td>
            <td>${event.name}</td>
            <td>${readableDate}</td>
            <td>${event.total_seats}</td>
            <td>${event.total_registrations}</td>
            <td>${event.available_seats}</td>
          </tr>
        `;
      })
      .join("");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

document.getElementById("createEventForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const eventName = document.getElementById("eventName").value.trim();
  const totalSeats = Number(document.getElementById("totalSeats").value);
  const eventDate = document.getElementById("eventDate").value;

  const payload = {
    name: eventName,
    total_seats: totalSeats,
    event_date: localDateTimeToIso(eventDate),
  };

  console.log("Create event payload:", payload);

  try {
    await requestJson("/events", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    event.target.reset();
    showMessage("Event created successfully.");
    await loadEvents();
  } catch (error) {
    console.error(error);
    showMessage(error.message, "error");
  }
});

document.getElementById("registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    user_name: document.getElementById("registerUserName").value.trim(),
    event_id: Number(document.getElementById("registerEventId").value),
  };

  try {
    await requestJson("/registrations", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    event.target.reset();
    showMessage("User registered successfully.");
    await loadEvents();
  } catch (error) {
    showMessage(error.message, "error");
  }
});

document.getElementById("cancelForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    user_name: document.getElementById("cancelUserName").value.trim(),
    event_id: Number(document.getElementById("cancelEventId").value),
  };

  try {
    await requestJson("/registrations", {
      method: "DELETE",
      body: JSON.stringify(payload),
    });

    event.target.reset();
    showMessage("Registration cancelled successfully.");
    await loadEvents();
  } catch (error) {
    showMessage(error.message, "error");
  }
});

document.getElementById("refreshEvents").addEventListener("click", loadEvents);
document.getElementById("sortByDate").addEventListener("change", loadEvents);
document.getElementById("upcomingOnly").addEventListener("change", loadEvents);

loadEvents();