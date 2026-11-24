import type { Severity } from './types'

const COLORS: Record<Severity, string> = {
    CRITICAL: '#ef4444',
    MAJOR: '#f97316',
    MODERATE: '#eab308',
    WARNING: '#eab308',
}

export const severityColor = (s: string): string => COLORS[s as Severity] ?? '#6b7280'