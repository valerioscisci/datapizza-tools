import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Datapizza Tools',
  description: 'Navigate the AI-driven job market',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
