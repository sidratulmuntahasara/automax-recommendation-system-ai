import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Property Appraisal Recommendation System",
  keywords: [
    "property appraisal",
    "real estate",
    "recommendation system",
    "comparables",
    "machine learning",
    "AI",
    "housing market",
  ],
  description: "A web application for recommending property comparables based on appraisal data.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
