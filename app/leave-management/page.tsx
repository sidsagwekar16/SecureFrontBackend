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
import { Textarea } from "@/components/ui/textarea"

const initialLeaveRequests = [
  {
    id: 1,
    employee: "John Doe",
    startDate: "2023-07-01",
    endDate: "2023-07-05",
    reason: "Vacation",
    status: "Pending",
  },
  {
    id: 2,
    employee: "Jane Smith",
    startDate: "2023-07-10",
    endDate: "2023-07-12",
    reason: "Personal",
    status: "Approved",
  },
  {
    id: 3,
    employee: "Mike Johnson",
    startDate: "2023-07-15",
    endDate: "2023-07-16",
    reason: "Sick Leave",
    status: "Pending",
  },
]

export default function LeaveManagementPage() {
  const [leaveRequests, setLeaveRequests] = useState(initialLeaveRequests)
  const [newLeave, setNewLeave] = useState({ employee: "", startDate: "", endDate: "", reason: "" })

  const handleApproveLeave = (leaveId) => {
    setLeaveRequests(leaveRequests.map((leave) => (leave.id === leaveId ? { ...leave, status: "Approved" } : leave)))
    toast({
      title: "Leave Approved",
      description: "The leave request has been approved.",
    })
  }

  const handleRejectLeave = (leaveId) => {
    setLeaveRequests(leaveRequests.map((leave) => (leave.id === leaveId ? { ...leave, status: "Rejected" } : leave)))
    toast({
      title: "Leave Rejected",
      description: "The leave request has been rejected.",
    })
  }

  const handleSubmitNewLeave = (e) => {
    e.preventDefault()
    const newLeaveRequest = {
      id: leaveRequests.length + 1,
      ...newLeave,
      status: "Pending",
    }
    setLeaveRequests([...leaveRequests, newLeaveRequest])
    setNewLeave({ employee: "", startDate: "", endDate: "", reason: "" })
    toast({
      title: "Leave Request Submitted",
      description: "Your leave request has been submitted for approval.",
    })
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Leave Management</h1>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Request Leave</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Request Leave</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmitNewLeave} className="space-y-4">
              <div>
                <Label htmlFor="employee">Employee Name</Label>
                <Input
                  id="employee"
                  value={newLeave.employee}
                  onChange={(e) => setNewLeave({ ...newLeave, employee: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={newLeave.startDate}
                  onChange={(e) => setNewLeave({ ...newLeave, startDate: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="endDate">End Date</Label>
                <Input
                  id="endDate"
                  type="date"
                  value={newLeave.endDate}
                  onChange={(e) => setNewLeave({ ...newLeave, endDate: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="reason">Reason</Label>
                <Textarea
                  id="reason"
                  value={newLeave.reason}
                  onChange={(e) => setNewLeave({ ...newLeave, reason: e.target.value })}
                  required
                />
              </div>
              <Button type="submit">Submit Request</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Leave Requests</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leaveRequests.map((leave) => (
                <TableRow key={leave.id}>
                  <TableCell>{leave.employee}</TableCell>
                  <TableCell>{leave.startDate}</TableCell>
                  <TableCell>{leave.endDate}</TableCell>
                  <TableCell>{leave.reason}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        leave.status === "Approved"
                          ? "success"
                          : leave.status === "Rejected"
                            ? "destructive"
                            : "secondary"
                      }
                    >
                      {leave.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {leave.status === "Pending" && (
                      <>
                        <Button onClick={() => handleApproveLeave(leave.id)} className="mr-2">
                          Approve
                        </Button>
                        <Button onClick={() => handleRejectLeave(leave.id)} variant="destructive">
                          Reject
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
    </div>
  )
}

