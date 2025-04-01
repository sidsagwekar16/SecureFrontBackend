"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"


// TypeScript interfaces for API data
interface Site {
  id: string
  siteId: string
  agencyId: string
  name: string
  description: string
  address: string
  assignedHours: number
  location: {
    additionalProp1: number
    additionalProp2: number
    additionalProp3: number
  }
  createdAt: string
  updatedAt: string
}

interface Guard {
  id: string
  name: string
  shift: string
}

interface Incident {
  id: string
  date: string
  description: string
  status: string
}

export default function SitePage({ params }: { params: { id: string } }) {
  const [site, setSite] = useState<Site | null>(null)
  const [guards, setGuards] = useState<Guard[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    fetchSiteData()
  }, [])

  const fetchSiteData = async () => {
    try {
      const agencyId = localStorage.getItem("agencyId")
      if (!agencyId) throw new Error("Agency ID is missing in local storage.")

      const siteRes = await fetch(`https://securefrontbackend.onrender.com/v1/sites/${params.id}?agency_id=${agencyId}`)
      if (!siteRes.ok) throw new Error("Failed to fetch site details")
      const siteData: Site = await siteRes.json()
      setSite(siteData)

      const guardsRes = await fetch(`https://securefrontbackend.onrender.com/v1/sites/${params.id}/guards`)
      if (!guardsRes.ok) throw new Error("Failed to fetch assigned guards")
      const guardsData: Guard[] = await guardsRes.json()
      setGuards(guardsData)

      const incidentsRes = await fetch(`https://securefrontbackend.onrender.com/v1/sites/${params.id}/incidents`)
      if (!incidentsRes.ok) throw new Error("Failed to fetch incidents")
      const incidentsData: Incident[] = await incidentsRes.json()
      setIncidents(incidentsData)

      setLoading(false)
    } catch (err: any) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) return <p>Loading site details...</p>

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Site Overview</h1>
        <Button onClick={() => router.push(`/sites/edit/${site?.siteId ?? "#"}`)}>Edit Site</Button>
      </div>

      {/* Site Information */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Site Information</CardTitle>
          </CardHeader>
          <CardContent>
            <h2 className="text-2xl font-bold mb-2">{site?.name ?? "N/A"}</h2>
            {/*
            <Badge variant={site?.status === "Active" ? "success" : "warning"} className="mb-4">
              {site?.status ?? "N/A"}
            </Badge> */}
            <div className="space-y-2">
              <p><strong>Address:</strong> {site?.address ?? "N/A"}</p>
              <p><strong>Assigned Hours:</strong> {site?.assignedHours ?? "N/A"}</p>
              
            </div>
          </CardContent>
        </Card>

        {/* Assigned Guards 
        <Card>
          <CardHeader>
            <CardTitle>Assigned Guards</CardTitle>
          </CardHeader>
          <CardContent>
            {guards.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Shift</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {guards.map((guard) => (
                    <TableRow key={guard.id}>
                      <TableCell>
                        <div className="flex items-center">
                          <Avatar className="mr-2">
                            <AvatarImage src={`/placeholder-${guard.id}.jpg`} alt={guard.name} />
                            <AvatarFallback>
                              {guard.name ? guard.name.split(" ").map((n) => n[0]).join("") : "NA"}
                            </AvatarFallback>
                          </Avatar>
                          {guard.name ?? "N/A"}
                        </div>
                      </TableCell>
                      <TableCell>{guard.shift ?? "N/A"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p>No assigned guards.</p>
            )}
          </CardContent>
        </Card>
        */}

        {/* Recent Incidents 
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Incidents</CardTitle>
          </CardHeader>
          <CardContent>
            {incidents.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {incidents.map((incident) => (
                    <TableRow key={incident.id}>
                      <TableCell>{incident.date ?? "N/A"}</TableCell>
                      <TableCell>{incident.description ?? "N/A"}</TableCell>
                      <TableCell>
                        <Badge variant={incident.status === "Resolved" ? "success" : "warning"}>
                          {incident.status ?? "N/A"}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p>No recent incidents.</p>
            )}
          </CardContent>
        </Card>
        */}
      </div>
    </div>
  )
}
