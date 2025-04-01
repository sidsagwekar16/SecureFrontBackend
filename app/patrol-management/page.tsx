"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const initialPatrols = [
  {
    id: 1,
    name: "Night Patrol A",
    assignedTo: "John Doe",
    status: "In Progress",
    checkpoints: 5,
    lastCheckpoint: "Main Entrance",
  },
  {
    id: 2,
    name: "Day Patrol B",
    assignedTo: "Jane Smith",
    status: "Completed",
    checkpoints: 8,
    lastCheckpoint: "Parking Lot",
  },
  {
    id: 3,
    name: "Evening Patrol C",
    assignedTo: "Mike Johnson",
    status: "Scheduled",
    checkpoints: 6,
    lastCheckpoint: "N/A",
  },
]

export default function PatrolManagementPage() {
  const [patrols, setPatrols] = useState(initialPatrols)

  return (
    <div className="py-6">
      <h1 className="text-3xl font-bold mb-6">Patrol Management</h1>
      <div className="flex justify-between items-center mb-4">
        <Input placeholder="Search patrols..." className="max-w-sm" />
        <Button>Create New Patrol</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Active Patrols</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patrol Name</TableHead>
                <TableHead>Assigned To</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Checkpoints</TableHead>
                <TableHead>Last Checkpoint</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {patrols.map((patrol) => (
                <TableRow key={patrol.id}>
                  <TableCell>{patrol.name}</TableCell>
                  <TableCell>{patrol.assignedTo}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        patrol.status === "In Progress"
                          ? "default"
                          : patrol.status === "Completed"
                            ? "success"
                            : "secondary"
                      }
                    >
                      {patrol.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{patrol.checkpoints}</TableCell>
                  <TableCell>{patrol.lastCheckpoint}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">
                      View Details
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

