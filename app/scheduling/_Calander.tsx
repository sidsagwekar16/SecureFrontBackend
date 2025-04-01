"use client";
import React from "react";
import moment from "moment";
import { Calendar, momentLocalizer, View, Views } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";

// Define the event interface to match your main component
interface CalendarEvent {
  id: number | string;
  title: string;
  start: Date;
  end: Date;
  employeeId?: string;
}

// Create localizer
const localizer = momentLocalizer(moment);

interface CustomCalendarProps {
  events?: CalendarEvent[];
  onSelectSlot?: (slotInfo: { start: Date; end: Date }) => void;
  onSelectEvent?: (event: CalendarEvent) => void;
  components?: any;
  defaultView?: View;
}

const CustomCalendar = ({
  events = [],
  onSelectSlot,
  onSelectEvent,
  components,
  defaultView = Views.WEEK,
}: CustomCalendarProps) => {
  return (
    <div className="h-full">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        selectable
        views={[Views.WEEK, Views.DAY, Views.AGENDA]}
        defaultView={defaultView}
        defaultDate={new Date()}
        step={60}
        timeslots={1}
        min={new Date(new Date().setHours(9, 0, 0))}
        max={new Date(new Date().setHours(17, 0, 0))}
        onSelectSlot={onSelectSlot}
        onSelectEvent={onSelectEvent}
        style={{ height: 600 }}
        components={components}
      />
    </div>
  );
};

export default CustomCalendar;
