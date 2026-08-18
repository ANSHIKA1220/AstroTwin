import type { Metadata } from "next";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_APP_URL ?? (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : "http://localhost:3000");

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "AstroTwin — Astrology that remembers your life",
  description: "A persistent astrology-inspired reflection companion connecting your goals, life events, daily guidance and human astrologers.",
  openGraph: { title: "AstroTwin", description: "Meet the astrology companion that remembers your life.", type: "website", images:["/og.png"] },
  twitter: { card:"summary_large_image", title:"AstroTwin", description:"Astrology that remembers your life.", images:["/og.png"] },
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
