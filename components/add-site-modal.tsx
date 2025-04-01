"use client";

import type React from "react";
import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export function AddSiteModal() {
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [siteName, setSiteName] = useState("");
  const [address, setAddress] = useState("");
  const [description, setDescription] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [operatingHours, setOperatingHours] = useState("");
  const [securityLevel, setSecurityLevel] = useState("");
  const [maxHours, setMaxHours] = useState("");
  const [polygon, setPolygon] = useState([]);
  const mapRef = useRef(null);

  useEffect(() => {
    if (typeof window !== "undefined" && window.google && window.google.maps) {
      const initMap = () => {
        const map = new window.google.maps.Map(mapRef.current, {
          center: { lat: 19.076, lng: 72.8777 },
          zoom: 13,
        });

        const drawingManager = new window.google.maps.drawing.DrawingManager({
          drawingMode: window.google.maps.drawing.OverlayType.POLYGON,
          drawingControl: true,
          drawingControlOptions: {
            position: window.google.maps.ControlPosition.TOP_CENTER,
            drawingModes: [window.google.maps.drawing.OverlayType.POLYGON],
          },
        });

        drawingManager.setMap(map);

        window.google.maps.event.addListener(
          drawingManager,
          "overlaycomplete",
          function (event) {
            if (event.type === "polygon") {
              const path = event.overlay.getPath().getArray();
              const coordinates = path.map((latLng) => ({
                lat: latLng.lat(),
                lng: latLng.lng(),
              }));
              setPolygon(coordinates);
            }
          }
        );
      };

      initMap();
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const siteData = {
      name: siteName,
      address,
      description,
      assignedHours: maxHours,
      location: polygon,
    };

    try {
      const agencyId = localStorage.getItem("agencyId");
      if (!agencyId) throw new Error("Agency ID is missing in local storage.");

      const response = await fetch("https://securefrontbackend.onrender.com/v1/sites", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...siteData, agencyId }),
      });

      const responseData = await response.json();
      if (!response.ok) throw new Error(responseData.detail || "Failed to create site");

      return responseData;
    } catch (error) {
      console.error("Error creating site:", error);
      throw error;
    } finally {
      setOpen(false);
      resetForm();
    }
  };

  const resetForm = () => {
    setSiteName("");
    setAddress("");
    setDescription("");
    setContactName("");
    setContactEmail("");
    setContactPhone("");
    setOperatingHours("");
    setSecurityLevel("");
    setMaxHours("");
    setPolygon([]);
    setPage(1);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">Add New Site</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Add New Site</DialogTitle>
          <DialogDescription>
            Enter the details for the new site. Click next to set up the geo-fence.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          {page === 1 ? (
            <div className="grid gap-4 py-4">
              {/* Site form fields as before */}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="siteName" className="text-right">Site Name</Label>
                <Input id="siteName" value={siteName} onChange={(e) => setSiteName(e.target.value)} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="address" className="text-right">Address</Label>
                <Input id="address" value={address} onChange={(e) => setAddress(e.target.value)} className="col-span-3" />
              </div>
              {/* Additional inputs omitted for brevity... */}
            </div>
          ) : (
            <div className="py-4">
              <Label className="mb-2 block">Draw Geo-fence</Label>
              <div ref={mapRef} className="h-[400px] w-full rounded border" />
              <Button type="button" onClick={() => setPolygon([])} variant="outline" className="mt-4">
                Clear Fence
              </Button>
            </div>
          )}
          <DialogFooter>
            {page === 1 ? (
              <Button type="button" onClick={() => setPage(2)}>Next</Button>
            ) : (
              <>
                <Button type="button" variant="outline" onClick={() => setPage(1)}>
                  Previous
                </Button>
                <Button type="submit">Save Site</Button>
              </>
            )}
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
