"use client";

import React, { useState } from "react";
import { formatDate } from "@fullcalendar/core";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import { EventApi, DateSelectArg, EventClickArg } from "@fullcalendar/core";

// Import or define your event utilities
interface Event {
  id: string;
  title: string;
  start: Date | string;
  end?: Date | string;
  allDay?: boolean;
  resourceId?: string;
}

// Replace this with your actual event utilities or implement here
const INITIAL_EVENTS: Event[] = [
  { title: "nice event", start: new Date(), resourceId: "a", id: "1" },
];

const createEventId = (): string => {
  return String(Math.floor(Math.random() * 1000000));
};

export default function CalendarPage() {
  const [weekendsVisible, setWeekendsVisible] = useState<boolean>(true);
  const [currentEvents, setCurrentEvents] = useState<EventApi[]>([]);

  const handleWeekendsToggle = (): void => {
    setWeekendsVisible(!weekendsVisible);
  };

  const handleDateSelect = (selectInfo: DateSelectArg): void => {
    console.log("selectInfo", selectInfo);

    const title = prompt("Please enter a new title for your event");
    const calendarApi = selectInfo.view.calendar;

    calendarApi.unselect(); // clear date selection

    if (title) {
      calendarApi.addEvent({
        id: createEventId(),
        title,
        start: selectInfo.startStr,
        end: selectInfo.endStr,
        allDay: selectInfo.allDay,
        resourceId: selectInfo.resource ? selectInfo.resource.id : undefined,
      });
    }
  };

  const handleEventClick = (clickInfo: EventClickArg): void => {
    console.log("clickInfo", clickInfo);

    if (
      confirm(
        `Are you sure you want to delete the event '${clickInfo.event.title}'`
      )
    ) {
      clickInfo.event.remove();
    }
  };

  const handleEvents = (events: EventApi[]): void => {
    console.log("events", events);

    setCurrentEvents(events);
  };

  return (
    <div className="demo-app">
      <Sidebar
        weekendsVisible={weekendsVisible}
        handleWeekendsToggle={handleWeekendsToggle}
        currentEvents={currentEvents}
      />
      <div className="demo-app-main">
        <FullCalendar
          timeZone="Asia/Kolkata"
          plugins={[
            resourceTimelinePlugin,
            dayGridPlugin,
            timeGridPlugin,
            interactionPlugin,
          ]}
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay",
          }}
          initialView="dayGridMonth"
          editable={true}
          selectable={true}
          selectMirror={true}
          dayMaxEvents={true}
          weekends={weekendsVisible}
          initialEvents={INITIAL_EVENTS}
          select={handleDateSelect}
          eventContent={renderEventContent}
          eventClick={handleEventClick}
          eventsSet={handleEvents}
          nowIndicator={true}
          /* you can update a remote database when these fire:
          eventAdd={function(){}}
          eventChange={function(){}}
          eventRemove={function(){}}
          */
        />
      </div>
    </div>
  );
}

interface RenderEventContentProps {
  timeText: string;
  event: EventApi;
}

function renderEventContent(eventInfo: EventContentArg) {
  return (
    <>
      {/* <b>{eventInfo.timeText}</b>
      <i>{eventInfo.event.title}</i> */}
      <b>
        {eventInfo.timeText} -{" "}
        {eventInfo.event.end
          ? formatDate(eventInfo.event.end, {
              hour: "numeric",
              minute: "numeric",
              hour12: true,
            })
          : ""}
      </b>
      <i>{eventInfo.event.title}</i>
    </>
  );
}

interface SidebarProps {
  weekendsVisible: boolean;
  handleWeekendsToggle: () => void;
  currentEvents: EventApi[];
}

function Sidebar({
  weekendsVisible,
  handleWeekendsToggle,
  currentEvents,
}: SidebarProps) {
  return (
    <div className="demo-app-sidebar">
      <div className="demo-app-sidebar-section">
        <h2>Instructions</h2>
        <ul>
          <li>Select dates and you will be prompted to create a new event</li>
          <li>Drag, drop, and resize events</li>
          <li>Click an event to delete it</li>
        </ul>
      </div>
      <div className="demo-app-sidebar-section">
        <label>
          <input
            type="checkbox"
            checked={weekendsVisible}
            onChange={handleWeekendsToggle}
          />
          toggle weekends
        </label>
      </div>
      <div className="demo-app-sidebar-section">
        <h2>All Events ({currentEvents.length})</h2>
        <ul>
          {currentEvents.map((event) => (
            <SidebarEvent key={event.id} event={event} />
          ))}
        </ul>
      </div>
    </div>
  );
}

interface SidebarEventProps {
  event: EventApi;
}

function SidebarEvent({ event }: SidebarEventProps) {
  return (
    <li>
      <b>
        {formatDate(event.start!, {
          year: "numeric",
          month: "short",
          day: "numeric",
        })}
      </b>
      <i>{event.title}</i>
    </li>
  );
}

// Need to add this interface
interface EventContentArg {
  event: EventApi;
  timeText: string;
}
