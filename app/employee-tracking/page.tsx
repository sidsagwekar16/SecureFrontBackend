"use client"

import { useEffect, useState } from "react"
import dynamic from "next/dynamic"
import "leaflet/dist/leaflet.css"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// Dynamically import react-leaflet components (Fixes SSR issues)
const MapContainer = dynamic(() => import("react-leaflet").then((mod) => mod.MapContainer), { ssr: false })
const TileLayer = dynamic(() => import("react-leaflet").then((mod) => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import("react-leaflet").then((mod) => mod.Marker), { ssr: false })
const Popup = dynamic(() => import("react-leaflet").then((mod) => mod.Popup), { ssr: false })

// Employee locations (mock data)
const employeeLocations = [
  { id: 1, name: "John Doe", position: [51.505, -0.09] },
  { id: 2, name: "Jane Smith", position: [51.51, -0.1] },
  { id: 3, name: "Mike Johnson", position: [51.515, -0.095] },
]

export default function EmployeeTrackingPage() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true) // Prevents SSR issues by ensuring the map renders only on the client

    if (typeof window !== "undefined") {
      import("leaflet").then((L) => {
        delete L.Icon.Default.prototype._getIconUrl
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: "/leaflet/marker-icon-2x.png",
          iconUrl: "/leaflet/marker-icon.png",
          shadowUrl: "/leaflet/marker-shadow.png",
        })
      })
    }
  }, [])

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Employee Tracking</h1>
      <Card>
        <CardHeader>
          <CardTitle>Live Employee Locations</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="h-[calc(100vh-200px)]">
            {isClient && ( // Prevents server-side rendering errors
              <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: "100%", width: "100%" }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                {employeeLocations.map((employee) => (
                  <Marker key={employee.id} position={employee.position}>
                    <Popup>{employee.name}</Popup>
                  </Marker>
                ))}
              </MapContainer>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
