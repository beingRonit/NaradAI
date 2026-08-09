import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import AgentationToolbar from "@/components/AgentationToolbar";
import "./globals.css";

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Narad AI",
  description: "An autonomous AI persona that discovers, analyzes and shares the most valuable AI & Tech insights.",
  icons: {
    icon: "/Favicon.png",
    shortcut: "/Favicon.png",
    apple: "/Favicon.png",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${jetbrainsMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#0B0F19]">
        {children}
        <AgentationToolbar />
      </body>
    </html>
  );
}
