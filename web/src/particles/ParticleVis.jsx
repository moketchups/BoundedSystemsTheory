import { useRef, useState } from 'react'
import useParticleShape from './useParticleShape'

export default function ParticleVis({
  shape,
  count = 10000,
  className = '',
  bloom = true,
  autoRotate = false,
  showHUD = true,
  showControls = true,
}) {
  const containerRef = useRef(null)
  const { info, controls, setControl } = useParticleShape(containerRef, shape, {
    count,
    bloom,
    autoRotate,
  })

  return (
    <div className={className}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {showHUD && info.title && (
        <div className="absolute top-3 left-3 pointer-events-none">
          <p className="text-xs font-mono font-bold text-white/90 drop-shadow-lg">
            {info.title}
          </p>
          <p className="text-xs font-mono text-white/60 mt-0.5 max-w-xs drop-shadow">
            {info.desc}
          </p>
        </div>
      )}

      {showControls && controls.length > 0 && (
        <div className="absolute bottom-3 left-3 right-3 flex flex-wrap gap-3 pointer-events-auto">
          {controls.map(c => (
            <label key={c.id} className="flex items-center gap-2 text-xs text-white/70">
              <span className="font-mono drop-shadow">{c.label}</span>
              <input
                type="range"
                min={c.min}
                max={c.max}
                step={(c.max - c.min) / 100}
                defaultValue={c.default}
                onChange={e => setControl(c.id, parseFloat(e.target.value))}
                className="w-24 h-1 accent-cyan-400"
              />
            </label>
          ))}
        </div>
      )}
    </div>
  )
}
