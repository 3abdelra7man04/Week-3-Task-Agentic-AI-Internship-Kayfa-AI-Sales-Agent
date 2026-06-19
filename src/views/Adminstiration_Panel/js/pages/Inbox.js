// ── Query Inbox — paginated log of user queries with confidence + feedback ─

const InboxPage = ({ t, lang, theme }) => {
  const isDark = theme === "dark";
  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";
  const isAr = lang === "ar";

  // BACKEND: GET /api/queries?page=1&limit=20 → paginated query history
  const queries = [
    {
      id: 1,
      q: "What is the vacation policy?",
      qAr: "ما هي سياسة الإجازات؟",
      answer: "According to Company Policy 2024…",
      answerAr: "وفقاً لسياسة الشركة 2024…",
      confidence: 0.94,
      source: "Company Policy 2024.pdf",
      time: "2 min ago",
      liked: true,
    },
    {
      id: 2,
      q: "How do I reset my password?",
      qAr: "كيف أعيد تعيين كلمة المرور؟",
      answer: "To reset your password, navigate to…",
      answerAr: "لإعادة تعيين كلمة المرور، انتقل إلى…",
      confidence: 0.88,
      source: "Onboarding Guide.md",
      time: "8 min ago",
      liked: null,
    },
    {
      id: 3,
      q: "What are the enterprise billing options?",
      qAr: "ما هي خيارات الفوترة للمؤسسات؟",
      answer: "I could not find a confident answer…",
      answerAr: "لم أجد إجابة واثقة…",
      confidence: 0.15,
      source: null,
      time: "23 min ago",
      liked: false,
    },
    {
      id: 4,
      q: "Explain the code review process",
      qAr: "اشرح عملية مراجعة الكود",
      answer: "The engineering runbook states…",
      answerAr: "تنص وثيقة التشغيل الهندسي على…",
      confidence: 0.79,
      source: "Engineering Runbook.txt",
      time: "1 hour ago",
      liked: true,
    },
  ];

  // دالة تحديد لون الثقة بناءً على الهوية
  const confColor = (c) =>
    c > 0.7 ? primaryColor : c > 0.4 ? secondaryColor : "#ff4d4f";

  const cardStyle = {
    backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
    border: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
    borderRadius: "15px",
    transition: "all 0.3s ease",
  };

  return (
    <div
      className="content"
      style={{
        padding: "24px",
        backgroundColor: isDark ? "#121212" : "#ffffff",
        minHeight: "100vh",
      }}
    >
      {/* ── Summary row ── */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
        {[
          { labelKey: "totalToday", value: "143", color: primaryColor },
          { labelKey: "highConfidence", value: "118", color: primaryColor },
          { labelKey: "lowConfidence", value: "25", color: "#ff4d4f" },
          { labelKey: "avgConfidence", value: "81%", color: secondaryColor },
        ].map((s, i) => (
          <div
            key={i}
            style={{
              ...cardStyle,
              padding: "16px 20px",
              flex: 1,
              display: "flex",
              flexDirection: "column",
              gap: "4px",
            }}
          >
            <div
              style={{
                fontSize: "10px",
                color: "#9ca3af",
                fontWeight: "bold",
                textTransform: "uppercase",
                letterSpacing: "1px",
              }}
            >
              {t(s.labelKey)}
            </div>
            <div
              style={{ fontSize: "24px", fontWeight: "900", color: s.color }}
            >
              {s.value}
            </div>
          </div>
        ))}
      </div>

      {/* ── Query list ── */}
      <div className="card" style={cardStyle}>
        <div
          className="card-header"
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "20px 24px",
            borderBottom: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
          }}
        >
          <span
            className="card-title"
            style={{
              fontWeight: "900",
              fontSize: "18px",
              color: isDark ? "#fff" : "#121212",
            }}
          >
            {t("recentQueries")}
          </span>
          <span
            className="card-action"
            style={{
              fontSize: "12px",
              color: primaryColor,
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            {t("exportLog")}
          </span>
        </div>

        {queries.map((q, i) => (
          <div
            key={q.id}
            style={{
              padding: "20px 24px",
              borderBottom:
                i < queries.length - 1
                  ? `1px solid ${isDark ? "#333" : "#f3f4f6"}`
                  : "none",
              transition: "background 0.2s",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: "8px",
              }}
            >
              <div
                style={{
                  fontWeight: "bold",
                  fontSize: "15px",
                  color: isDark ? "#eee" : "#374151",
                }}
              >
                {isAr ? q.qAr : q.q}
              </div>
              <div
                style={{
                  display: "flex",
                  gap: "12px",
                  alignItems: "center",
                  marginLeft: isAr ? 0 : "16px",
                  marginRight: isAr ? "16px" : 0,
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    fontSize: "12px",
                    fontWeight: "900",
                    color: confColor(q.confidence),
                  }}
                >
                  {Math.round(q.confidence * 100)}% {t("conf")}
                </span>
                <span
                  style={{
                    fontSize: "11px",
                    color: "#9ca3af",
                    fontWeight: "500",
                  }}
                >
                  {q.time}
                </span>
              </div>
            </div>

            <div
              style={{
                fontSize: "13px",
                color: isDark ? "#aaa" : "#6b7280",
                marginBottom: "12px",
                lineHeight: 1.6,
              }}
            >
              {(isAr ? q.answerAr : q.answer).slice(0, 110)}…
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              {q.source && (
                <span
                  style={{
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    backgroundColor: `${primaryColor}15`,
                    color: primaryColor,
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                  }}
                >
                  <Icon.Doc size={12} /> {q.source}
                </span>
              )}

              {q.liked === true && (
                <span
                  style={{
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    backgroundColor: "#f0fdf4",
                    color: "#166534",
                  }}
                >
                  {t("helpful")}
                </span>
              )}
              {q.liked === false && (
                <span
                  style={{
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    backgroundColor: "#fef2f2",
                    color: "#991b1b",
                  }}
                >
                  {t("unhelpful")}
                </span>
              )}

              <button
                style={{
                  marginLeft: isAr ? 0 : "auto",
                  marginRight: isAr ? "auto" : 0,
                  backgroundColor: "transparent",
                  border: "none",
                  color: primaryColor,
                  fontWeight: "bold",
                  fontSize: "12px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "5px",
                }}
              >
                <Icon.Eye size={14} /> {t("viewFull")}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
