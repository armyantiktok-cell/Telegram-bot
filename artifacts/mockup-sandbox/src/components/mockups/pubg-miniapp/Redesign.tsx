export function Redesign() {
  return (
    <div style={{
      fontFamily: "-apple-system, 'Inter', 'Segoe UI', sans-serif",
      background: "#050c0a",
      color: "#f0f0f0",
      minHeight: "100vh",
      maxWidth: "390px",
      margin: "0 auto",
      overflowX: "hidden",
      paddingBottom: "70px",
      position: "relative",
    }}>
      {/* Ambient glow */}
      <div style={{
        position: "fixed", top: "-100px", left: "50%", transform: "translateX(-50%)",
        width: "400px", height: "400px",
        background: "radial-gradient(circle, rgba(0,212,163,.12) 0%, transparent 70%)",
        pointerEvents: "none", zIndex: 0,
      }} />

      {/* Header */}
      <div style={{
        background: "linear-gradient(180deg, #071410 0%, #050c0a 100%)",
        padding: "20px 20px 16px",
        borderBottom: "1px solid rgba(0,212,163,.18)",
        position: "relative", zIndex: 1,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "14px" }}>
          <img
            src="/__mockup/images/logo.jpg"
            alt="ARMYAN"
            style={{ width: "44px", height: "44px", borderRadius: "12px", objectFit: "cover", flexShrink: 0, border: "1.5px solid rgba(0,212,163,.3)" }}
          />
          <div>
            <div style={{ fontSize: "15px", fontWeight: 700, color: "#00d4a3", letterSpacing: ".5px" }}>ARMYAN SERVICES</div>
            <div style={{ fontSize: "11px", color: "#4a7a6f", letterSpacing: "1px" }}>PUBG MOBILE • УСЛУГИ</div>
          </div>
        </div>
        <h1 style={{
          fontSize: "22px", fontWeight: 800, lineHeight: 1.2,
          background: "linear-gradient(90deg, #fff 0%, #00d4a3 100%)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>Магазин услуг</h1>
        <p style={{ fontSize: "13px", color: "#6a9e93", marginTop: "6px", lineHeight: 1.5 }}>Выбери категорию — всё для твоей игры</p>
      </div>

      {/* Content */}
      <div style={{ padding: "16px 20px 0", position: "relative", zIndex: 1 }}>
        <div style={{ fontSize: "11px", fontWeight: 700, color: "#2a6a5e", letterSpacing: "1.2px", marginBottom: "12px", textTransform: "uppercase" }}>Выбери категорию</div>

        {/* Main card */}
        <div style={{
          position: "relative", borderRadius: "18px", overflow: "hidden",
          padding: "22px 18px", cursor: "pointer",
          border: "1.5px solid rgba(0,212,163,.4)",
          background: "radial-gradient(circle at 85% 15%, rgba(0,212,163,.2) 0%, transparent 50%), radial-gradient(circle at 15% 85%, rgba(0,180,140,.1) 0%, transparent 55%), linear-gradient(135deg, #071f1a 0%, #050e0c 60%, #050a09 100%)",
          marginBottom: "14px",
        }}>
          <div style={{ fontSize: "18px", fontWeight: 800, color: "#00d4a3", marginBottom: "6px" }}>🎯 Настройка чувствительности</div>
          <div style={{ fontSize: "12px", color: "#7ab5aa", lineHeight: 1.5 }}>Индивидуально • Голосовой звонок • iPhone / iPad / Android</div>
          <div style={{ position: "absolute", top: "50%", right: "16px", transform: "translateY(-50%)", fontSize: "22px", color: "rgba(0,212,163,.6)" }}>›</div>
        </div>

        {/* Soon card */}
        <div style={{
          borderRadius: "18px", overflow: "hidden",
          padding: "22px 18px",
          border: "1.5px solid rgba(0,212,163,.15)",
          background: "linear-gradient(135deg, #060e0c 0%, #050a09 100%)",
          marginBottom: "20px",
        }}>
          <div style={{
            display: "inline-block", fontSize: "9px", fontWeight: 800, letterSpacing: "1px",
            background: "rgba(0,212,163,.12)", border: "1px solid rgba(0,212,163,.3)",
            color: "#00d4a3", padding: "3px 10px", borderRadius: "20px", marginBottom: "8px",
            textTransform: "uppercase",
          }}>Скоро</div>
          <div style={{ fontSize: "18px", fontWeight: 800, color: "#00d4a3", marginBottom: "6px" }}>✨ Новые услуги</div>
          <div style={{ fontSize: "12px", color: "#4a7a6f", lineHeight: 1.5 }}>Ассортимент расширяется — следи за обновлениями</div>
        </div>

        {/* Popular */}
        <div style={{ fontSize: "11px", fontWeight: 700, color: "#2a6a5e", letterSpacing: "1.2px", marginBottom: "12px", textTransform: "uppercase" }}>Популярное</div>
        {[
          { icon: "🎯", name: "Настройка чувствительности", sub: "Разовая • 20–60 мин", price: "800 грн" },
          { icon: "💎", name: "Оплата в UC", sub: "Настройка за UC на PUBG ID", price: "1320 UC" },
        ].map((item, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: "12px",
            background: "rgba(0,212,163,.04)", border: "1px solid rgba(0,212,163,.12)",
            borderRadius: "12px", padding: "12px 14px", marginBottom: "8px", cursor: "pointer",
          }}>
            <div style={{
              width: "36px", height: "36px", minWidth: "36px", borderRadius: "10px",
              background: "rgba(0,212,163,.1)", display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "18px",
            }}>{item.icon}</div>
            <div>
              <div style={{ fontSize: "13px", fontWeight: 700, color: "#fff" }}>{item.name}</div>
              <div style={{ fontSize: "11px", color: "#4a7a6f", marginTop: "2px" }}>{item.sub}</div>
            </div>
            <div style={{ marginLeft: "auto", fontSize: "14px", fontWeight: 800, color: "#00d4a3", whiteSpace: "nowrap" }}>{item.price}</div>
          </div>
        ))}
      </div>

      {/* Bottom Nav */}
      <nav style={{
        position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)",
        width: "100%", maxWidth: "390px",
        background: "#071410",
        borderTop: "1px solid rgba(0,212,163,.12)",
        display: "flex", zIndex: 100,
      }}>
        {[
          { icon: "🛍️", label: "Магазин", active: true },
          { icon: "📦", label: "Заказы", active: false },
          { icon: "👤", label: "Профиль", active: false },
        ].map((tab, i) => (
          <div key={i} style={{
            flex: 1, display: "flex", flexDirection: "column", alignItems: "center",
            justifyContent: "center", padding: "10px 4px",
            color: tab.active ? "#00d4a3" : "#2a5a50",
            fontSize: "10px", gap: "4px",
          }}>
            <span style={{ fontSize: "22px", lineHeight: 1 }}>{tab.icon}</span>
            {tab.label}
          </div>
        ))}
      </nav>
    </div>
  );
}
