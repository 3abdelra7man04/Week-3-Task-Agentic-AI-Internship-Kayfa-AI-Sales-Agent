const DashboardPage = ({ t, theme, lang }) => {
  const isDark = theme === "dark";
  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";
  const cardBackground = isDark ? "#1e1e1e" : "#ffffff";
  const bodyBackground = isDark ? "#121212" : "#ffffff";
  const textColor = isDark ? "#ffffff" : "#374151";
  const subText = isDark ? "#9ca3af" : "#6b7280";
  const borderColor = isDark ? "#333333" : "#f3f4f6";

  const stats = [
    {
      labelKey: "indexedDocuments",
      value: "2,769",
      delta: "+12% " + t("thisWeek").replace("{n}", ""),
      up: true,
      sparkData: [20, 35, 28, 45, 38, 52, 48, 60, 55, 70],
      color: primaryColor,
    },
    {
      labelKey: "queriesAnswered",
      value: "14,382",
      delta: "+8% " + t("thisWeek").replace("{n}", ""),
      up: true,
      sparkData: [80, 72, 90, 85, 95, 100, 92, 108, 115, 120],
      color: secondaryColor,
    },
    {
      labelKey: "avgResponseTime",
      value: "1.4s",
      delta: "-0.2s " + t("improved").replace("{n}", ""),
      up: true,
      sparkData: [2.1, 1.9, 2.0, 1.8, 1.7, 1.6, 1.5, 1.5, 1.4, 1.4],
      color: primaryColor,
    },
    {
      labelKey: "failedQueries",
      value: "47",
      delta: "+3 " + t("sincYesterday").replace("{n}", ""),
      up: false,
      sparkData: [30, 28, 35, 25, 20, 30, 28, 40, 38, 47],
      color: "#ff4d4f",
    },
  ];

  // BACKEND: GET /api/queries/daily?range=7d
  const barData = [
    { l: t("mon"), v: 42 },
    { l: t("tue"), v: 68 },
    { l: t("wed"), v: 55 },
    { l: t("thu"), v: 80 },
    { l: t("fri"), v: 73 },
    { l: t("sat"), v: 30 },
    { l: t("sun"), v: 25 },
  ];

  const activityData = [
    {
      icon: "doc",
      title: t("actDocumentIndexed"),
      sub: t("actDocIndexedSub"),
      time: "2 min ago",
      color: isDark ? "rgba(26,155,179,0.1)" : "#e8f1ff",
      iconColor: primaryColor,
    },
    {
      icon: "chat",
      title: t("actQueryAnswered"),
      sub: t("actQueryAnsweredSub"),
      time: "15 min ago",
      color: isDark ? "rgba(61,129,246,0.1)" : "#e0faf4",
      iconColor: secondaryColor,
    },
    {
      icon: "doc",
      title: t("actDocumentUploaded"),
      sub: t("actDocUploadedSub"),
      time: "1 hour ago",
      color: isDark ? "rgba(26,155,179,0.1)" : "#e8f1ff",
      iconColor: primaryColor,
    },
    {
      icon: "warn",
      title: t("actIndexError"),
      sub: t("actIndexErrorSub"),
      time: "3 hours ago",
      color: isDark ? "rgba(255,77,79,0.1)" : "#fff1f0",
      iconColor: "#ff4d4f",
    },
    {
      icon: "admin",
      title: t("actAdminAdded"),
      sub: t("actAdminAddedSub"),
      time: "2 days ago",
      color: isDark ? "rgba(155,89,182,0.1)" : "#fdf3ff",
      iconColor: "#9b59b6",
    },
  ];

  const topSources = [
    {
      name: lang === "ar" ? "سياسة الشركة 2024.pdf" : "Company Policy 2024.pdf",
      queries: 1240,
      pct: 100,
    },
    {
      name: lang === "ar" ? "دليل المنتج Q3.docx" : "Product Handbook Q3.docx",
      queries: 870,
      pct: 70,
    },
    {
      name: lang === "ar" ? "دليل الإعداد.md" : "Onboarding Guide.md",
      queries: 540,
      pct: 44,
    },
    {
      name: lang === "ar" ? "دفتر تشغيل الهندسة.txt" : "Engineering Runbook.txt",
      queries: 320,
      pct: 26,
    },
  ];

  return (
    <div
      className="content"
      style={{
        backgroundColor: bodyBackground,
        color: textColor,
        padding: "20px",
        transition: "all 0.3s",
      }}
    >
      {/* ── Stat Cards ── */}
      <div
        className="stats-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        {stats.map((s, i) => (
          <div
            key={i}
            className="stat-card"
            style={{
              backgroundColor: cardBackground,
              border: `1px solid ${borderColor}`,
              padding: "20px",
              borderRadius: "15px",
            }}
          >
            <div
              className="stat-icon"
              style={{
                background: s.color + "22",
                padding: "10px",
                borderRadius: "10px",
                display: "inline-block",
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={s.color} strokeWidth="2">
                {i === 0 && (<><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>)}
                {i === 1 && (<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />)}
                {i === 2 && (<><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></>)}
                {i === 3 && (<><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></>)}
              </svg>
            </div>
            <div className="stat-label" style={{ color: subText, fontSize: "12px", marginTop: "10px" }}>
              {t(s.labelKey)}
            </div>
            <div className="stat-value" style={{ fontSize: "24px", fontWeight: "bold" }}>
              {s.value}
            </div>
            <div className={`stat-delta ${s.up ? "up" : "down"}`} style={{ color: s.up ? "#2ecc71" : "#ff4d4f", fontSize: "11px" }}>
              {s.delta}
            </div>
            <Sparkline data={s.sparkData} color={s.color} />
          </div>
        ))}
      </div>

      {/* ── Weekly chart + Activity feed ── */}
      <div
        className="grid-2"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "20px",
          marginBottom: "20px",
        }}
      >
        <div
          className="card"
          style={{ backgroundColor: cardBackground, border: `1px solid ${borderColor}`, padding: "20px", borderRadius: "15px" }}
        >
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
            <span className="card-title" style={{ fontWeight: "bold" }}>{t("queriesThisWeek")}</span>
            <span className="card-action" style={{ color: primaryColor, fontSize: "12px", cursor: "pointer" }}>{t("exportCsv")}</span>
          </div>
          <div className="card-body">
            <BarChart data={barData} color={primaryColor} />
          </div>
        </div>

        <div
          className="card"
          style={{ backgroundColor: cardBackground, border: `1px solid ${borderColor}`, padding: "20px", borderRadius: "15px" }}
        >
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
            <span className="card-title" style={{ fontWeight: "bold" }}>{t("recentActivity")}</span>
            <span className="card-action" style={{ color: primaryColor, fontSize: "12px", cursor: "pointer" }}>{t("viewAll")}</span>
          </div>
          <div className="card-body" style={{ padding: "0px" }}>
            {activityData.map((a, i) => (
              <div key={i} className="activity-item" style={{ display: "flex", gap: "12px", marginBottom: "15px", alignItems: "center" }}>
                <div className="act-icon" style={{ background: a.color, padding: "8px", borderRadius: "8px" }}>
                  <svg width="14" height="14" fill="none" stroke={a.iconColor} strokeWidth="2" viewBox="0 0 24 24">
                    {a.icon === "doc" && (<><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>)}
                    {a.icon === "chat" && (<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />)}
                    {a.icon === "warn" && (<><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></>)}
                    {a.icon === "admin" && (<><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /></>)}
                  </svg>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="act-title" style={{ fontSize: "13px", fontWeight: "bold" }}>{a.title}</div>
                  <div className="act-sub" style={{ fontSize: "11px", color: subText, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.sub}</div>
                </div>
                <div className="act-time" style={{ fontSize: "10px", color: subText }}>{a.time}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Top queried sources ── */}
      <div
        className="card"
        style={{ backgroundColor: cardBackground, border: `1px solid ${borderColor}`, padding: "20px", borderRadius: "15px" }}
      >
        <div className="card-header" style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
          <span className="card-title" style={{ fontWeight: "bold" }}>{t("topQueriedSources")}</span>
          <span className="card-action" style={{ color: primaryColor, fontSize: "12px", cursor: "pointer" }}>{t("manageDocs")}</span>
        </div>
        <div className="card-body">
          {topSources.map((d, i) => (
            <div key={i} style={{ marginBottom: "14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
                <span style={{ fontSize: "13px", color: textColor }}>{d.name}</span>
                <span style={{ fontSize: "12px", color: subText }}>{d.queries.toLocaleString()} {t("queries")}</span>
              </div>
              <div className="progress-bar" style={{ background: isDark ? "#333" : "#eee", height: "6px", borderRadius: "10px", overflow: "hidden" }}>
                <div className="progress-fill" style={{ width: `${d.pct}%`, background: primaryColor, height: "100%" }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};