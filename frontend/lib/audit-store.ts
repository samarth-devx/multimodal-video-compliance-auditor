import type { AuditResult } from './types'

const KEY = 'auditResult'

export function saveAudit(result: AuditResult): void {
    try {
        sessionStorage.setItem(KEY, JSON.stringify(result))
    } catch {
        /* storage unavailable (private mode etc.) */
    }
}

export function loadAudit(): AuditResult | null {
    try {
        const raw = sessionStorage.getItem(KEY)
        return raw ? (JSON.parse(raw) as AuditResult) : null
    } catch {
        return null
    }
}