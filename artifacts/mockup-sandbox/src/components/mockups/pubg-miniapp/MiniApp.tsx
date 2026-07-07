import { useState } from "react";
import { Check, ChevronRight, Crosshair, Shield, Zap, Star, MessageCircle, Send } from "lucide-react";

const FEATURES = [
  "Настройка под ваш девайс и стиль игры",
  "Расчёт чувствительности для любого прицела",
  "Подходит для PUBG Mobile и BGMI",
  "Поддержка гироскопа и без него",
  "Результат в течение 24 часов",
  "Индивидуальная консультация в Telegram",
];

const STEPS = [
  { icon: MessageCircle, label: "Напишите боту", desc: "Нажмите кнопку ниже" },
  { icon: Send, label: "Заполните анкету", desc: "Ответьте на 5 вопросов" },
  { icon: Crosshair, label: "Получите настройку", desc: "В течение 24 часов" },
];

const REVIEWS = [
  { name: "Artem_Pro", rank: "Платина II", text: "Убойная настройка, сразу почувствовал разницу. Рекойл стал намного стабильнее 🔥", stars: 5 },
  { name: "Kira_Mobile", rank: "Бриллиант", text: "Брала под iPhone с гироскопом. Теперь стреляю как на ПК, спасибо!", stars: 5 },
  { name: "NightHunter77", rank: "Корона", text: "Скептически относился, но результат удивил. Топчик за свои деньги.", stars: 5 },
];

export function MiniApp() {
  const [step, setStep] = useState<"home" | "order">("home");

  return (
    <div
      style={{
        fontFamily: "'Inter', 'Segoe UI', sans-serif",
        background: "#0a0a0f",
        minHeight: "100vh",
        color: "#f0f0f0",
        maxWidth: 390,
        margin: "0 auto",
        position: "relative",
        overflowX: "hidden",
      }}
    >
      {/* Ambient glow */}
      <div style={{
        position: "fixed", top: -80, left: "50%", transform: "translateX(-50%)",
        width: 320, height: 320,
        background: "radial-gradient(circle, rgba(255,180,0,0.12) 0%, transparent 70%)",
        pointerEvents: "none", zIndex: 0,
      }} />

      {step === "home" ? <HomePage onOrder={() => setStep("order")} /> : <OrderPage onBack={() => setStep("home")} />}
    </div>
  );
}

function HomePage({ onOrder }: { onOrder: () => void }) {
  return (
    <div style={{ position: "relative", zIndex: 1 }}>
      {/* Header */}
      <div style={{
        background: "linear-gradient(180deg, #1a1408 0%, #0a0a0f 100%)",
        padding: "28px 20px 20px",
        borderBottom: "1px solid rgba(255,180,0,0.15)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
          <div style={{
            width: 40, height: 40,
            background: "linear-gradient(135deg, #ffb400, #ff7a00)",
            borderRadius: 10,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Crosshair size={22} color="#000" />
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "#ffb400", letterSpacing: 0.5 }}>PUBG SENS PRO</div>
            <div style={{ fontSize: 11, color: "#888", letterSpacing: 1 }}>ИНДИВИДУАЛЬНАЯ НАСТРОЙКА</div>
          </div>
        </div>

        <h1 style={{
          fontSize: 26, fontWeight: 800, lineHeight: 1.2, margin: 0,
          background: "linear-gradient(90deg, #fff 0%, #ffb400 100%)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          Настройка чувствительности<br />под тебя
        </h1>
        <p style={{ fontSize: 13, color: "#aaa", marginTop: 8, lineHeight: 1.5 }}>
          Перестань проигрывать из-за неправильных настроек — получи индивидуальный профиль за 24 часа
        </p>
      </div>

      {/* Price card */}
      <div style={{ padding: "20px 20px 0" }}>
        <div style={{
          background: "linear-gradient(135deg, #1c1608 0%, #141010 100%)",
          border: "1px solid rgba(255,180,0,0.3)",
          borderRadius: 16,
          padding: "20px",
          position: "relative",
          overflow: "hidden",
        }}>
          <div style={{
            position: "absolute", top: 0, right: 0,
            background: "linear-gradient(135deg, #ffb400, #ff7a00)",
            color: "#000", fontSize: 11, fontWeight: 700,
            padding: "5px 14px", borderBottomLeftRadius: 12,
            letterSpacing: 0.5,
          }}>ХИТ ПРОДАЖ</div>

          <div style={{ display: "flex", alignItems: "baseline", gap: 6, marginBottom: 4 }}>
            <span style={{ fontSize: 38, fontWeight: 900, color: "#ffb400" }}>249</span>
            <span style={{ fontSize: 20, fontWeight: 700, color: "#ffb400" }}>₽</span>
            <span style={{ fontSize: 13, color: "#666", textDecoration: "line-through", marginLeft: 4 }}>499 ₽</span>
          </div>
          <div style={{ fontSize: 12, color: "#888", marginBottom: 16 }}>Разовая настройка • Без подписки</div>

          <div style={{ display: "flex", gap: 8 }}>
            {[Shield, Zap, Star].map((Icon, i) => (
              <div key={i} style={{
                flex: 1,
                background: "rgba(255,180,0,0.08)",
                border: "1px solid rgba(255,180,0,0.15)",
                borderRadius: 10, padding: "10px 6px",
                textAlign: "center",
              }}>
                <Icon size={16} color="#ffb400" style={{ marginBottom: 4 }} />
                <div style={{ fontSize: 10, color: "#aaa", lineHeight: 1.3 }}>
                  {["Безопасно", "Быстро", "Топ рейтинг"][i]}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <div style={{ padding: "20px 20px 0" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#888", letterSpacing: 1, marginBottom: 12 }}>
          ЧТО ВХОДИТ
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {FEATURES.map((f, i) => (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <div style={{
                width: 20, height: 20, minWidth: 20,
                background: "rgba(255,180,0,0.15)",
                borderRadius: 6,
                display: "flex", alignItems: "center", justifyContent: "center", marginTop: 1,
              }}>
                <Check size={12} color="#ffb400" strokeWidth={3} />
              </div>
              <span style={{ fontSize: 13, color: "#ccc", lineHeight: 1.4 }}>{f}</span>
            </div>
          ))}
        </div>
      </div>

      {/* How it works */}
      <div style={{ padding: "20px 20px 0" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#888", letterSpacing: 1, marginBottom: 12 }}>
          КАК ЭТО РАБОТАЕТ
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {STEPS.map((s, i) => (
            <div key={i} style={{
              flex: 1, textAlign: "center",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 12, padding: "14px 8px",
            }}>
              <div style={{
                width: 36, height: 36, margin: "0 auto 8px",
                background: "rgba(255,180,0,0.12)",
                borderRadius: 10,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <s.icon size={18} color="#ffb400" />
              </div>
              <div style={{ fontSize: 11, fontWeight: 700, color: "#fff", marginBottom: 3 }}>{s.label}</div>
              <div style={{ fontSize: 10, color: "#666", lineHeight: 1.3 }}>{s.desc}</div>
              {i < STEPS.length - 1 && (
                <ChevronRight size={12} color="#444" style={{ position: "absolute", right: -14, top: "50%" }} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Reviews */}
      <div style={{ padding: "20px 20px 0" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#888", letterSpacing: 1, marginBottom: 12 }}>
          ОТЗЫВЫ ИГРОКОВ
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {REVIEWS.map((r, i) => (
            <div key={i} style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 12, padding: "14px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "#fff" }}>{r.name}</div>
                  <div style={{ fontSize: 11, color: "#ffb400" }}>{r.rank}</div>
                </div>
                <div style={{ display: "flex", gap: 2 }}>
                  {Array(r.stars).fill(0).map((_, j) => (
                    <Star key={j} size={12} fill="#ffb400" color="#ffb400" />
                  ))}
                </div>
              </div>
              <div style={{ fontSize: 12, color: "#aaa", lineHeight: 1.5 }}>{r.text}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div style={{ padding: "24px 20px 32px" }}>
        <button
          onClick={onOrder}
          style={{
            width: "100%",
            background: "linear-gradient(135deg, #ffb400, #ff7a00)",
            color: "#000",
            border: "none",
            borderRadius: 14,
            padding: "16px",
            fontSize: 16,
            fontWeight: 800,
            cursor: "pointer",
            letterSpacing: 0.3,
            boxShadow: "0 4px 24px rgba(255,180,0,0.35)",
          }}
        >
          Заказать настройку — 249 ₽
        </button>
        <div style={{ textAlign: "center", fontSize: 12, color: "#555", marginTop: 10 }}>
          Оплата после получения настройки
        </div>
      </div>
    </div>
  );
}

function OrderPage({ onBack }: { onBack: () => void }) {
  const [sent, setSent] = useState(false);

  return (
    <div style={{ position: "relative", zIndex: 1 }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", gap: 12,
        padding: "20px 20px 16px",
        borderBottom: "1px solid rgba(255,180,0,0.1)",
      }}>
        <button
          onClick={onBack}
          style={{
            background: "rgba(255,255,255,0.06)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 8, padding: "6px 12px",
            color: "#fff", fontSize: 13, cursor: "pointer",
          }}
        >
          ← Назад
        </button>
        <div style={{ fontSize: 16, fontWeight: 700 }}>Оформить заказ</div>
      </div>

      {!sent ? (
        <div style={{ padding: "24px 20px" }}>
          <div style={{
            background: "rgba(255,180,0,0.06)",
            border: "1px solid rgba(255,180,0,0.2)",
            borderRadius: 14, padding: "16px", marginBottom: 24,
          }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#ffb400", marginBottom: 4 }}>
              Как происходит оплата?
            </div>
            <div style={{ fontSize: 12, color: "#aaa", lineHeight: 1.6 }}>
              Вы нажимаете кнопку ниже → пишете менеджеру в Telegram → получаете настройку → оплачиваете 249 ₽ удобным способом.
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 28 }}>
            {[
              { q: "📱 Ваше устройство", hint: "Например: iPhone 13, Samsung S22, Xiaomi" },
              { q: "🎮 Стиль игры", hint: "Агрессивный / Снайпер / Смешанный" },
              { q: "🔄 Гироскоп?", hint: "Да / Нет / Иногда" },
              { q: "🏆 Ваш текущий ранг", hint: "Золото / Платина / Бриллиант / Корона" },
              { q: "👁️ Тип прицела", hint: "Красная точка, 2x, 4x, 6x..." },
            ].map((item, i) => (
              <div key={i}>
                <label style={{ display: "block", fontSize: 13, color: "#ccc", fontWeight: 600, marginBottom: 6 }}>
                  {item.q}
                </label>
                <input
                  type="text"
                  placeholder={item.hint}
                  style={{
                    width: "100%", boxSizing: "border-box",
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 10, padding: "11px 14px",
                    color: "#fff", fontSize: 13,
                    outline: "none",
                  }}
                />
              </div>
            ))}
          </div>

          <button
            onClick={() => setSent(true)}
            style={{
              width: "100%",
              background: "linear-gradient(135deg, #ffb400, #ff7a00)",
              color: "#000", border: "none",
              borderRadius: 14, padding: "15px",
              fontSize: 15, fontWeight: 800, cursor: "pointer",
              boxShadow: "0 4px 24px rgba(255,180,0,0.3)",
            }}
          >
            Написать менеджеру в Telegram
          </button>
          <div style={{ textAlign: "center", fontSize: 11, color: "#555", marginTop: 10 }}>
            Нажимая кнопку, вы перейдёте в Telegram
          </div>
        </div>
      ) : (
        <div style={{ padding: "60px 20px", textAlign: "center" }}>
          <div style={{
            width: 72, height: 72, margin: "0 auto 20px",
            background: "linear-gradient(135deg, #ffb400, #ff7a00)",
            borderRadius: "50%",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Check size={36} color="#000" strokeWidth={3} />
          </div>
          <div style={{ fontSize: 22, fontWeight: 800, marginBottom: 10 }}>Заявка отправлена!</div>
          <div style={{ fontSize: 14, color: "#888", lineHeight: 1.6, marginBottom: 32 }}>
            Менеджер свяжется с вами в Telegram<br />в течение 15 минут
          </div>
          <button
            onClick={onBack}
            style={{
              background: "transparent",
              border: "1px solid rgba(255,180,0,0.4)",
              color: "#ffb400", borderRadius: 12,
              padding: "12px 24px", fontSize: 14,
              fontWeight: 700, cursor: "pointer",
            }}
          >
            На главную
          </button>
        </div>
      )}
    </div>
  );
}
