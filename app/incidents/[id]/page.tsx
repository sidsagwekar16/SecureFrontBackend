"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

// This would typically come from an API call
const getIncidentDetails = (id: string) => {
  return {
    id,
    date: "2023-06-01",
    time: "14:30",
    description: "Unauthorized access attempt at the main entrance",
    site: "Main Office Complex",
    status: "Resolved",
    reportedBy: "John Doe",
    assignedTo: "Security Team A",
    resolution: "Identified as a misunderstanding. Visitor was expected but not properly registered.",
    actions: [
      { date: "2023-06-01 14:35", action: "Incident reported", by: "John Doe" },
      { date: "2023-06-01 14:40", action: "Security team dispatched", by: "Control Room" },
      { date: "2023-06-01 15:00", action: "Situation assessed", by: "Security Team A" },
      { date: "2023-06-01 15:30", action: "Incident resolved", by: "Security Team A" },
    ],
  }
}

export default function IncidentDetailsPage() {
  const params = useParams()
  const [incident, setIncident] = useState<any>(null)

  useEffect(() => {
    if (params.id) {
      const incidentDetails = getIncidentDetails(params.id as string)
      setIncident(incidentDetails)
    }
  }, [params.id])

  if (!incident) {
    return <div>Loading...</div>
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Incident Details</h1>
        <Button variant="outline">Edit Incident</Button>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Incident Information</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="font-semibold">Date</dt>
                <dd>{incident.date}</dd>
              </div>
              <div>
                <dt className="font-semibold">Time</dt>
                <dd>{incident.time}</dd>
              </div>
              <div className="col-span-2">
                <dt className="font-semibold">Description</dt>
                <dd>{incident.description}</dd>
              </div>
              <div>
                <dt className="font-semibold">Site</dt>
                <dd>{incident.site}</dd>
              </div>
              <div>
                <dt className="font-semibold">Status</dt>
                <dd>
                  <Badge variant={incident.status === "Resolved" ? "success" : "warning"}>{incident.status}</Badge>
                </dd>
              </div>
              <div>
                <dt className="font-semibold">Reported By</dt>
                <dd>{incident.reportedBy}</dd>
              </div>
              <div>
                <dt className="font-semibold">Assigned To</dt>
                <dd>{incident.assignedTo}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Resolution</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{incident.resolution}</p>
          </CardContent>
        </Card>
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Action Log</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {incident.actions.map((action: any, index: number) => (
                <li key={index} className="border-b pb-2 last:border-b-0">
                  <p className="font-semibold">{action.date}</p>
                  <p>{action.action}</p>
                  <p className="text-sm text-muted-foreground">By: {action.by}</p>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

