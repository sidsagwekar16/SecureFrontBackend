"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "@/components/ui/use-toast";
import { CustomSelect } from "./_CustomSelect";

export default function CommunicationPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<any | null>(null);
  const [message, setMessage] = useState("");
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // NEW: sites & selectedSite states
  const [sites, setSites] = useState<any[]>([]);
  const [selectedSite, setSelectedSite] = useState("");

  useEffect(() => {
    // Fetch employees and sites when component mounts
    fetchEmployees();
    fetchSites();
  }, []);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const agencyId = localStorage.getItem("agencyId");
      if (!agencyId) {
        throw new Error("Agency ID not found in local storage");
      }
      const response = await fetch(
        `https://securefrontbackend.onrender.com/web/employee/all?agency_id=${agencyId}`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch employees");
      }
      const data = await response.json();
      setEmployees(data);
    } catch (error) {
      console.error("Error fetching employees:", error);
      toast({
        title: "Error",
        description: "Failed to load employees.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // NEW: fetch sites for the dropdown
  const fetchSites = async () => {
    try {
      const agencyId = localStorage.getItem("agencyId");
      if (!agencyId) {
        throw new Error("Agency ID not found in local storage");
      }
      const response = await fetch(
        `https://securefrontbackend.onrender.com/v1/sites?agency_id=${agencyId}`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch sites");
      }
      const data = await response.json();
      setSites(data);
    } catch (error) {
      console.error("Error fetching sites:", error);
      toast({
        title: "Error",
        description: "Failed to load sites.",
        variant: "destructive",
      });
    }
  };

  const handleCall = (e: React.MouseEvent, phone: string) => {
    e.preventDefault();
    window.location.href = `tel:${phone}`;
  };

  const handleSendSMS = () => {
    if (!selectedEmployee) return;
    toast({
      title: "SMS Sent",
      description: `Message sent to ${selectedEmployee.name} at ${selectedEmployee.phone}`,
    });
    setMessage("");
  };

  // UPDATED: Mention selectedSite in the toast (no functional change, just more info)
  // const handleBroadcast = () => {
  //   toast({
  //     title: "Broadcast Sent",
  //     description: selectedSite
  //       ? `Message broadcasted to site ID: ${selectedSite}`
  //       : "No site selected.",
  //   });
  //   setBroadcastMessage("");
  // };

  const handleBroadcast = async () => {
    if (!broadcastMessage || !selectedSite) {
      toast({
        title: "Error",
        description: "Please select a site and enter a message",
        variant: "destructive",
      });
      return;
    }
  
    try {
      setLoading(true);
      const agencyId = localStorage.getItem("agencyId");
      const authToken = localStorage.getItem("token"); // Assuming you store the auth token in localStorage
  
      if (!agencyId) {
        throw new Error("Agency ID not found in local storage");
      }
  
      if (!authToken) {
        throw new Error("Authorization token not found");
      }
  
      const response = await fetch(
        `https://securefrontbackend.onrender.com/v1/messages/broadcast?agency_id=${agencyId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "authorization": authToken,
          },
          body: JSON.stringify({
            siteId: selectedSite,
            text: broadcastMessage,
          }),
        }
      );
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to send broadcast message");
      }
  
      toast({
        title: "Success",
        description: `Message broadcasted to site ID: ${selectedSite}`,
      });
      setBroadcastMessage("");
    } catch (error) {
      console.error("Error sending broadcast message:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send broadcast message",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const siteOptions = [
    { value: "", label: "-- Choose a Site --" },
    ...sites.map((site) => ({
      value: site.siteId,
      label: site.name,
    })),
  ];

  return (
    <div className="py-6">
      <h1 className="text-3xl font-bold mb-6">Communication</h1>
      <div className="grid gap-6 md:grid-cols-2">
        {/* Employee List */}
        <Card className="max-h-[50vh] overflow-y-scroll">
          <CardHeader>
            <CardTitle>Employee List</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading employees...</p>
            ) : employees.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {employees.map((employee) => (
                    <TableRow key={employee.id}>
                      <TableCell>{employee.name}</TableCell>
                      <TableCell>{employee.phone}</TableCell>
                      <TableCell>
                        <Button onClick={() => setSelectedEmployee(employee)}>
                          Select
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p>No employees found.</p>
            )}
          </CardContent>
        </Card>

        {/* Communication Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Communication Panel</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedEmployee ? (
              <div className="space-y-4">
                <div>
                  <strong>Selected Employee:</strong> {selectedEmployee.name}
                </div>
                <div>
                  <strong>Phone:</strong> {selectedEmployee.phone}
                </div>
                <div className="space-x-2">
                  <Button
                    onClick={(e) => handleCall(e, selectedEmployee.phone)}
                  >
                    Call
                  </Button>
                  {/*
                  <Button onClick={handleSendSMS} disabled={!message}>
                    Send SMS
                  </Button>
                  */}
                </div>
                <Textarea
                  placeholder="Type your message here..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                />
              </div>
            ) : (
              <div>Please select an employee from the list.</div>
            )}
          </CardContent>
        </Card>

        {/* Broadcast Message */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Broadcast Message</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* NEW: Site dropdown */}
              <CustomSelect
                label="Select Site:"
                options={siteOptions}
                value={selectedSite === "" ? "_empty_" : selectedSite}
                onValueChange={setSelectedSite}
                placeholder="-- Choose a Site --"
                className="mb-4 w-max"
              />
              <Textarea
                placeholder="Type your broadcast message here..."
                value={broadcastMessage}
                onChange={(e) => setBroadcastMessage(e.target.value)}
              />
              <Button onClick={handleBroadcast} disabled={!broadcastMessage}>
                Send Broadcast
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
