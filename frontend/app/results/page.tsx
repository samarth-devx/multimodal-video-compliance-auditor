'use client'

import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Shield, ArrowLeft, ArrowRight, CheckCircle, XCircle, AlertTriangle, AlertCircle } from 'lucide-react'

interface ComplianceIssue {
    category: string
    severity: string
    description: string
}

interface AuditResult {
    session_id: string
    video_id: string
    status: string
    final_report: string
    compliance_results: ComplianceIssue[]
}

function getAuditData(): AuditResult | null {
    if (typeof window === 'undefined') return null
    const stored = localStorage.getItem('auditResult')
    if (!stored) return null
    return JSON.parse(stored) as AuditResult
}

export default function Results() {
    const router = useRouter()
    const data = getAuditData()

    if (!data) {
        router.push('/')
        return null
    }

    const isPassed = data.status === 'PASS'

    const severityColor = (severity: string) => {
        switch (severity?.toUpperCase()) {
            case 'CRITICAL': return '#ef4444'
            case 'MAJOR': return '#f97316'
            case 'MODERATE': return '#eab308'
            case 'WARNING': return '#eab308'
            default: return '#6b7280'
        }
    }

    return (
        <div className="max-w-2xl mx-auto px-4 py-10">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    {isPassed
                        ? <CheckCircle size={28} color="#7ce04a" />
                        : <XCircle size={28} color="#ef4444" />}
                    <div>
                        <p className="text-xs text-muted-foreground">audit result</p>
                        <h1 className="text-2xl font-medium tracking-tight" style={{ color: isPassed ? '#7ce04a' : '#ef4444' }}>
                            {isPassed ? 'PASS' : 'FAIL'}
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

            <Card className="bg-card border-border mb-4">
                <CardHeader>
                    <CardTitle className="text-sm font-medium tracking-tight inline-flex items-center gap-2">
                        <AlertTriangle size={14} color="#eab308" />
                        violations detected ({data.compliance_results?.length || 0})
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                    {data.compliance_results?.length === 0
                        ? <p className="text-muted-foreground text-sm">no violations found.</p>
                        : data.compliance_results?.map((issue, i) => (
                            <div key={i} className="border border-border rounded-lg p-3">
                                <div className="flex items-center gap-2 mb-1.5">
                                    <AlertCircle size={12} color={severityColor(issue.severity)} />
                                    <Badge
                                        variant="secondary"
                                        className="text-xs font-medium tracking-tight"
                                        style={{ color: severityColor(issue.severity) }}
                                    >
                                        {issue.severity}
                                    </Badge>
                                    <span className="text-sm font-medium tracking-tight">{issue.category}</span>
                                </div>
                                <p className="text-muted-foreground text-xs leading-relaxed">{issue.description}</p>
                            </div>
                        ))}
                </CardContent>
            </Card>

            <Card className="bg-card border-border mb-6">
                <CardHeader>
                    <CardTitle className="text-sm font-medium tracking-tight inline-flex items-center gap-2">
                        <Shield size={14} color="#7ce04a" />
                        final summary
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