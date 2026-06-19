// ── Gap Analysis — LLM-powered topic coverage and unanswered query review ─

const AnalysisPage = ({ t, theme, language }) => {
  const isDark = theme === "dark";
  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";
  const isAr = language === "ar";

  // الألوان المشتقة من اللون الأساسي
  const topics = [
    { nameKey: "hrPolicies", covered: 92, queries: 340, color: "#1A9BB3" }, // اللون الأساسي
    { nameKey: "productFeatures", covered: 78, queries: 280, color: "#25A9C2" }, // درجة أفتح
    { nameKey: "onboarding", covered: 85, queries: 210, color: "#3D81F6" }, // اللون الثانوي
    { nameKey: "technicalDocs", covered: 61, queries: 190, color: "#5294FF" }, // درجة أفتح من الثانوي
    { nameKey: "legalCompliance", covered: 34, queries: 150, color: "#158296" }, // درجة أغمق
    { nameKey: "billingFinance", covered: 20, queries: 120, color: "#0E5C6A" }, // درجة أغمق جداً
  ];

  const unanswered = [
    {
      q: "What is the refund policy for enterprise plans?",
      qAr: "ما هي سياسة الاسترداد لخطط المؤسسات؟",
      hits: 0,
      confidence: 0.12,
    },
    {
      q: "How to configure SSO with Okta?",
      qAr: "كيفية إعداد SSO مع Okta؟",
      hits: 1,
      confidence: 0.31,
    },
    {
      q: "Data retention period under GDPR?",
      qAr: "مدة الاحتفاظ بالبيانات وفق GDPR؟",
      hits: 0,
      confidence: 0.08,
    },
    {
      q: "Invoice generation for custom contracts?",
      qAr: "كيفية إنشاء فاتورة للعقود المخصصة؟",
      hits: 0,
      confidence: 0.15,
    },
    {
      q: "How to appeal a performance review?",
      qAr: "كيفية الاعتراض على تقييم الأداء؟",
      hits: 2,
      confidence: 0.42,
    },
  ];

  return (
    <div
      className="content"
      style={{
        padding: "24px",
        backgroundColor: isDark ? "#121212" : "#ffffff",
        minHeight: "100vh",
        transition: "all 0.4s",
      }}
    >
      <div
        className="grid-2"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: "24px",
          marginBottom: "24px",
        }}
      >
        {/* ── Topic coverage bars ── */}
        <div
          className="card"
          style={{
            backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
            borderRadius: "20px",
            border: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
            padding: "24px",
          }}
        >
          <div
            className="card-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "20px",
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
              {t("topicCoverage")}
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
              {t("reAnalyze")}
            </span>
          </div>
          <div className="card-body">
            {topics.map((topic, i) => (
              <div key={i} style={{ marginBottom: "20px" }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "6px",
                  }}
                >
                  <span
                    style={{
                      fontSize: "13px",
                      fontWeight: "bold",
                      color: isDark ? "#eee" : "#374151",
                    }}
                  >
                    {t(topic.nameKey)}
                  </span>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <span style={{ fontSize: "11px", color: "#9ca3af" }}>
                      {topic.queries} {t("queries")}
                    </span>
                    <span
                      style={{
                        fontSize: "13px",
                        fontWeight: "900",
                        color: topic.color,
                      }}
                    >
                      {topic.covered}%
                    </span>
                  </div>
                </div>
                <div
                  className="coverage-bar"
                  style={{
                    height: "8px",
                    background: isDark ? "#333" : "#f3f4f6",
                    borderRadius: "10px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    className="coverage-fill"
                    style={{
                      width: `${topic.covered}%`,
                      height: "100%",
                      background: topic.color,
                      borderRadius: "10px",
                      transition: "width 1s ease-in-out",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Coverage donut ── */}
        <div
          className="card"
          style={{
            backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
            borderRadius: "20px",
            border: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
            padding: "24px",
          }}
        >
          <div
            className="card-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "20px",
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
              {t("coverageOverview")}
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
              {t("fullReport")}
            </span>
          </div>
          <div
            className="card-body"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "20px",
              paddingTop: "10px",
            }}
          >
            {/* Donut Chart يستخدم تدرج الهوية */}
            <div
              style={{ position: "relative", width: "150px", height: "150px" }}
            >
              <DonutChart
                segments={[
                  { pct: 68, color: primaryColor },
                  { pct: 20, color: secondaryColor },
                  { pct: 12, color: isDark ? "#444" : "#e5e7eb" },
                ]}
              />
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "10px",
                width: "100%",
              }}
            >
              {[
                { labelKey: "wellCovered", color: primaryColor, pct: "68%" },
                {
                  labelKey: "partialCoverage",
                  color: secondaryColor,
                  pct: "20%",
                },
                {
                  labelKey: "gapDetected",
                  color: isDark ? "#666" : "#9ca3af",
                  pct: "12%",
                },
              ].map((l, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    fontSize: "12px",
                  }}
                >
                  <span
                    style={{
                      width: "10px",
                      height: "10px",
                      borderRadius: "50%",
                      background: l.color,
                      flexShrink: 0,
                    }}
                  />
                  <span
                    style={{
                      flex: 1,
                      fontWeight: "bold",
                      color: isDark ? "#aaa" : "#6b7280",
                    }}
                  >
                    {t(l.labelKey)}
                  </span>
                  <span style={{ fontWeight: "900", color: l.color }}>
                    {l.pct}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Low-confidence query list ── */}
      <div
        className="card"
        style={{
          backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
          borderRadius: "20px",
          border: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
          padding: "8px 0",
        }}
      >
        <div
          className="card-header"
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "20px 24px",
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
            {t("unansweredQueries")}
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
            {t("exportGaps")}
          </span>
        </div>
        <div className="card-body">
          {unanswered.map((u, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "14px",
                padding: "16px 24px",
                borderBottom:
                  i < unanswered.length - 1
                    ? `1px solid ${isDark ? "#333" : "#f3f4f6"}`
                    : "none",
                transition: "background 0.2s",
              }}
            >
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontSize: "14px",
                    fontWeight: "bold",
                    color: isDark ? "#eee" : "#374151",
                    marginBottom: "4px",
                  }}
                >
                  {isAr ? u.qAr : u.q}
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: "#9ca3af",
                    fontWeight: "500",
                  }}
                >
                  {u.hits} {t("matchingChunks")} · {t("confidence")}{" "}
                  <span
                    style={{
                      color: u.confidence < 0.2 ? "#ff4d4f" : primaryColor,
                    }}
                  >
                    {Math.round(u.confidence * 100)}%
                  </span>
                </div>
              </div>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  style={{
                    backgroundColor: "transparent",
                    border: `1px solid ${primaryColor}`,
                    color: primaryColor,
                    padding: "6px 12px",
                    borderRadius: "8px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    cursor: "pointer",
                  }}
                >
                  {t("suggestDoc")}
                </button>
                <button
                  style={{
                    backgroundColor: isDark ? "#333" : "#f3f4f6",
                    border: "none",
                    color: isDark ? "#aaa" : "#6b7280",
                    padding: "6px 12px",
                    borderRadius: "8px",
                    fontSize: "11px",
                    fontWeight: "bold",
                    cursor: "pointer",
                  }}
                >
                  {t("dismiss")}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
