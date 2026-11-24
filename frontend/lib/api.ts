import type { AuditResult } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

// FastAPI returns { detail: string } for HTTPException and
// { detail: [{ msg }] } for validation errors (422).
function extractError(body: unknown): string | null {
    const detail = (body as { detail?: unknown } | null)?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && typeof detail[0]?.msg === 'string') {
        return detail[0].msg.replace(/^Value error, /, '')
    }
    return null
}

export async function runAudit(videoUrl: string): Promise<AuditResult> {
    let res: Response
    try {
        res = await fetch(`${API_URL}/audit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_url: videoUrl }),
        })
    } catch {
        throw new Error('Failed to connect to the server. Make sure the API is running.')
    }

    if (!res.ok) {
        const body = await res.json().catch(() => null)
        throw new Error(extractError(body) ?? `Request failed (${res.status})`)
    }
    return res.json()
}