"use client";

import { useState, useEffect, useLayoutEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Users, AlertCircle, Shield, UserPlus } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MapWrapper } from "@/components/map-wrapper";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";

const siteLocations = {
  "Main Office Complex": { lat: 51.505, lng: -0.09 },
  "Warehouse Facility": { lat: 51.51, lng: -0.1 },
  "Retail Store": { lat: 51.515, lng: -0.095 },
};

export default function DashboardPage() {
  const router = useRouter();
  const [selectedSite, setSelectedSite] = useState("all");
  const [sites, setSites] = useState([]);
  const [isAuth, setIsAuth] = useState(null);
  const agencyId = localStorage.getItem("agencyId");

  useLayoutEffect(() => {
    setIsAuth(!!agencyId);
  }, []);

  useEffect(() => {
    const fetchSites = async () => {
      // Use optional chaining

      if (!agencyId) {
        console.warn("No agency ID found in local storage.");
        router.replace("/login");
        return;
      }

      try {
        const response = await fetch(
          `https://securefrontbackend.onrender.com/v1/sites?agency_id=${agencyId}`
        );
        if (!response.ok) throw new Error("Failed to fetch sites");

        const data = await response.json();

        if (data.length === 0) {
          console.warn("No sites found for this agency.");
        }

        const formattedSites = [
          { id: "all", name: "All Sites" },
          ...data.map((site) => ({ id: site.siteId, name: site.name })),
        ];

        setSites(formattedSites);
      } catch (error) {
        console.error("Error fetching sites:", error);
      }
    };

    fetchSites();
  }, []);

  const getMetrics = (siteId) => {
    if (siteId === "all") {
      return {
        personnel: 0,
        personnelChange: "+5 this week",
        patrols:0,
        patrolsChange: "2 more than yesterday",
        incidents: 0,
        incidentsChange: "-3 from last month",
        visitors: 0,
        visitorsChange: "+5 from yesterday",
      };
    }

    const siteMetrics = {
      1: {
        personnel: 0,
        personnelChange: "+2 this week",
        patrols: 0,
        patrolsChange: "1 more than yesterday",
        incidents: 0,
        incidentsChange: "-1 from last month",
        visitors: 0,
        visitorsChange: "+2 from yesterday",
      },
    };

    return siteMetrics[siteId] || siteMetrics[1];
  };

  const metrics = getMetrics(selectedSite);

  const mapMarkers = Object.entries(siteLocations).map(([name, position]) => ({
    name,
    position: [position.lat, position.lng],
  }));

  const handleNavigation = (e) => {
    e.preventDefault();
    const siteName = sites.find((site) => site.id == selectedSite);
    router.push(`/incidents?site=${siteName?.name}`);
  };

  const handleLogout = () => {
    localStorage.clear(); // Clears all items from localStorage
    setTimeout(() => {
      router.push("/login");
    }, 1000); // Redirects to login page after 1 second
  };

  if (isAuth) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-y-3 sm:flex sm:flex-row items-center justify-between space-x-4">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Dashboard
          </h1>
          <div className="flex items-center space-x-4">
            <Select value={selectedSite} onValueChange={setSelectedSite}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select site" />
              </SelectTrigger>
              <SelectContent>
                {sites.map((site) => (
                  <SelectItem key={site.id} value={site?.id?.toString()}>
                    {site.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                  <Avatar>
                    <AvatarImage src="/placeholder-user.jpg" alt="User" />
                    <AvatarFallback>SF</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link href="/settings">Settings</Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleLogout}>
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
              Attendance
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.personnel}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.personnelChange}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Alerts
              </CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.patrols}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.patrolsChange}
              </p>
            </CardContent>
          </Card>

          <Card
            onClick={(e) => handleNavigation(e)}
            className=" cursor-pointer"
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Reports
              </CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.incidents}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.incidentsChange}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Sites
              </CardTitle>
              <UserPlus className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.visitors}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.visitorsChange}
              </p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Live Map</CardTitle>
          </CardHeader>
          {/*
          <CardContent className="p-0 aspect-[2/1]">
            <div className="h-[70vh] sm:h-full w-full overflow-hidden">
              <MapWrapper center={[51.505, -0.09]} markers={mapMarkers} />
            </div>
          </CardContent>
          */}
        </Card>
      </div>
    );
  } else {
    return (
      <Skeleton>
        <div>Loading....</div>
      </Skeleton>
    );
  }
}
