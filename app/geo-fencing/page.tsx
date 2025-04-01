"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const DynamicMapComponent = dynamic(() => import("./MapComponent").then((mod) => mod.MapComponent), { ssr: false })

const sites = [
  { id: "site1", name: "Main Office Complex" },
  { id: "site2", name: "Warehouse Facility" },
  { id: "site3", name: "Retail Store" },
]

function PolygonCreator({ polygon, setPolygon }) {
  useMapEvents({
    click: (e) => {
      setPolygon([...polygon, [e.latlng.lat, e.latlng.lng]])
    },
  })
  return null
}

export default function GeoFencingPage() {
  const [selectedSite, setSelectedSite] = useState("")
  const [polygon, setPolygon] = useState([])
  const [isDrawing, setIsDrawing] = useState(false)

  const handleStartDrawing = () => {
    setIsDrawing(true)
    setPolygon([])
  }

  const handleFinishDrawing = () => setIsDrawing(false)

  const handleClearFence = () => setPolygon([])

  const handleSaveFence = () => {
    console.log("Saving fence for site:", selectedSite)
    console.log("Fence coordinates:", polygon)
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Geo-fencing</h1>
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center justify-between space-x-4">
            <Select value={selectedSite} onValueChange={setSelectedSite}>
              <SelectTrigger className="w-[200px]">
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
            <div className="space-x-2">
              <Button onClick={handleStartDrawing} disabled={isDrawing}>Start Drawing Fence</Button>
              <Button onClick={handleFinishDrawing} disabled={!isDrawing}>Finish Drawing</Button>
              <Button onClick={handleClearFence} variant="outline">Clear Fence</Button>
              <Button onClick={handleSaveFence} disabled={polygon.length < 3}>Save Fence</Button>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-0">
          <div className="h-[calc(100vh-250px)]">
            <DynamicMapComponent isDrawing={isDrawing} polygon={polygon} setPolygon={setPolygon} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}