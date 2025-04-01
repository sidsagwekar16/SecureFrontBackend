"use client"

import { useState } from "react"
import {
  Home,
  Users,
  Briefcase,
  Calendar,
  PhoneCall,
  AlertCircle,
  BarChart2,
  Settings,
  Map,
  MapPin,
  Shield,
  UserPlus,
  Clock,
  FileText,
  Menu,
  Sun,
  Moon,
} from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { useTheme } from "next-themes"
import Link from "next/link"
import { usePathname } from "next/navigation"

const menuItems = [
  { href: "/", icon: Home, label: "Dashboard" },
  { href: "/employees", icon: Users, label: "Employees" },
  { href: "/sites", icon: Briefcase, label: "Sites" },
 // { href: "/scheduling", icon: Calendar, label: "Scheduling" },
  { href: "/communication", icon: PhoneCall, label: "Communication" },
  { href: "/incidents", icon: AlertCircle, label: "Incidents" },
  // { href: "/patrol-management", icon: Shield, label: "Patrol Management" },
  { href: "/reports", icon: BarChart2, label: "Analytics & KPIs" },
]

export function AppSidebar() {
  const [open, setOpen] = useState(false)
  const { setTheme, theme } = useTheme()
  const pathname = usePathname()

  const SidebarContents = () => (
    <>
      <SidebarHeader className="flex h-14 items-center border-b px-6">
        <span className="text-lg font-semibold">SecureFront</span>
      </SidebarHeader>
      <SidebarContent>
        <div className="space-y-4 py-4">
          <div className="px-3 py-2">
            <div className="space-y-1">
              <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight text-muted-foreground">Overview</h2>
              <SidebarMenu>
                {menuItems.map((item) => (
                  <SidebarMenuItem key={item.label} onClick={e=>setOpen(false)}>
                    <SidebarMenuButton asChild active={pathname === item.href}>
                      <Link href={item.href} prefetch className="group relative flex items-center">
                        <item.icon className="mr-2 h-4 w-4" />
                        <span>{item.label}</span>
                        {pathname === item.href && (
                          <span className="absolute inset-y-0 left-[-12px] w-1 rounded-r-lg bg-primary" />
                        )}
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </div>
          </div>
        </div>
      </SidebarContent>
      <div className="mt-auto border-t px-3 py-4">
        <div className="flex h-[40px] items-center justify-between px-4">
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 rounded-md"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            <span className="sr-only">Toggle theme</span>
          </Button>
          <Button variant="ghost" size="icon" className="h-9 w-9 rounded-md" asChild>
            <Link href="/settings">
              <Settings className="h-4 w-4" />
              <span className="sr-only">Settings</span>
            </Link>
          </Button>
        </div>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile Menu */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="md:hidden fixed top-4 left-4 z-40">
            <Menu className="h-6 w-6" />
            <span className="sr-only">Open menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="p-0 w-72">
          <SidebarContents />
        </SheetContent>
      </Sheet>

      {/* Desktop Sidebar */}
      <Sidebar className="hidden border-r md:block">
        <SidebarContents />
      </Sidebar>
    </>
  )
}

