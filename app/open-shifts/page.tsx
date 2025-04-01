"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { toast } from "@/components/ui/use-toast"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const initialOpenShifts = [
  { id: 1, date: "2023-06-20", time: "09:00 - 17:00", site: "Main Office Complex", status: "Open" },
  { id: 2, date: "2023-06-21", time: "14:00 - 22:00", site: "Warehouse Facility", status: "Open" },
  { id: 3, date: "2023-06-22", time: "10:00 - 18:00", site: "Retail Store", status: "Assigned" },
]

const employees = [
  { id: 1, name: "John Doe" },
  { id: 2, name: "Jane Smith" },
  { id: 3, name: "Mike Johnson" },
]

export default function OpenShiftsPage() {
  const [openShifts, setOpenShifts] = useState(initialOpenShifts)
  const [newShift, setNewShift] = useState({ date: "", time: "", site: "" })
  const [selectedShift, setSelectedShift] = useState(null)
  const [selectedEmployee, setSelectedEmployee] = useState("")

  const handleCreateShift = (e) => {
    e.preventDefault()
    const newShiftEntry = {
      id: openShifts.length + 1,
      ...newShift,
      status: "Open",
    }
    setOpenShifts([...openShifts, newShiftEntry])
    setNewShift({ date: "", time: "", site: "" })
    toast({
      title: "Open Shift Created",
      description: "A new open shift has been created and added to the list.",
    })
  }

  const handleAssignShift = () => {
    if (selectedShift && selectedEmployee) {
      setOpenShifts(
        openShifts.map((shift) => (shift.id === selectedShift.id ? { ...shift, status: "Assigned" } : shift)),
      )
      toast({
        title: "Shift Assigned",
        description: `The shift has been assigned to ${selectedEmployee}.`,
      })
      setSelectedShift(null)
      setSelectedEmployee("")
    }
  }

  const handleBroadcastShift = (shiftId) => {
    toast({
      title: "Shift Broadcasted",
      description: "The open shift has been broadcasted to all available employees.",
    })
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Open Shifts Management</h1>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Create Open Shift</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Open Shift</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateShift} className="space-y-4">
              <div>
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={newShift.date}
                  onChange={(e) => setNewShift({ ...newShift, date: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="time">Time</Label>
                <Input
                  id="time"
                  placeholder="e.g., 09:00 - 17:00"
                  value={newShift.time}
                  onChange={(e) => setNewShift({ ...newShift, time: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="site">Site</Label>
                <Input
                  id="site"
                  placeholder="e.g., Main Office Complex"
                  value={newShift.site}
                  onChange={(e) => setNewShift({ ...newShift, site: e.target.value })}
                  required
                />
              </div>
              <Button type="submit">Create Shift</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Open Shifts</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Site</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {openShifts.map((shift) => (
                <TableRow key={shift.id}>
                  <TableCell>{shift.date}</TableCell>
                  <TableCell>{shift.time}</TableCell>
                  <TableCell>{shift.site}</TableCell>
                  <TableCell>
                    <Badge variant={shift.status === "Open" ? "secondary" : "success"}>{shift.status}</Badge>
                  </TableCell>
                  <TableCell>
                    {shift.status === "Open" && (
                      <>
                        <Button onClick={() => setSelectedShift(shift)} className="mr-2">
                          Assign
                        </Button>
                        <Button onClick={() => handleBroadcastShift(shift.id)} variant="outline">
                          Broadcast
                        </Button>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      {selectedShift && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Assign Shift</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-4">
              <div className="flex-grow">
                <Label htmlFor="employee">Select Employee</Label>
                <Select value={selectedEmployee} onValueChange={setSelectedEmployee}>
                  <SelectTrigger id="employee">
                    <SelectValue placeholder="Select an employee" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((employee) => (
                      <SelectItem key={employee.id} value={employee.name}>
                        {employee.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={handleAssignShift} disabled={!selectedEmployee}>
                Assign Shift
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

