// ── Topbar — sticky header with page title, theme switch, lang, notifications

const Topbar = ({ title, dark, setDark, lang, setLang, theme }) => {
  const isAr = lang === "ar";
  const isDark = theme === "dark";
  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";

  const topbarStyle = {
    height: "70px",
    backgroundColor: isDark ? "#121212" : "#ffffff",
    borderBottom: `1px solid ${isDark ? "rgba(255,255,255,0.05)" : "#f3f4f6"}`,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 24px",
    position: "sticky",
    top: 0,
    zIndex: 100,
    transition: "all 0.3s ease",
  };

  return (
    <header className="topbar" style={topbarStyle}>
      <h1
        className="page-title"
        style={{
          fontSize: "20px",
          fontWeight: "900",
          margin: 0,
          color: isDark ? "#ffffff" : "#121212",
          letterSpacing: "-0.5px",
        }}
      >
        {title}
      </h1>

      <div
        className="topbar-right"
        style={{ display: "flex", alignItems: "center", gap: "20px", direction: "ltr" }}
      >
        {/* Dark / light mode toggle */}
        <div
          className="theme-toggle"
          style={{ display: "flex", alignItems: "center", gap: "10px" }}
        >
          <Icon.Sun
            size={18}
            style={{ color: isDark ? "#4b5563" : primaryColor }}
          />
          <label
            className="toggle-wrap"
            style={{ position: "relative", width: "40px", height: "22px" }}
          >
            <input
              type="checkbox"
              style={{ opacity: 0, width: 0, height: 0 }}
              checked={dark}
              onChange={(e) => setDark(e.target.checked)}
            />
            <span
              style={{
                position: "absolute",
                cursor: "pointer",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: dark ? primaryColor : "#e5e7eb",
                transition: "0.4s",
                borderRadius: "34px",
              }}
            >
              <span
                style={{
                  position: "absolute",
                  height: "16px",
                  width: "16px",
                  left: dark ? "20px" : "4px",
                  bottom: "3px",
                  backgroundColor: "white",
                  transition: "0.4s",
                  borderRadius: "50%",
                }}
              />
            </span>
          </label>
          <Icon.Moon
            size={18}
            style={{ color: isDark ? primaryColor : "#9ca3af" }}
          />
        </div>

        {/* Language switcher — EN <-> AR */}
        <button
          className="lang-btn"
          onClick={() => setLang(isAr ? "en" : "ar")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            backgroundColor: isDark ? "rgba(255,255,255,0.05)" : "#f3f4f6",
            border: `1px solid ${isDark ? "#333" : "#e5e7eb"}`,
            padding: "6px 14px",
            borderRadius: "10px",
            cursor: "pointer",
            color: "inherit",
            fontWeight: "bold",
            fontSize: "13px",
            transition: "0.3s",
          }}
        >
          <span style={{ color: primaryColor, fontWeight: "900" }}>
            {isAr ? "EN" : "AR"}
          </span>
          {isAr ? "English" : "العربية"}
        </button>

        {/* Notifications */}
        <button
          className="notif-btn"
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            position: "relative",
            color: isDark ? "#9ca3af" : "#6b7280",
            padding: "5px",
            display: "flex",
            alignItems: "center",
          }}
        >
          <Icon.Bell size={22} />
          <span
            className="notif-dot"
            style={{
              position: "absolute",
              top: "5px",
              right: "5px",
              width: "8px",
              height: "8px",
              backgroundColor: "#ff4d4f",
              borderRadius: "50%",
              border: `2px solid ${isDark ? "#121212" : "#ffffff"}`,
            }}
          />
        </button>
      </div>
    </header>
  );
};
