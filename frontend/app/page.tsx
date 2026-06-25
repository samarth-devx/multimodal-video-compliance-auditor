'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { ArrowRight, Loader2, Video } from 'lucide-react'

export default function Home() {
    const router = useRouter()
    const [url, setUrl] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    async function handleAudit() {
        if (!url.trim()) return setError('please enter a youtube url')
        setLoading(true)
        setError('')
        try {
            const res = await fetch('http://localhost:8000/audit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_url: url })
            })
            const data = await res.json()
            localStorage.setItem('auditResult', JSON.stringify(data))
            router.push('/results')
        } catch {
            setError('failed to connect to server. make sure the API is running.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
            <h1 className="text-4xl font-medium mb-4 leading-tight tracking-tight">
                Audit any youtube ad<br />
                <span style={{ color: '#FFFFFF' }}>for</span>
                <span style={{ color: '#7ce04a' }}> compliance</span>
            </h1>
            <p className="text-muted-foreground text-base mb-8 max-w-md leading-relaxed">
                Paste a youtube url, and we analyze it against FTC guidelines and brand rules automatically.
            </p>

            <Card className="w-full max-w-md bg-card border-border">
                <CardHeader>
                    <CardTitle className="text-base font-medium tracking-tight">New audit</CardTitle>
                    <CardDescription className="text-sm text-muted-foreground">
                        Enter a youtube ad url to begin compliance check
                    </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                    <div className="flex flex-col gap-1.5">
                        <label className="text-sm font-medium tracking-tight text-muted-foreground inline-flex items-center gap-1.5">
                            <Video size={13} />
                            youtube url
                        </label>
                        <Input
                            placeholder="https://youtu.be/..."
                            value={url}
                            onChange={e => { setUrl(e.target.value); setError('') }}
                            onKeyDown={e => e.key === 'Enter' && handleAudit()}
                            className="bg-muted border-border text-foreground placeholder:text-muted-foreground"
                        />
                        {error && <p className="text-red-400 text-xs">{error}</p>}
                    </div>
                    <Button
                        onClick={handleAudit}
                        disabled={loading}
                        className="w-full mt-2 font-medium tracking-tight flex items-center gap-2"
                    >
                        {loading ? (
                            <>
                                <Loader2 size={14} className="animate-spin" />
                                analyzing... this may take 2-3 mins
                            </>
                        ) : (
                            <>
                                run audit
                                <ArrowRight size={14} />
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>
        </div>
    )
}