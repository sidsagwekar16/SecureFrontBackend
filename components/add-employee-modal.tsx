"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Employee {
  id: string
  name: string
  email: string
  phone: string
  dateOfBirth: string
  address: string
  role: string
  status: string
  employeeCode: string
  agencyId: string
  site: string
  emergencyContact: string
  emergencyPhone: string
  createdAt: string
  updatedAt: string
}

interface AddEmployeeModalProps {
  employeeData?: Employee
  type: "edit" | "add"
}

export function AddEmployeeModal({ employeeData, type }: AddEmployeeModalProps) {
  const [open, setOpen] = useState(false)

  const [formData, setFormData] = useState({
    name: "",
    employeeCode: "",
    role: "",
    status: "",
    site: "",
    email: "",
    phone: "",
    address: "",
    dateOfBirth: "",
    emergencyContact: "",
    emergencyPhone: "",
  })

  const [sites, setSites] = useState<{ id: string; name: string }[]>([])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const agencyId = localStorage.getItem("agencyId")
    if (!agencyId) {
      alert("Error: Agency ID is missing in local storage.")
      return
    }

    const requestData = {
      ...formData,
      agencyId,
      employeeCode: employeeData?.employeeCode,
    }

    try {
      let response
      let url = "https://securefrontbackend.onrender.com/web/employee/add"
      let method = "POST"

      if (type === "edit" && employeeData?.id) {
        url = `https://securefrontbackend.onrender.com/v1/employees/${employeeData.id}`
        method = "PATCH"
      }

      response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      })

      const responseData = await response.json()

      if (!response.ok) {
        console.error("Server Response:", responseData)
        throw new Error(
          responseData.message || responseData.detail || `Failed to ${type} employee`
        )
      }

      window.location.reload()

      if (type === "add") {
        setFormData({
          name: "",
          employeeCode: "",
          role: "",
          status: "",
          site: "",
          email: "",
          phone: "",
          address: "",
          dateOfBirth: "",
          emergencyContact: "",
          emergencyPhone: "",
        })
      }
    } catch (error: any) {
      console.error(`Error ${type}ing employee:`, error)
      alert(error.message || `Failed to ${type} employee. Please try again.`)
    }
  }

  useEffect(() => {
    if (type === "edit" && employeeData) {
      setFormData({
        name: employeeData.name || "",
        employeeCode: employeeData.employeeCode || "",
        role: employeeData.role || "",
        status: employeeData.status || "",
        site: employeeData.site || "",
        email: employeeData.email || "",
        phone: employeeData.phone || "",
        address: employeeData.address || "",
        dateOfBirth: employeeData.dateOfBirth || "",
        emergencyContact: employeeData.emergencyContact || "",
        emergencyPhone: employeeData.emergencyPhone || "",
      })
    }
  }, [employeeData, type])

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const agencyId = localStorage.getItem("agencyId")
        if (!agencyId) throw new Error("Missing agency ID")

        const res = await fetch(`https://securefrontbackend.onrender.com/v1/sites?agency_id=${agencyId}`)
        if (!res.ok) throw new Error("Failed to fetch sites")

        const data = await res.json()

        const siteOptions = data.map((site: any) => ({
          id: site.siteId,
          name: site.name,
        }))

        setSites(siteOptions)
      } catch (err) {
        console.error("Error fetching sites:", err)
      }
    }

    fetchSites()
  }, [])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="text-[.8rem] px-2 py-1 sm:text:3xl sm:p-3">
          {`${type === "edit" ? "Edit" : "Add"} Employee`}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] h-[95vh] overflow-scroll">
        <DialogHeader>
          <DialogTitle>{`${type === "edit" ? "Edit" : "Add"} New Employee`}</DialogTitle>
          <DialogDescription>
            Enter the details for the new employee. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* Name */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">Name</Label>
              <Input id="name" name="name" value={formData.name} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Employee Code */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="employeeCode" className="text-right">Employee Code</Label>
              <Input id="employeeCode" name="employeeCode" value={formData.employeeCode} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Role */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="role" className="text-right">Role</Label>
              <Input id="role" name="role" value={formData.role} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Status */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="status" className="text-right">Status</Label>
              <Select value={formData.status} onValueChange={(value) => handleSelectChange("status", value)}>
                <SelectTrigger id="status" className="col-span-3">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="on-leave">On Leave</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Site (Dynamic Dropdown) */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="site" className="text-right">Site</Label>
              <Select value={formData.site} onValueChange={(value) => handleSelectChange("site", value)}>
                <SelectTrigger id="site" className="col-span-3">
                  <SelectValue placeholder="Select site" />
                </SelectTrigger>
                <SelectContent>
                  {sites.map((site) => (
                    <SelectItem key={site.id} value={site.name}>
                      {site.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Email */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="email" className="text-right">Email</Label>
              <Input id="email" name="email" type="email" value={formData.email} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Phone */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="phone" className="text-right">Phone</Label>
              <Input id="phone" name="phone" type="tel" value={formData.phone} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Address */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="address" className="text-right">Address</Label>
              <Input id="address" name="address" value={formData.address} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* DOB */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="dateOfBirth" className="text-right">Date of Birth</Label>
              <Input id="dateOfBirth" name="dateOfBirth" type="date" value={formData.dateOfBirth} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Emergency Contact */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="emergencyContact" className="text-right">Emergency Contact</Label>
              <Input id="emergencyContact" name="emergencyContact" value={formData.emergencyContact} onChange={handleInputChange} className="col-span-3" />
            </div>

            {/* Emergency Phone */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="emergencyPhone" className="text-right">Emergency Phone</Label>
              <Input id="emergencyPhone" name="emergencyPhone" type="tel" value={formData.emergencyPhone} onChange={handleInputChange} className="col-span-3" />
            </div>
          </div>

          <DialogFooter>
            <Button type="submit">Save Employee</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
