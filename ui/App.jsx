import React from "react";
import { motion } from "framer-motion";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl p-10 shadow-2xl max-w-md w-full"
      >
        <h1 className="text-4xl font-bold text-white mb-2">TitanDefender</h1>
        <p className="text-white/70 mb-6">Modern Antivirus · Glassmorphism UI</p>
        <button className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-semibold hover:opacity-90 transition">
          Quick Scan
        </button>
        <div className="mt-6 grid grid-cols-2 gap-3">
          {["Protected", "Last scan: 2m ago", "Threats: 0", "DB: up to date"].map((t) => (
            <div key={t} className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-3 text-white/80 text-sm">
              {t}
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
