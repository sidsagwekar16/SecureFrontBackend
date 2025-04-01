"use client";

import type React from "react";
import "@/styles/globals.css";
import { Inter } from "next/font/google";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/lib/store";
import "react-big-calendar/lib/css/react-big-calendar.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, initializeAuth } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [agencyID, setAgencyID] = useState<string | null>(null);

  // const id = localStorage.getItem("agencyID");
  useEffect(() => {
    initializeAuth();
    // setAgencyID(localStorage.getItem("agencyID"));
    setLoading(false);
  }, []);

  useEffect(() => {
    const id = localStorage.getItem("agencyID");
    setAgencyID(id);
  
    if (loading) return; // Prevent redirects before loading is false
  
    if (!id && pathname !== "/login" && pathname !== "/signup") {

      router.replace("/login");
    } else if (id && (pathname === "/login" || pathname === "/signup")) {
      router.replace("/");
    }
  }, [pathname, loading]);

  useEffect(() => {
    const handleStorageChange = () => {
      setAgencyID(localStorage.getItem("agencyID"));
    };

    window.addEventListener("storage", handleStorageChange);
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  if (loading) {
    return (
      <html lang="en" suppressHydrationWarning className="h-full min-h-screen">
        <body
          className={`${inter.className} antialiased h-full min-h-screen overflow-auto`}
        >
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <div className="flex items-center justify-center min-h-screen">
              <Skeleton>
                <div>Loading...</div>
              </Skeleton>
            </div>
          </ThemeProvider>
        </body>
      </html>
    );
  }

  return (
    <html lang="en" suppressHydrationWarning className="h-full min-h-screen">
      <body
        className={`${inter.className} antialiased h-full min-h-screen overflow-auto`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {agencyID ? (
            <SidebarProvider>
              <div className="flex min-h-screen w-full">
                <AppSidebar />
                <div className="flex-1 min-h-screen w-full overflow-auto">
                  {pathname !== "/login" ? (
                    <div className="px-4 py-6 lg:px-8">{children}</div>
                  ) : (
                    <Skeleton>
                      <div>Loading...</div>
                    </Skeleton>
                  )}
                </div>
              </div>
            </SidebarProvider>
          ) : (
            <div className="flex items-center justify-center min-h-screen">
              {children}
            </div>
          )}
        </ThemeProvider>
      </body>
    </html>
  );
}
