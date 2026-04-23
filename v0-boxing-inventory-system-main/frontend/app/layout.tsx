import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Boxing Store - Menaxhimi i Stokut",
  description: "Sistem per menaxhimin e stokut te dyqanit te boksit",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="sq" className="bg-background">
      <body className={`${inter.className} antialiased`}>{children}</body>
    </html>
  );
}
