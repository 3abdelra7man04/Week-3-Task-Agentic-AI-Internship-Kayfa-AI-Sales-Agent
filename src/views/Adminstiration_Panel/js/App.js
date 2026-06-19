// ── App — root component: routing, dark mode, language, RTL, ReactDOM mount

const App = () => {
  const { useState, useEffect } = React;

  // ── Auth state ────────────────────────────────────────────────────────
  // null = not signed in  |  { userId, email } = signed in
  const [user, setUser] = useState({ userId: "dev", email: "admin@university.edu" });

  // ── UI state ──────────────────────────────────────────────────────────
  const [page, setPage] = useState("dashboard");
  const [dark, setDark] = useState(false);
  const [lang, setLang] = useState("en"); // 'en' | 'ar'

  const t        = makeT(lang);
  const isAr     = lang === "ar";
  const theme    = dark ? "dark" : "light";
  const language = lang;

  // Apply dark mode class and RTL direction to <html>
  useEffect(() => {
    document.documentElement.dir = isAr ? "rtl" : "ltr";
    document.documentElement.lang = lang;
    document.body.className = dark ? "dark" : "";
    document.body.style.margin  = "0";
    document.body.style.padding = "0";
  }, [dark, lang]);

  // ── Handlers ──────────────────────────────────────────────────────────
  const handleSignIn   = (userData) => setUser(userData);
  const handleSignOut  = () => { setUser(null); setPage("dashboard"); };
  const toggleTheme    = () => setDark((d) => !d);

  // ── Sign-in gate ──────────────────────────────────────────────────────
  if (!user) {
    return (
      <SignInPage
        theme={theme}
        toggleTheme={toggleTheme}
        onSignIn={handleSignIn}
      />
    );
  }

  // ── Dashboard shell ───────────────────────────────────────────────────
  const PAGE_TITLES_LOCAL = {
    dashboard: t("dashboard"),
    knowledge: t("knowledgeBase"),
    analysis:  t("gapAnalysis"),
    inbox:     t("queryInbox"),
    admins:    t("admins"),
    settings:  t("settings"),
  };

  const renderPage = () => {
    const props = { t, lang, theme, language };
    switch (page) {
      case "dashboard": return <DashboardPage {...props} />;
      case "knowledge": return <KnowledgePage {...props} />;
      case "analysis":  return <AnalysisPage  {...props} />;
      case "inbox":     return <InboxPage     {...props} />;
      case "admins":    return <AdminsPage    {...props} />;
      case "settings":  return <SettingsPage  {...props} />;
      default:          return <DashboardPage {...props} />;
    }
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        margin: 0,
        padding: 0,
        overflow: "hidden",
        backgroundColor: dark ? "#0d1117" : "#f0f2f7",
      }}
    >
      <Sidebar
        page={page}
        setPage={setPage}
        t={t}
        theme={theme}
        language={language}
        user={user}
        onSignOut={handleSignOut}
      />

      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <Topbar
          title={PAGE_TITLES_LOCAL[page]}
          dark={dark}
          setDark={setDark}
          lang={lang}
          setLang={setLang}
          theme={theme}
        />

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            backgroundColor: dark ? "#0d1117" : "#f0f2f7",
            padding: "0",
          }}
        >
          {renderPage()}
        </div>
      </main>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
