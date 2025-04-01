"use client";

import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

export default function IncidentsPage() {
  const [selectedSite, setSelectedSite] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [incidents, setIncidents] = useState([]);
  const [filteredIncidents, setFilteredIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sites, setSites] = useState([]); // 🛠 Fixed: Corrected state name from `site` to `sites`
  const router = useRouter();

  useEffect(() => {
    if (typeof window === "undefined") return;
    
    const agencyId = localStorage.getItem("agencyId");
    if (!agencyId) {
      router.replace("/login");
      return;
    }

    async function fetchIncidents() {
      try {
        const response = await fetch(`https://securefrontbackend.onrender.com/v1/incidents?agency_id=${agencyId}`);
        if (!response.ok) throw new Error("Failed to fetch incidents");
        const data = await response.json();
        setIncidents(data);
        setFilteredIncidents(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchIncidents();
  }, []);

  useEffect(() => {
    const filtered = incidents.filter((incident) => {
      const matchesSite = selectedSite === "all" || incident.siteId === selectedSite;
      const matchesSearch = incident.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSite && matchesSearch;
    });

    setFilteredIncidents(filtered);
  }, [selectedSite, searchQuery, incidents]);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <IncidentsContent
        selectedSite={selectedSite}
        setSelectedSite={setSelectedSite}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        filteredIncidents={filteredIncidents}
        loading={loading}
        error={error}
        sites={sites} // 🛠 Fixed: Pass `sites` as a prop
        setSites={setSites} // 🛠 Fixed: Pass `setSites` as a prop
      />
    </Suspense>
  );
}

function IncidentsContent({
  selectedSite,
  setSelectedSite,
  searchQuery,
  setSearchQuery,
  filteredIncidents,
  loading,
  error,
  sites,
  setSites,
}) {
  const searchParams = useSearchParams();

  useEffect(() => {
    const siteParam = searchParams.get("site");
    if (siteParam) {
      const matchingSite = sites.find((site) => site.name === siteParam);
      setSelectedSite(matchingSite ? matchingSite.id : "all");
    }
  }, [searchParams, sites]); // 🛠 Fixed: Added `sites` as a dependency

  useEffect(() => {
    const fetchSites = async () => {
      if (typeof window === "undefined") return;
      const agencyId = localStorage.getItem("agencyId");
      if (!agencyId) return;

      try {
        const response = await fetch(`https://securefrontbackend.onrender.com/v1/sites?agency_id=${agencyId}`);
        if (!response.ok) throw new Error("Failed to fetch sites");

        const data = await response.json();
        const formattedSites = [{ id: "all", name: "All Sites" }, ...data.map((site) => ({ id: site.siteId, name: site.name }))];
        setSites(formattedSites);
      } catch (error) {
        console.error("Error fetching sites:", error);
      }
    };

    fetchSites();
  }, [setSites]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Incidents</h1>
       
      </div>

      <div className="flex justify-between items-center mb-4">
        <Input
          placeholder="Search incidents..."
          className="max-w-sm"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Select value={selectedSite} onValueChange={setSelectedSite}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select a site" />
          </SelectTrigger>
          <SelectContent>
            {sites.length > 0 ? (
              sites.map((site) => (
                <SelectItem key={site.id} value={site.id}>
                  {site.name}
                </SelectItem>
              ))
            ) : (
              <SelectItem disabled>No Sites Available</SelectItem>
            )}
          </SelectContent>
        </Select>
      </div>

      {loading && <div>Loading incidents...</div>}
      {error && <div className="text-red-500">Error: {error}</div>}

      {!loading && !error && (
        <div className="overflow-y-auto max-h-full">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Site</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredIncidents.length > 0 ? (
                filteredIncidents.map((incident) => (
                  <TableRow key={incident.incidentId}>
                    <TableCell>{new Date(incident.timestamp).toLocaleDateString()}</TableCell>
                    <TableCell>{incident.description}</TableCell>
                    <TableCell>
                      {sites.find((site) => site.id === incident.siteId)?.name || "Unknown"}
                    </TableCell>
                    <TableCell>
                      <Badge variant={incident.status === "Resolved" ? "success" : "warning"}>
                        {incident.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Link href={`/incidents/${incident.incidentId}`}>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center">
                    No incidents found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
