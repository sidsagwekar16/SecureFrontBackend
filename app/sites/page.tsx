"use client"


import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { AddSiteModal } from "@/components/add-site-modal" // Import the modal

// Define the Site Type
interface Site {
  siteId: string
  agencyId: string
  name: string
  description: string
  address: string
  assignedHours: number
  location: {
    latitude: number
    longitude: number
  }
  createdAt: string
  updatedAt: string
}

export default function SitesPage() {
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
    fetchSites()
  }, [])

  const fetchSites = async () => {
    try {
      const agencyId = localStorage.getItem("agencyId")

      if (!agencyId) {
        throw new Error("Agency ID is missing in local storage.")
      }

      const response = await fetch(`https://securefrontbackend.onrender.com/v1/sites?agency_id=${agencyId}`)
      if (!response.ok) {
        throw new Error("Failed to fetch sites")
      }

      const data: Site[] = await response.json()
      setSites(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isClient) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-3xl font-bold">Sites</h1>
        <div className="flex gap-2 w-full sm:w-auto">
          <Button asChild variant="outline">
            <Link href="/geo-fencing">Geo-fencing</Link>
          </Button>
          {/* Replace the Link-based button with the modal trigger */}
          <AddSiteModal />
        </div>
      </div>

      {/* Search Input */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Input
          placeholder="Search sites..."
          className="w-full sm:max-w-sm"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Loading and Error Handling */}
      {loading ? (
        <p>Loading sites...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Address</TableHead>
              <TableHead>Hours</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sites
              .filter((site) => site.name.toLowerCase().includes(search.toLowerCase()))
              .map((site) => (
                <TableRow key={site.siteId}>
                  <TableCell className="font-medium">{site.name}</TableCell>
                  <TableCell>{site.address}</TableCell>
                  <TableCell className="font-medium">{site.assignedHours}</TableCell>
                  <TableCell>
                    <Link href={`/sites/${site.id}`} className="text-blue-600 hover:underline">
                      View
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
 