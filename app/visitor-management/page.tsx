"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const initialVisitors = [
  {
    id: 1,
    name: "Alice Johnson",
    company: "Tech Corp",
    host: "John Doe",
    checkIn: "2023-06-15 09:30",
    checkOut: null,
    status: "Checked In",
  },
  {
    id: 2,
    name: "Bob Smith",
    company: "Marketing Inc",
    host: "Jane Smith",
    checkIn: "2023-06-15 10:15",
    checkOut: "2023-06-15 11:45",
    status: "Checked Out",
  },
  {
    id: 3,
    name: "Charlie Brown",
    company: "Sales Co",
    host: "Mike Johnson",
    checkIn: "2023-06-15 13:00",
    checkOut: null,
    status: "Checked In",
  },
]

export default function VisitorManagementPage() {
  const [visitors, setVisitors] = useState(initialVisitors)

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Visitor Management</h1>
      <div className="flex justify-between items-center mb-4">
        <Input placeholder="Search visitors..." className="max-w-sm" />
        <Button>Check In New Visitor</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Today's Visitors</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Visitor Name</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Host</TableHead>
                <TableHead>Check In</TableHead>
                <TableHead>Check Out</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {visitors.map((visitor) => (
                <TableRow key={visitor.id}>
                  <TableCell>{visitor.name}</TableCell>
                  <TableCell>{visitor.company}</TableCell>
                  <TableCell>{visitor.host}</TableCell>
                  <TableCell>{visitor.checkIn}</TableCell>
                  <TableCell>{visitor.checkOut || "-"}</TableCell>
                  <TableCell>
                    <Badge variant={visitor.status === "Checked In" ? "success" : "secondary"}>{visitor.status}</Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">
                      {visitor.status === "Checked In" ? "Check Out" : "View Details"}
                    </Button>
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

