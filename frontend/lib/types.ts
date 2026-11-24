export type Severity = 'CRITICAL' | 'MAJOR' | 'MODERATE' | 'WARNING'
export type AuditStatus = 'PASS' | 'FAIL' | 'ERROR'

export interface Violation {
    category: string
    severity: Severity
    description: string
    evidence: string
    timestamp: string | null
}

export interface AuditResult {
    session_id: string
    video_id: string
    status: AuditStatus
    final_report: string
    compliance_results: Violation[]
}