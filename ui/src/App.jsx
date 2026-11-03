import React, { useState } from "react";

export default function App() {
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [page, setPage] = useState("dashboard");

  const nav = [
    { id: "dashboard", label: "📊 Панель" },
    { id: "scan", label: "🔍 Сканирование" },
    { id: "deep", label: "🔬 Глубокий скан" },
    { id: "optimize", label: "⚡ Оптимизация" },
    { id: "quarantine", label: "🔒 Карантин" },
    { id: "history", label: "📜 История" },
    { id: "settings", label: "⚙️ Настройки" },
  ];

  return (
    <div className="flex h-screen bg-[#0a0e1a] text-white">
      <aside className="w-56 bg-[#080c18] p-4 flex flex-col gap-1">
        <div className="text-xl font-bold text-violet-300 mb-4">🛡️ TitanDefender</div>
        {nav.map(n => (
          <button key={n.id} onClick={() => setPage(n.id)}
            className={`text-left px-4 py-3 rounded-lg transition ${page===n.id ? "bg-violet-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}>
            {n.label}
          </button>
        ))}
        <div className="mt-auto text-xs text-emerald-400 px-4">● Безопасный режим</div>
      </aside>
      <main className="flex-1 p-8 overflow-auto">
        {page === "dashboard" && (
          <div>
            <h1 className="text-3xl font-bold text-violet-300 mb-6">Панель управления</h1>
            <div className="grid grid-cols-4 gap-4 mb-6">
              {["Последнее сканирование: 2 мин назад","Угрозы: 0","Сигнатуры: 100","Статус: Активен"].map((t,i)=>(
                <div key={i} className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                  <div className="text-slate-400 text-xs">{t.split(":")[0]}</div>
                  <div className="text-white font-bold text-lg mt-1">{t.split(":")[1]}</div>
                </div>
              ))}
            </div>
          </div>
        )}
        {page === "scan" && (
          <div>
            <h1 className="text-3xl font-bold text-violet-300 mb-6">Сканирование</h1>
            <button onClick={() => { setScanning(true); setProgress(0); const iv=setInterval(()=>setProgress(p=>{if(p>=100){clearInterval(iv);setScanning(false);return 100;}return p+4;}),80); }}
              disabled={scanning} className="px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 font-bold disabled:opacity-50">
              {scanning ? `Сканирование... ${progress}%` : "Быстрое сканирование"}
            </button>
            <div className="mt-4 h-2 rounded-full bg-slate-800 overflow-hidden">
              <div className="h-full bg-gradient-to-r from-violet-500 to-cyan-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
            <pre className="mt-6 bg-slate-900 border border-slate-800 rounded-2xl p-4 text-sm text-slate-300 min-h-[200px]">Результаты появятся здесь...</pre>
          </div>
        )}
      </main>
    </div>
  );
}
