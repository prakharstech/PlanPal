// src/Calendar.jsx
import React from 'react';

function GoogleCalendar({ userEmail }) {
  // Use the user's email for the calendar source URL, or default if not available
  const calendarUrl = `https://calendar.google.com/calendar/embed?src=${encodeURIComponent(userEmail)}&ctz=Asia/Kolkata`;

  return (
    <div className="calendar-container">
      <iframe
        src={calendarUrl}
        style={{ border: 0 }}
        width="800"
        height="600"
        frameBorder="0"
        scrolling="no"
        title="Google Calendar"
      ></iframe>
    </div>
  );
}

export default GoogleCalendar;