import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  Search, Brain, Shield, Zap,
  Cpu, Database, Activity,
  ChevronRight, Network, Sparkles
} from 'lucide-react'
import * as THREE from 'three'

// --- COMPONENTS ---

const Header = () => (
  <header className="fixed top-0 left-0 right-0 h-20 flex items-center justify-between px-8 z-50 glass-panel" style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
    <div className="flex items-center gap-4">
      <div className="w-10 h-10 bg-black border border-[#00ff9d] flex items-center justify-center rounded">
        <Brain className="text-[#00ff9d]" size={24} />
      </div>
      <div>
        <h1 className="text-xl font-bold tracking-widest uppercase neon-text">Sovereign Intelligence</h1>
        <p className="text-[10px] uppercase tracking-[4px] text-gray-400">Deep Mesh Actuation</p>
      </div>
    </div>
    <div className="flex gap-6">
      <div className="flex items-center gap-2 px-4 py-1 rounded bg-[#00ff9d11] border border-[#00ff9d44]">
        <div className="w-2 h-2 rounded-full bg-[#00ff9d] animate-pulse" />
        <span className="text-xs font-mono text-[#00ff9d]">MESH: ONLINE</span>
      </div>
      <button className="neon-button text-xs py-2">DEPLOY ENGINE</button>
    </div>
  </header>
)

const Hero = () => (
  <section className="min-height-[60vh] flex flex-col items-center justify-center pt-32 pb-20 px-4 text-center">
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="max-w-4xl"
    >
      <h2 className="text-5xl md:text-7xl font-black mb-6 tracking-tight leading-tight">
        PHYSICAL <span className="neon-text">INTELLIGENCE</span> <br />
        DEPLOYED AT SCALE.
      </h2>
      <p className="text-gray-400 text-lg md:text-xl mb-10 max-w-2xl mx-auto leading-relaxed">
        The first external application actuated by the Sovereign Agent Mesh.
        Deep research, neural mapping, and autonomous product synthesis.
      </p>

      <div className="flex flex-col md:flex-row gap-4 justify-center items-center">
        <div className="relative w-full max-w-lg">
          <input
            type="text"
            placeholder="Initialize Deep Research Protocol..."
            className="w-full bg-black/40 border border-white/10 rounded-xl px-6 py-4 text-lg focus:border-[#00ff9d] focus:outline-none transition-all pr-16 backdrop-blur-xl"
          />
          <button className="absolute right-2 top-2 p-3 bg-[#00ff9d] text-black rounded-lg hover:bg-[#00d2ff] transition-all">
            <Search size={24} />
          </button>
        </div>
      </div>
    </motion.div>
  </section>
)

const FeatureCard = ({ icon: Icon, title, desc, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.5 }}
    className="glass-panel p-8 group hover:border-[#00ff9d] transition-all cursor-pointer"
  >
    <div className="w-12 h-12 bg-white/5 flex items-center justify-center rounded-lg mb-6 group-hover:bg-[#00ff9d22] transition-colors">
      <Icon className="text-gray-400 group-hover:text-[#00ff9d] transition-colors" size={28} />
    </div>
    <h3 className="text-xl font-bold mb-3 group-hover:neon-text transition-all">{title}</h3>
    <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
    <div className="mt-6 flex items-center gap-2 text-[10px] font-mono text-[#00ff9d] opacity-0 group-hover:opacity-100 transition-opacity">
      ACTIVATE MODULE <ChevronRight size={12} />
    </div>
  </motion.div>
)

const IntelligenceMesh = () => {
  const mountRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!mountRef.current) return

    // Simple 3D Scene for Intelligence Suite
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000)
    camera.position.z = 5

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight)
    mountRef.current.appendChild(renderer.domElement)

    const geometry = new THREE.IcosahedronGeometry(2, 1)
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff9d, wireframe: true, transparent: true, opacity: 0.1 })
    const sphere = new THREE.Mesh(geometry, material)
    scene.add(sphere)

    // Add floating points
    const pointsGeometry = new THREE.BufferGeometry()
    const pointsCount = 100
    const coords = new Float32Array(pointsCount * 3)
    for (let i = 0; i < pointsCount * 3; i++) coords[i] = (Math.random() - 0.5) * 10
    pointsGeometry.setAttribute('position', new THREE.BufferAttribute(coords, 3))
    const pointsMaterial = new THREE.PointsMaterial({ size: 0.05, color: 0x00d2ff })
    const points = new THREE.Points(pointsGeometry, pointsMaterial)
    scene.add(points)

    const animate = () => {
      requestAnimationFrame(animate)
      sphere.rotation.y += 0.002
      points.rotation.y -= 0.001
      renderer.render(scene, camera)
    }
    animate()

    return () => {
      renderer.dispose()
    }
  }, [])

  return <div ref={mountRef} className="absolute inset-0 pointer-events-none opacity-40" />
}

export default function App() {
  return (
    <div className="min-h-screen bg-[#010101] text-white selection:bg-[#00ff9d44] selection:text-[#00ff9d]">
      <div className="fixed inset-0 pointer-events-none">
        <IntelligenceMesh />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#010101]" />
      </div>

      <Header />

      <main className="relative z-10">
        <Hero />

        <section className="max-w-7xl mx-auto px-8 py-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={Network}
              title="Neural Graph Mapping"
              desc="Deep-level analysis of multi-layered data structures. Visualize the intent behind the information."
              delay={0.1}
            />
            <FeatureCard
              icon={Shield}
              title="Autonomous Auditing"
              desc="Real-time security verification driven by a 1,176-agent mesh security protocols."
              delay={0.2}
            />
            <FeatureCard
              icon={Sparkles}
              title="Predictive Synthesis"
              desc="Generative engine for new product concepts and code actuation based on current market signals."
              delay={0.3}
            />
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-8 py-40 flex flex-col md:flex-row items-center gap-20">
          <div className="flex-1">
            <h2 className="text-4xl font-bold mb-8 leading-tight">
              THE <span className="neon-text">SOVEREIGN</span> ADVANTAGE
            </h2>
            <div className="space-y-6">
              {[
                { icon: Zap, label: "Quantum Latency", val: "1.2ms Response" },
                { icon: Database, label: "Mesh Persistence", val: "Distributed Ledger" },
                { icon: Activity, label: "Real-time Pulse", val: "Heartbeat Protocol" }
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-6 p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-all">
                  <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-black border border-[#00ff9d33]">
                    <item.icon className="text-[#00ff9d]" size={24} />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 uppercase tracking-widest">{item.label}</div>
                    <div className="text-lg font-mono font-bold text-white">{item.val}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="flex-1 w-full aspect-square glass-panel p-10 relative overflow-hidden flex items-center justify-center">
            <div className="absolute inset-0 bg-[#00ff9d08] animate-pulse" />
            <div className="relative text-center">
              <Cpu size={120} className="text-[#00ff9d] mb-8 animate-bounce opacity-80" />
              <div className="text-xs font-mono text-[#00ff9d] tracking-widest">ACTUATING PHYSICAL CORE...</div>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-20 border-t border-white/5 text-center text-xs text-gray-600 uppercase tracking-[4px]">
        &copy; 2026 Sovereign Agent Mesh // Perfected by Antigravity
      </footer>
    </div>
  )
}
