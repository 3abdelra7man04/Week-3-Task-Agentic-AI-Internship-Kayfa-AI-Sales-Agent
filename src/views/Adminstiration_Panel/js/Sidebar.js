const Sidebar = ({ page, setPage, t, theme, language, content }) => {
  const isDark = theme === "dark";
  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";
  const isRTL = language === "ar";

  const NAV_ITEMS = [
    { id: "dashboard", labelKey: "dashboard", icon: "Dashboard" },
    { id: "knowledge", labelKey: "knowledgeBase", icon: "Database" },
    { id: "analysis", labelKey: "gapAnalysis", icon: "Analysis" },
    { id: "inbox", labelKey: "queryInbox", icon: "Inbox" },
    { id: "admins", labelKey: "admins", icon: "Admins" },
    { id: "settings", labelKey: "settings", icon: "Settings" },
  ];

  const sidebarStyle = {
    backgroundColor: isDark ? "#121212" : "#ffffff",
    // الحدود تكون فقط من جهة واحدة للفصل بين السايدبار والمحتوى
    borderRight: isRTL
      ? "none"
      : `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "#eeeeee"}`,
    borderLeft: isRTL
      ? `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "#eeeeee"}`
      : "none",
    color: isDark ? "#ffffff" : "#374151",
    transition: "all 0.4s ease",
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    width: "280px",
    minWidth: "280px",
    margin: 0, // تصفير المسافة تماماً
    padding: 0,
    zIndex: 50,
    position: "relative",
  };

  return (
    <aside className="sidebar" style={sidebarStyle}>
      {/* Logo Section - ملتصق بالأعلى */}
      <div
        className="logo"
        style={{ padding: "35px 24px", display: "flex", alignItems: "center" }}
      >
        <p
          style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: "36px",
            fontWeight: "900",
            letterSpacing: "-0.05em",
            margin: 0,
            display: "flex",
            alignItems: "center",
            direction: "ltr",
          }}
        >
          <span style={{ color: isDark ? "#ffffff" : "#1f2937" }}>Uni</span>
          <span
            style={{
              background: "linear-gradient(to right, #1A9BB3, #3D81F6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Ask
          </span>
        </p>
      </div>

      <nav className="nav" style={{ flex: 1, padding: "0 10px" }}>
        <div
          className="nav-label"
          style={{
            fontSize: "10px",
            fontWeight: "bold",
            textTransform: "uppercase",
            color: isDark ? "#4b5563" : "#9ca3af",
            padding: "15px",
            letterSpacing: "1px",
          }}
        >
          {t("mainMenu")}
        </div>

        {NAV_ITEMS.map(({ id, labelKey, icon }) => {
          const I = Icon[icon];
          const isActive = page === id;

          return (
            <div
              key={id}
              className={`nav-item${isActive ? " active" : ""}`}
              onClick={() => setPage(id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "12px 20px",
                margin: "2px 8px",
                borderRadius: "10px", // حواف خفيفة للعناصر الداخلية فقط
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: isActive ? "bold" : "500",
                transition: "all 0.2s",
                backgroundColor: isActive ? `${primaryColor}10` : "transparent",
                color: isActive ? primaryColor : isDark ? "#9ca3af" : "#6b7280",
              }}
            >
              <I size={18} />
              <span style={{ flex: 1 }}>{t(labelKey)}</span>
            </div>
          );
        })}
      </nav>

      {/* Footer - ملتصق بالأسفل تماماً */}
      <div
        className="sidebar-footer"
        style={{
          padding: "20px",
          borderTop: `1px solid ${isDark ? "rgba(255,255,255,0.05)" : "#f3f4f6"}`,
        }}
      >
        <div
          className="user-card"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            backgroundColor: isDark ? "rgba(255,255,255,0.03)" : "#f9fafb",
            padding: "12px",
            borderRadius: "12px",
          }}
        >
          <div
            className="avatar"
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              background: `linear-gradient(135deg, ${primaryColor}, ${secondaryColor})`,
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "bold",
            }}
          >
            AJ
          </div>
          <div style={{ overflow: "hidden" }}>
            <div
              className="user-name"
              style={{ fontSize: "13px", fontWeight: "bold" }}
            >
              Abanoub Wagih
            </div>
            <div
              className="user-role"
              style={{ fontSize: "11px", color: "#9ca3af" }}
            >
              {t("seniorRagAdmin")}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
