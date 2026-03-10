import { useEffect, useRef, useState, useCallback } from 'react'
import ParticleEngine from './ParticleEngine'

export default function useParticleShape(containerRef, shapeFn, options = {}) {
  const engineRef = useRef(null)
  const [info, setInfo] = useState({ title: '', desc: '' })
  const [controls, setControls] = useState([])

  const setControl = useCallback((id, value) => {
    if (engineRef.current) engineRef.current.setControl(id, value)
  }, [])

  useEffect(() => {
    const el = containerRef.current
    if (!el || !shapeFn) return

    const engine = new ParticleEngine(el, shapeFn, {
      ...options,
      onInfo: (title, desc) => setInfo({ title, desc }),
      onControlsReady: (defs) => setControls(defs),
    })

    engineRef.current = engine

    // ResizeObserver
    const ro = new ResizeObserver(() => engine.resize())
    ro.observe(el)

    return () => {
      ro.disconnect()
      engine.dispose()
      engineRef.current = null
    }
  }, [shapeFn]) // Only re-create when shape changes

  return { info, controls, setControl }
}
