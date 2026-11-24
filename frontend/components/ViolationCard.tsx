import { AlertCircle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { severityColor } from '@/lib/severity'
import type { Violation } from '@/lib/types'

export function ViolationCard({ violation }: { violation: Violation }) {
    const color = severityColor(violation.severity)

    return (
        <div className="border border-border rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1.5">
                <AlertCircle size={12} color={color} />
                <Badge variant="secondary" className="text-xs font-medium tracking-tight" style={{ color }}>
                    {violation.severity}
                </Badge>
                <span className="text-sm font-medium tracking-tight">{violation.category}</span>
                {violation.timestamp && (
                    <span className="ml-auto text-xs font-mono text-muted-foreground">
                        @ {violation.timestamp}
                    </span>
                )}
            </div>
            <p className="text-muted-foreground text-xs leading-relaxed">{violation.description}</p>
            {violation.evidence && (
                <blockquote className="mt-2 border-l-2 border-border pl-2 text-xs italic text-muted-foreground">
                    &ldquo;{violation.evidence}&rdquo;
                </blockquote>
            )}
        </div>
    )
}