// "use client";
// import { useState } from "react";
// import { Calendar, momentLocalizer, Views } from "react-big-calendar";
// import moment from "moment";
// import "react-big-calendar/lib/css/react-big-calendar.css";
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from "@/components/ui/select";
// import { Progress } from "@/components/ui/progress";
// import { Button } from "@/components/ui/button";
// import {
//   Dialog,
//   DialogContent,
//   DialogHeader,
//   DialogTitle,
//   DialogFooter,
// } from "@/components/ui/dialog";
// import { DndContext, useDraggable, useDroppable } from "@dnd-kit/core";
// import Link from "next/link";
// import CustomCalender from "./_Calander";

// const localizer = momentLocalizer(moment);

// const employees = [
//   { id: "1", name: "John Doe" },
//   { id: "2", name: "Jane Smith" },
//   { id: "3", name: "Mike Johnson" },
// ];

// const sites = [
//   { id: "site1", name: "Main Office Complex", maxHours: 160 },
//   { id: "site2", name: "Warehouse Facility", maxHours: 120 },
//   { id: "site3", name: "Retail Store", maxHours: 80 },
// ];

// function DraggableEmployee({ employee }) {
//   const { attributes, listeners, setNodeRef } = useDraggable({
//     id: employee.id,
//   });
//   return (
//     <div
//       ref={setNodeRef}
//       {...listeners}
//       {...attributes}
//       className="p-2 bg-gray-200 rounded mb-2 cursor-grab"
//     >
//       {employee.name}
//     </div>
//   );
// }

// function DroppableSlot({ date, children }) {
//   const { setNodeRef } = useDroppable({ id: date.toString() });
//   return (
//     <div ref={setNodeRef} className="h-full w-ful">
//       {children}
//     </div>
//   );
// }

// export default function SchedulingPage() {
//   const [selectedSite, setSelectedSite] = useState("site1");
//   const [events, setEvents] = useState([]);
//   const [selectedEvent, setSelectedEvent] = useState(null);
//   const [availableEmployees, setAvailableEmployees] = useState(employees);

//   const handleSelectSlot = ({ start, end }) => {
//     console.log("Selected slot:", start, end);

//     const overlappingEvent = events.find((event) => {
//       return (
//         moment(start).isBetween(event.start, event.end, null, "[)") ||
//         moment(end).isBetween(event.start, event.end, null, "(]") ||
//         moment(event.start).isBetween(start, end, null, "[)")
//       );
//     });

//     if (overlappingEvent) {
//       const updatedEvents = events.map((event) => {
//         if (event.id === overlappingEvent.id) {
//           return {
//             ...event,
//             start,
//             end,
//           };
//         }
//         return event;
//       });
//       setEvents(updatedEvents);
//     }
//   };

//   console.log("111");

//   const handleSelectEvent = (event) => {
//     console.log("Selected event:", event);

//     setSelectedEvent(event);
//   };

//   const handleDeleteEvent = () => {
//     if (selectedEvent) {
//       setEvents((prevEvents) =>
//         prevEvents.filter((e) => e.id !== selectedEvent.id)
//       );
//       setSelectedEvent(null);
//     }
//   };

//   const handleDragEnd = (event) => {
//     const { active, over } = event;
//     if (!over) return;

//     const employee = employees.find((emp) => emp.id === active.id);
//     if (!employee) return;

//     const newStart = new Date(over.id);
//     const newEnd = moment(newStart).add(1, "hour").toDate();

//     const overlappingEvent = events.find(
//       (e) =>
//         moment(newStart).isBetween(e.start, e.end, null, "[)") ||
//         moment(newEnd).isBetween(e.start, e.end, null, "(]") ||
//         moment(e.start).isBetween(newStart, newEnd, null, "[)")
//     );

//     if (overlappingEvent) {
//       alert("This slot is already assigned!");
//       return;
//     }

//     const newEvent = {
//       id: new Date().getTime(),
//       title: employee.name,
//       start: newStart,
//       end: newEnd,
//       employeeId: employee.id,
//     };

//     setEvents((prevEvents) => [...prevEvents, newEvent]);
//   };

//   const assignedHours = events.reduce(
//     (acc, event) => acc + moment(event.end).diff(moment(event.start), "hours"),
//     0
//   );
//   const maxHours =
//     sites.find((site) => site.id === selectedSite)?.maxHours || 0;

//   return (
//     <div className="space-y-6 p-4">
//       <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
//         <h1 className="text-3xl font-bold">Scheduling</h1>
//         <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
//           <Select value={selectedSite} onValueChange={setSelectedSite}>
//             <SelectTrigger className="w-[180px]">
//               <SelectValue placeholder="Select a site" />
//             </SelectTrigger>
//             <SelectContent>
//               {sites.map((site) => (
//                 <SelectItem key={site.id} value={site.id}>
//                   {site.name}
//                 </SelectItem>
//               ))}
//             </SelectContent>
//           </Select>
//           <div className="flex gap-2">
//             <Button asChild>
//               <Link href="/open-shifts">Open Shifts</Link>
//             </Button>
//             <Button asChild variant="outline">
//               <Link href="/leave-management">Leave Management</Link>
//             </Button>
//           </div>
//         </div>
//       </div>

//       <Card className="mb-6">
//         <CardHeader>
//           <CardTitle>Assigned Hours</CardTitle>
//         </CardHeader>
//         <CardContent>
//           <div className="flex items-center justify-between mb-2">
//             <span>
//               {assignedHours} / {maxHours} hours
//             </span>
//             <span>
//               {maxHours ? ((assignedHours / maxHours) * 100).toFixed(1) : "0"}%
//             </span>
//           </div>
//           <Progress value={maxHours ? (assignedHours / maxHours) * 100 : 0} />
//         </CardContent>
//       </Card>

//       <DndContext onDragEnd={handleDragEnd}>
//         <div className="flex flex-col gap-4">
//           <div className=" flex-grow py-4">
//             <h2 className=" text-3xl font-semibold my-2">Employees</h2>
//             <div className=" w-max h-max flex flex-row gap-x-2">
//               {availableEmployees.map((employee) => (
//                 <DraggableEmployee key={employee.id} employee={employee} />
//               ))}
//             </div>
//           </div>

//           <div className="flex-grow">
//             <Calendar
//               localizer={localizer}
//               events={events}
//               startAccessor="start"
//               endAccessor="end"
//               selectable
//               views={[Views.WEEK, Views.DAY, Views.AGENDA]}
//               defaultView={Views.WEEK}
//               defaultDate={new Date()}
//               step={60}
//               timeslots={1}
//               min={new Date(new Date().setHours(9, 0, 0))}
//               max={new Date(new Date().setHours(17, 0, 0))}
//               onSelectSlot={handleSelectSlot}
//               onSelectEvent={handleSelectEvent}
//               style={{ height: "600" }}
//               components={{
//                 timeSlotWrapper: (props) => (
//                   <DroppableSlot date={props.value}>
//                     {props.children}
//                   </DroppableSlot>
//                 ),
//               }}
//             />
//           </div>
//           <div className="h-[100vh]">
//             <CustomCalender />
//           </div>
//         </div>
//       </DndContext>

//       {selectedEvent && (
//         <Dialog
//           open={Boolean(selectedEvent)}
//           onOpenChange={() => setSelectedEvent(null)}
//         >
//           <DialogContent>
//             <DialogHeader>
//               <DialogTitle>Event Details</DialogTitle>
//             </DialogHeader>
//             <div>
//               <p>
//                 <strong>Employee:</strong> {selectedEvent.title}
//               </p>
//               <p>
//                 <strong>Start:</strong>{" "}
//                 {moment(selectedEvent.start).format("LLL")}
//               </p>
//               <p>
//                 <strong>End:</strong> {moment(selectedEvent.end).format("LLL")}
//               </p>
//             </div>
//             <DialogFooter>
//               <Button variant="destructive" onClick={handleDeleteEvent}>
//                 Delete
//               </Button>
//               <Button onClick={() => setSelectedEvent(null)}>Close</Button>
//             </DialogFooter>
//           </DialogContent>
//         </Dialog>
//       )}
//     </div>
//   );
// }



"use client";
import { useState } from "react";
import moment from "moment";
import { Views } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { DndContext, useDraggable, useDroppable } from "@dnd-kit/core";
import Link from "next/link";
import CustomCalendar from "./_Calander"; // Make sure the path is correct

const employees = [
  { id: "1", name: "John Doe" },
  { id: "2", name: "Jane Smith" },
  { id: "3", name: "Mike Johnson" },
];

const sites = [
  { id: "site1", name: "Main Office Complex", maxHours: 160 },
  { id: "site2", name: "Warehouse Facility", maxHours: 120 },
  { id: "site3", name: "Retail Store", maxHours: 80 },
];

function DraggableEmployee({ employee }) {
  const { attributes, listeners, setNodeRef } = useDraggable({
    id: employee.id,
  });
  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className="p-2 bg-gray-200 rounded mb-2 cursor-grab"
    >
      {employee.name}
    </div>
  );
}

function DroppableSlot({ date, children }) {
  const { setNodeRef } = useDroppable({ id: date.toString() });
  return (
    <div ref={setNodeRef} className="h-full w-full">
      {children}
    </div>
  );
}

export default function SchedulingPage() {
  const [selectedSite, setSelectedSite] = useState("site1");
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [availableEmployees, setAvailableEmployees] = useState(employees);

  const handleSelectSlot = ({ start, end }) => {
    console.log("Selected slot:", start, end);

    const overlappingEvent = events.find((event) => {
      return (
        moment(start).isBetween(event.start, event.end, null, "[)") ||
        moment(end).isBetween(event.start, event.end, null, "(]") ||
        moment(event.start).isBetween(start, end, null, "[)")
      );
    });

    if (overlappingEvent) {
      const updatedEvents = events.map((event) => {
        if (event.id === overlappingEvent.id) {
          return {
            ...event,
            start,
            end,
          };
        }
        return event;
      });
      setEvents(updatedEvents);
    }
  };

  const handleSelectEvent = (event) => {
    console.log("Selected event:", event);
    setSelectedEvent(event);
  };

  const handleDeleteEvent = () => {
    if (selectedEvent) {
      setEvents((prevEvents) =>
        prevEvents.filter((e) => e.id !== selectedEvent.id)
      );
      setSelectedEvent(null);
    }
  };

  const handleDragEnd = (event) => {
    console.log('event', event);
    
    const { active, over } = event;
    if (!over) return;

    const employee = employees.find((emp) => emp.id === active.id);
    if (!employee) return;

    const newStart = new Date(over.id);
    const newEnd = moment(newStart).add(1, "hour").toDate();

    const overlappingEvent = events.find(
      (e) =>
        moment(newStart).isBetween(e.start, e.end, null, "[)") ||
        moment(newEnd).isBetween(e.start, e.end, null, "(]") ||
        moment(e.start).isBetween(newStart, newEnd, null, "[)")
    );

    if (overlappingEvent) {
      alert("This slot is already assigned!");
      return;
    }

    const newEvent = {
      id: new Date().getTime(),
      title: employee.name,
      start: newStart,
      end: newEnd,
      employeeId: employee.id,
    };

    setEvents((prevEvents) => [...prevEvents, newEvent]);
  };

  const assignedHours = events.reduce(
    (acc, event) => acc + moment(event.end).diff(moment(event.start), "hours"),
    0
  );
  const maxHours =
    sites.find((site) => site.id === selectedSite)?.maxHours || 0;

  const calendarComponents = {
    timeSlotWrapper: (props) => (
      <DroppableSlot date={props.value}>{props.children}</DroppableSlot>
    ),
  };

  return (
    <div className="space-y-6 p-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-3xl font-bold">Scheduling</h1>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <Select value={selectedSite} onValueChange={setSelectedSite}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select a site" />
            </SelectTrigger>
            <SelectContent>
              {sites.map((site) => (
                <SelectItem key={site.id} value={site.id}>
                  {site.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="flex gap-2">
            <Button asChild>
              <Link href="/open-shifts">Open Shifts</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/leave-management">Leave Management</Link>
            </Button>
          </div>
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Assigned Hours</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-2">
            <span>
              {assignedHours} / {maxHours} hours
            </span>
            <span>
              {maxHours ? ((assignedHours / maxHours) * 100).toFixed(1) : "0"}%
            </span>
          </div>
          <Progress value={maxHours ? (assignedHours / maxHours) * 100 : 0} />
        </CardContent>
      </Card>

      <DndContext onDragEnd={handleDragEnd}>
        <div className="flex flex-col gap-4">
          <div className="flex-grow py-4">
            <h2 className="text-3xl font-semibold my-2">Employees</h2>
            <div className="w-max h-max flex flex-row gap-x-2">
              {availableEmployees.map((employee) => (
                <DraggableEmployee key={employee.id} employee={employee} />
              ))}
            </div>
          </div>

          <div className="flex-grow">
            {/* Replace the existing Calendar with CustomCalendar */}
            <CustomCalendar
              events={events}
              onSelectSlot={handleSelectSlot}
              onSelectEvent={handleSelectEvent}
              components={calendarComponents}
              defaultView={Views.WEEK}
            />
          </div>
        </div>
      </DndContext>

      {selectedEvent && (
        <Dialog
          open={Boolean(selectedEvent)}
          onOpenChange={() => setSelectedEvent(null)}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Event Details</DialogTitle>
            </DialogHeader>
            <div>
              <p>
                <strong>Employee:</strong> {selectedEvent.title}
              </p>
              <p>
                <strong>Start:</strong>{" "}
                {moment(selectedEvent.start).format("LLL")}
              </p>
              <p>
                <strong>End:</strong> {moment(selectedEvent.end).format("LLL")}
              </p>
            </div>
            <DialogFooter>
              <Button variant="destructive" onClick={handleDeleteEvent}>
                Delete
              </Button>
              <Button onClick={() => setSelectedEvent(null)}>Close</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}