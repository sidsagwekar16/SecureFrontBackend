"use client"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import Link from "next/link"
import { AddEmployeeModal } from "@/components/add-employee-modal"

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([])
  const [filteredEmployees, setFilteredEmployees] = useState<any[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedSite, setSelectedSite] = useState("all")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [sites, setSites] = useState<{ id: string; name: string }[]>([
    { id: "all", name: "All Sites" },
  ])

  // Fetch employees
  useEffect(() => {
    const fetchEmployees = async () => {
      setLoading(true)
      setError("")

      try {
        const agencyId = localStorage.getItem("agencyId")
        if (!agencyId) throw new Error("Missing agency ID in localStorage")

        const response = await fetch(
          `https://securefrontbackend.onrender.com/web/employee/all?agency_id=${agencyId}`
        )
        if (!response.ok) throw new Error("Failed to fetch employees")

        const data = await response.json()
        setEmployees(data.length > 0 ? data : [])
        setFilteredEmployees(data.length > 0 ? data : [])
      } catch (err: any) {
        setError(err.message || "An error occurred while fetching employees.")
      } finally {
        setLoading(false)
      }
    }

    fetchEmployees()
  }, [])

  // Fetch sites for dropdown
  useEffect(() => {
    const fetchSites = async () => {
      try {
        const agencyId = localStorage.getItem("agencyId")
        if (!agencyId) throw new Error("Missing agency ID")

        const res = await fetch(
          `https://securefrontbackend.onrender.com/v1/sites?agency_id=${agencyId}`
        )
        if (!res.ok) throw new Error("Failed to fetch sites")

        const data = await res.json()

        const siteOptions = data.map((site: any) => ({
          id: site.siteId,
          name: site.name,
        }))

        setSites([{ id: "all", name: "All Sites" }, ...siteOptions])
      } catch (err) {
        console.error("Error fetching sites:", err)
      }
    }

    fetchSites()
  }, [])

  // Filter logic
  useEffect(() => {
    let filtered = employees.filter(
      (employee) =>
        employee.name.toLowerCase().includes(searchTerm) ||
        employee.role.toLowerCase().includes(searchTerm)
    )

    if (selectedSite !== "all") {
      const selectedSiteName = sites.find((s) => s.id === selectedSite)?.name
      filtered = filtered.filter((employee) => employee.site === selectedSiteName)
    }

    setFilteredEmployees(filtered)
  }, [searchTerm, selectedSite, employees, sites])

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Employees</h1>
        <AddEmployeeModal type="add" />
      </div>

      <div className="flex justify-between items-center mb-4">
        <Input
          placeholder="Search employees..."
          className="max-w-sm"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value.toLowerCase())}
        />
        <Select value={selectedSite} onValueChange={(siteId) => setSelectedSite(siteId)}>
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
      </div>

      {loading ? (
        <p>Loading employees...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : filteredEmployees.length === 0 ? (
        <p>No employee data available for the selected site.</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Site</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredEmployees.map((employee) => (
              <TableRow key={employee.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center">
                    <Avatar className="mr-2">
                      <AvatarImage src={`/placeholder-${employee.id}.jpg`} alt={employee.name} />
                      <AvatarFallback>
                        {employee.name
                          .split(" ")
                          .map((n: any) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                    {employee.name}
                  </div>
                </TableCell>
                <TableCell>{employee.role}</TableCell>
                <TableCell>{employee.status}</TableCell>
                <TableCell>{employee.site}</TableCell>
                <TableCell>
                <Link
                             href={`/employees/${employee.id}`}
                              className="text-blue-600 hover:underline"
                                >
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
