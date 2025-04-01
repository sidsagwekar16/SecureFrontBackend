"use client"
import { MapContainer, TileLayer, Polygon, useMapEvents } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import L from "leaflet"
import { useEffect } from "react"

export function MapComponent({ isDrawing, polygon, setPolygon }) {
  useEffect(() => {
    if (typeof window !== "undefined" && L) {
      delete L.Icon.Default.prototype._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "/leaflet/marker-icon-2x.png",
        iconUrl: "/leaflet/marker-icon.png",
        shadowUrl: "/leaflet/marker-shadow.png",
      })
    }
  }, [])

  return (
    <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: "100%", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {isDrawing && <PolygonCreator polygon={polygon} setPolygon={setPolygon} />}
      {polygon.length > 0 && <Polygon positions={polygon} />}
    </MapContainer>
  )
}
