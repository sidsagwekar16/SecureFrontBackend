"use client"

import { useEffect, useState } from "react"
import dynamic from "next/dynamic"

const MapComponent = dynamic(() => import("./map-component"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-muted animate-pulse rounded-lg flex items-center justify-center">
      Loading map...
    </div>
  ),
})

export function MapWrapper({ center, markers }: { center: [number, number]; markers: any[] }) {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) return null

  return <MapComponent center={center} markers={markers} />
}

