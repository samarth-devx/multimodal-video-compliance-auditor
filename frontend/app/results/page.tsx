'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Shield, ArrowLeft, ArrowRight, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { ViolationCard } from '@/components/ViolationCard'
import { loadAudit } from '@/lib/audit-store'
import type { AuditResult, AuditStatus } from '@/lib/types'

const STATUS_UI: Record<AuditStatus, { color: string; Icon: typeof CheckCircle }> = {
    PASS: { color: '#7ce04a', Icon: CheckCircle },
    FAIL: { color: '#ef4444', Icon: XCircle },
    ERROR: { color: '#eab308', Icon: AlertTriangle },
}

export default function Results() {
    const router = useRouter()
    const [data, setData] = useState<AuditResult | null>(null)

    useEffect(() => {
        const stored = loadAudit()
        if (stored) setData(stored)
        else router.replace('/')
    }, [router])

    if (!data) return null

    const { color, Icon } = STATUS_UI[data.status] ?? STATUS_UI.ERROR
    const isError = data.status === 'ERROR'
    const violations = data.compliance_results ?? []

    return (
        <div className="max-w-2xl mx-auto px-4 py-10">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <Icon size={28} color={color} />
                    <div>
                        <p className="text-xs text-muted-foreground">audit result</p>
                        <h1 className="text-2xl font-medium tracking-tight" style={{ color }}>
                            {data.status}
                        </h1>
                    </div>
                </div>
                <Button variant="ghost" onClick={() => router.push('/')} className="text-muted-foreground flex items-center gap-2 text-sm">
                    <ArrowLeft size={14} /> new audit
                </Button>
            </div>

            <Card className="bg-card border-border mb-4">
                <CardContent className="py-4 flex flex-col gap-1">
                    <p className="text-xs text-muted-foreground">session id</p>
                    <p className="text-sm font-mono text-foreground">{data.session_id}</p>
                    <p className="text-xs text-muted-foreground mt-2">video id</p>
                    <p className="text-sm font-mono text-foreground">{data.video_id}</p>
                </CardContent>
            </Card>

            {!isError && (
                <Card className="bg-card border-border mb-4">
                    <CardHeader>
                        <CardTitle className="text-sm font-medium tracking-tight inline-flex items-center gap-2">
                            <AlertTriangle size={14} color="#eab308" />
                            violations detected ({violations.length})
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-3">
                        {violations.length === 0
                            ? <p className="text-muted-foreground text-sm">no violations found.</p>
                            : violations.map((v, i) => <ViolationCard key={i} violation={v} />)}
                    </CardContent>
                </Card>
            )}

            <Card className="bg-card border-border mb-6">
                <CardHeader>
                    <CardTitle className="text-sm font-medium tracking-tight inline-flex items-center gap-2">
                        <Shield size={14} color="#7ce04a" />
                        {isError ? 'what went wrong' : 'final summary'}
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground text-sm leading-relaxed">{data.final_report}</p>
                </CardContent>
            </Card>

            <Button onClick={() => router.push('/')} className="w-full font-medium tracking-tight flex items-center gap-2">
                audit another video <ArrowRight size={14} />
            </Button>
        </div>
    )
}