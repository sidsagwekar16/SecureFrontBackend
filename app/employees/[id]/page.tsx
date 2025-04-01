"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { DialogClose } from "@/components/ui/dialog"

import Link from "next/link"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AddEmployeeModal } from "@/components/add-employee-modal";

export default function EmployeePage({ params }: { params: { id: string } }) {
  const [employee, setEmployee] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();
  
const handleDelete = async () => {
  try {
    const agencyId = localStorage.getItem("agencyId")
    if (!agencyId) throw new Error("Agency ID not found")

    const res = await fetch(
      `https://securefrontbackend.onrender.com/web/employee/${params.id}?agency_id=${agencyId}`,
      { method: "DELETE" }
    )

    if (!res.ok) throw new Error("Failed to delete employee")
    alert("Employee deleted successfully")
    router.push("/employees")
  } catch (error: any) {
    alert(error.message || "Error deleting employee")
  }
}

  useEffect(() => {
    const fetchEmployee = async () => {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(
          `https://securefrontbackend.onrender.com/v1/employees/${params.id}`
        );
        
        if (!response.ok) throw new Error(`Failed to fetch employee data...`);

        const data = await response.json();
        setEmployee(data);
      } catch (err: any) {
        setError(
          err.message || "An error occurred while fetching employee details."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchEmployee();
  }, [params.id]);

  if (loading) return <p>Loading employee details...</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!employee) return <p>No employee found.</p>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Employee Details</h1>  
        <div> 
        
<Dialog>
  <DialogTrigger asChild>
    <Button variant="destructive" className="mr-5">
      Delete Employee
    </Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Delete Employee</DialogTitle>
    </DialogHeader>

    <div className="py-2">
      <p>Are you sure you want to delete this employee? This action cannot be undone.</p>
    </div>

    <DialogFooter>
      <DialogClose asChild>
        <Button variant="ghost">Cancel</Button>
      </DialogClose>
      <Button
        variant="destructive"
        onClick={async () => {
          try {
            const agencyId = localStorage.getItem("agencyId")
            if (!agencyId) throw new Error("Agency ID is missing.")

            const res = await fetch(
              `https://securefrontbackend.onrender.com/v1/employees/${employee.id}`,
              { method: "DELETE" }
            )

            if (!res.ok) throw new Error("Failed to delete employee")

            
            router.push("/employees")
          } catch (error: any) {
            alert(error.message || "Something went wrong.")
          }
        }}
      >
        Confirm Delete
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

        {/* <Button onClick={() => router.push(`/employees/edit/${employee.id}`)}>Edit Employee</Button> */}
        <AddEmployeeModal employeeData={employee} type="edit" />
      </div>
       
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Employee Personal Info */}
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 mb-4">
              <Avatar className="w-20 h-20">
                <AvatarImage
                  src={`/placeholder-${employee.id}.jpg`}
                  alt={employee.name}
                />
                <AvatarFallback>
                  {employee.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="text-2xl font-bold">{employee.name}</h2>
                <p className="text-muted-foreground">{employee.role}</p>
                <Badge
                  variant={employee.status === "Active" ? "success" : "warning"}
                >
                  {employee.status}
                </Badge>
              </div>
            </div>
            <div className="space-y-2">
              <p>
                <strong>Email:</strong> {employee.email}
              </p>
              <p>
                <strong>Phone:</strong> {employee.phone}
              </p>
              <p>
                <strong>Address:</strong> {employee.address}
              </p>
              <p>
                <strong>Date of Birth:</strong> {employee.dateOfBirth}
              </p>
              <p>
                <strong>Emergency Contact:</strong> {employee.emergencyContact}{" "}
                ({employee.emergencyPhone})
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Activity Logs */}
        {/* <Card>
          <CardHeader>
            <CardTitle>Activity Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Activity</TableHead>
                  <TableHead>Duration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {employee.activityLogs?.length > 0 ? (
                  employee.activityLogs.map((log: any) => (
                    <TableRow key={log.id}>
                      <TableCell>{log.date}</TableCell>
                      <TableCell>{log.activity}</TableCell>
                      <TableCell>{log.duration}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center">
                      No activity logs available.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card> */}
      </div>
    </div>
  );
}
