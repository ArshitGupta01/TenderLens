import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TenderLens — AI-Powered Government Procurement Engine',
  description: 'Deterministic tender compliance intelligence and statutory audit platform for Indian public procurement.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.svg" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
