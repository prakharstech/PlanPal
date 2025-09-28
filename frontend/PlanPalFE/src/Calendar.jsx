import React from 'react';

function GoogleCalendar() {
  const calendarUrl = "https://calendar.google.com/calendar/embed?src=prakhar.srivastava0509%40gmail.com&ctz=Asia%2FKolkata";

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