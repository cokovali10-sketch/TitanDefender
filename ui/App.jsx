import React, { useState } from "react";
import { motion } from "framer-motion";

const cards = [
  { label: "Защита", value: "Активна", color: "from-emerald-400 to-cyan-400" },
  { label: "Последнее сканирование", value: "2 мин назад", color: "from-violet-400 to-fuchsia-400" },
  { label: "Угрозы", value: "0", color: "from-rose-400 to-orange-400" },
  { label: "База", value: "Актуальна", color: "from-amber-400 to-yellow-400" },
];

export default function App() {
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);

  const startScan = () => {
    setScanning(true);
    setProgress(0);
    const iv = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) { clearInterval(iv); setScanning(false); return 100; }
        return p + 4;
      });
    }, 80);
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#0a0e1a] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(124,58,237,0.25),transparent_40%),radial-gradient(circle_at_80%_80%,rgba(56,189,248,0.2),transparent_40%)]" />
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative z-10 flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-2xl">
          <motion.div initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="backdrop-blur-2xl bg-white/5 border border-white/10 rounded-3xl p-8 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-5xl font-black tracking-tight bg-gradient-to-r from-violet-400 via-fuchsia-400 to-cyan-400 bg-clip-text text-transparent">TitanDefender</h1>
                <p className="text-white/60 mt-1">Современный антивирус · Glassmorphism</p>
              </div>
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 8, ease: "linear" }} className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-2xl shadow-lg">🛡️</motion.div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={startScan}
              disabled={scanning}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-violet-600 via-fuchsia-600 to-cyan-600 text-white font-bold text-lg shadow-xl disabled:opacity-60"
            >
              {scanning ? `Сканирование... ${progress}%` : "Быстрое сканирование"}
            </motion.button>

            {scanning && (
              <div className="mt-4 h-2 rounded-full bg-white/10 overflow-hidden">
                <motion.div className="h-full bg-gradient-to-r from-violet-500 to-cyan-500" style={{ width: `${progress}%` }} />
              </div>
            )}

            <div className="mt-6 grid grid-cols-2 gap-3">
              {cards.map((c, i) => (
                <motion.div
                  key={c.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 hover:bg-white/10 transition"
                >
                  <div className={`text-xs font-semibold bg-gradient-to-r ${c.color} bg-clip-text text-transparent`}>{c.label}</div>
                  <div className="text-white/90 font-medium mt-1">{c.value}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
