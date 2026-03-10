import { useRef, useState, useEffect, lazy, Suspense } from 'react'

const ParticleVis = lazy(() => import('./ParticleVis'))

export default function LazyParticleVis(props) {
  const sentinelRef = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = sentinelRef.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          obs.disconnect()
        }
      },
      { rootMargin: '200px' }
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  return (
    <div ref={sentinelRef} className={props.className || ''}>
      {visible ? (
        <Suspense fallback={
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs text-muted animate-pulse">Loading visualization...</span>
          </div>
        }>
          <ParticleVis {...props} />
        </Suspense>
      ) : (
        <div className="absolute inset-0 bg-surface/50 rounded" />
      )}
    </div>
  )
}
