import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { Shield } from 'lucide-react'

const geist = Geist({ subsets: ['latin'], variable: '--font-sans' })
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata: Metadata = {
    title: 'MVCA',
    description: 'Multimodal Video Compliance Auditor',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body className={`${geist.variable} ${geistMono.variable}`}>
                <nav className="border-b border-border h-13 flex items-center justify-between px-6">
                    <Link href="/" className="font-medium text-sm flex items-center gap-2 tracking-tight">
                        <Shield size={15} color="#7ce04a" />
                        Advertising Compliance Auditor
                    </Link>
                    <span className="text-sm text-muted-foreground tracking-tight">
                        Multimodal Video Compliance Auditor
                    </span>
                </nav>
                <main>{children}</main>
            </body>
        </html>
    )
}