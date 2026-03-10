import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'

const MOBILE = typeof window !== 'undefined' && window.innerWidth < 768

export default class ParticleEngine {
  constructor(container, shapeFn, options = {}) {
    this.container = container
    this.shapeFn = shapeFn
    this.options = options
    this.count = MOBILE ? Math.min(options.count || 10000, 5000) : (options.count || 10000)
    this.useBloom = MOBILE ? false : (options.bloom !== false)
    this.autoRotate = options.autoRotate || false
    this.controls = {}
    this.controlDefs = []
    this._annotations = new Map()
    this._annotationSprites = new Map()
    this._info = { title: '', desc: '' }
    this._onInfo = options.onInfo || null
    this._onControlsReady = options.onControlsReady || null
    this._running = false
    this._disposed = false
    this._time = 0
    this._observer = null

    // Defer init to next frame so layout is resolved
    requestAnimationFrame(() => {
      if (!this._disposed) this._init()
    })
  }

  _init() {
    const w = this.container.clientWidth || 400
    const h = this.container.clientHeight || 300
    const dpr = MOBILE ? 1 : Math.min(window.devicePixelRatio, 2)

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: !MOBILE, alpha: true })
    this.renderer.setPixelRatio(dpr)
    this.renderer.setSize(w, h)
    this.renderer.setClearColor(0x000000, 0)
    this.container.appendChild(this.renderer.domElement)

    // Scene
    this.scene = new THREE.Scene()
    this.scene.fog = new THREE.FogExp2(0x000000, 0.008)

    // Camera
    this.camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 500)
    this.camera.position.set(0, 0, 80)

    // Controls
    this.orbit = new OrbitControls(this.camera, this.renderer.domElement)
    this.orbit.enableDamping = true
    this.orbit.dampingFactor = 0.05
    this.orbit.autoRotate = this.autoRotate
    this.orbit.autoRotateSpeed = 0.5

    // Instanced mesh
    const geo = new THREE.SphereGeometry(0.15, 6, 6)
    const mat = new THREE.MeshBasicMaterial({ vertexColors: false })
    this.mesh = new THREE.InstancedMesh(geo, mat, this.count)
    this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage)

    // Instance color buffer
    const colors = new Float32Array(this.count * 3)
    this.mesh.instanceColor = new THREE.InstancedBufferAttribute(colors, 3)
    this.mesh.instanceColor.setUsage(THREE.DynamicDrawUsage)

    this.scene.add(this.mesh)

    // Bloom
    if (this.useBloom) {
      this.composer = new EffectComposer(this.renderer)
      this.composer.addPass(new RenderPass(this.scene, this.camera))
      const bloom = new UnrealBloomPass(new THREE.Vector2(w, h), 0.8, 0.4, 0.85)
      this.composer.addPass(bloom)
    }

    // Collect control definitions from shape (dry run for particle 0)
    this._collectControls()

    // Intersection observer for auto-pause
    this._observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !this._running) this.start()
        else if (!entry.isIntersecting && this._running) this._pause()
      },
      { threshold: 0.05 }
    )
    this._observer.observe(this.container)
  }

  _collectControls() {
    const defs = []
    const dummy = new THREE.Object3D()
    const color = new THREE.Color()
    const target = new THREE.Vector3()

    const addControl = (id, label, min, max, defaultVal) => {
      if (!(id in this.controls)) {
        this.controls[id] = defaultVal
        defs.push({ id, label, min, max, default: defaultVal })
      }
      return this.controls[id]
    }

    // Run shape fn once for particle 0 to register controls
    try {
      this.shapeFn({
        i: 0, count: this.count, target, color, THREE, time: 0,
        setInfo: () => {},
        annotate: () => {},
        addControl,
      })
    } catch (e) {
      // Shape may fail on first pass — that's okay
    }

    this.controlDefs = defs
    if (this._onControlsReady) this._onControlsReady(defs)
  }

  setControl(id, value) {
    this.controls[id] = value
  }

  start() {
    if (this._disposed) return
    this._running = true
    this._lastFrame = performance.now()
    this._animate()
  }

  stop() {
    this._running = false
  }

  _pause() {
    this._running = false
  }

  _animate() {
    if (!this._running || this._disposed) return
    requestAnimationFrame(() => this._animate())

    const now = performance.now()
    const dt = (now - this._lastFrame) / 1000
    this._lastFrame = now
    this._time += dt

    this._updateParticles()
    this.orbit.update()

    if (this.composer) {
      this.composer.render()
    } else {
      this.renderer.render(this.scene, this.camera)
    }
  }

  _updateParticles() {
    const dummy = new THREE.Object3D()
    const color = new THREE.Color()
    const target = new THREE.Vector3()
    const time = this._time
    const count = this.count

    let infoSet = false
    const annotations = new Map()

    const addControl = (id, _label, _min, _max, defaultVal) => {
      return this.controls[id] !== undefined ? this.controls[id] : defaultVal
    }

    const setInfo = (title, desc) => {
      if (!infoSet) {
        infoSet = true
        if (this._info.title !== title || this._info.desc !== desc) {
          this._info = { title, desc }
          if (this._onInfo) this._onInfo(title, desc)
        }
      }
    }

    const annotate = (id, pos, text) => {
      annotations.set(id, { pos: pos.clone(), text })
    }

    for (let i = 0; i < count; i++) {
      target.set(0, 0, 0)
      color.setRGB(1, 1, 1)

      this.shapeFn({
        i, count, target, color, THREE, time,
        setInfo,
        annotate,
        addControl,
      })

      dummy.position.copy(target)
      dummy.updateMatrix()
      this.mesh.setMatrixAt(i, dummy.matrix)
      this.mesh.instanceColor.setXYZ(i, color.r, color.g, color.b)
    }

    this.mesh.instanceMatrix.needsUpdate = true
    this.mesh.instanceColor.needsUpdate = true

    // Update annotation sprites
    this._updateAnnotations(annotations)
  }

  _updateAnnotations(annotations) {
    // Remove old annotations not in new set
    for (const [id, sprite] of this._annotationSprites) {
      if (!annotations.has(id)) {
        this.scene.remove(sprite)
        this._annotationSprites.delete(id)
      }
    }

    // Update or create annotations
    for (const [id, { pos, text }] of annotations) {
      let sprite = this._annotationSprites.get(id)
      if (!sprite) {
        const canvas = document.createElement('canvas')
        canvas.width = 256
        canvas.height = 64
        const ctx = canvas.getContext('2d')
        ctx.font = '20px monospace'
        ctx.fillStyle = 'rgba(255,255,255,0.7)'
        ctx.textAlign = 'center'
        ctx.fillText(text, 128, 40)
        const tex = new THREE.CanvasTexture(canvas)
        const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false })
        sprite = new THREE.Sprite(mat)
        sprite.scale.set(12, 3, 1)
        this.scene.add(sprite)
        this._annotationSprites.set(id, sprite)
      }
      sprite.position.copy(pos)
    }
  }

  resize() {
    if (this._disposed) return
    const w = this.container.clientWidth
    const h = this.container.clientHeight
    if (w === 0 || h === 0) return
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(w, h)
    if (this.composer) this.composer.setSize(w, h)
  }

  dispose() {
    this._disposed = true
    this._running = false
    if (this._observer) {
      this._observer.disconnect()
      this._observer = null
    }
    // Guard: init may not have run yet (React strict mode double-invoke)
    if (!this.mesh) return
    // Clean up annotations
    for (const [, sprite] of this._annotationSprites) {
      sprite.material.map?.dispose()
      sprite.material.dispose()
      this.scene.remove(sprite)
    }
    this._annotationSprites.clear()
    this.mesh.geometry.dispose()
    this.mesh.material.dispose()
    this.scene.remove(this.mesh)
    this.orbit.dispose()
    if (this.composer) {
      this.composer.passes.forEach(p => p.dispose?.())
    }
    this.renderer.dispose()
    if (this.renderer.domElement.parentNode) {
      this.renderer.domElement.parentNode.removeChild(this.renderer.domElement)
    }
  }
}
