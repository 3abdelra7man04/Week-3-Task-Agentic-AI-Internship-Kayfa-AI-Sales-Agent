// ── SignIn Page — UniAsk Administration Portal ────────────────────────────
const SignInPage = ({ onSignIn, theme, toggleTheme }) => {
  const { useState } = React;

  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState("");

  const isDark = theme === "dark";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/api/v1/admin/login/1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const data = await res.json();

      if (res.ok) {
        onSignIn({ userId: data.user_id, email: email.trim() });
      } else {
        setError("Invalid email or password. Please try again.");
      }
    } catch {
      setError("Cannot reach the server. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: isDark ? "#121212" : "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'DM Sans', sans-serif",
        padding: "20px",
        position: "relative",
        transition: "background 0.4s ease",
      }}
    >
      {/* ── Theme toggle ─────────────────────────────────────────────── */}
      <button
        onClick={toggleTheme}
        title={isDark ? "Switch to Light" : "Switch to Dark"}
        style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          width: "38px",
          height: "38px",
          borderRadius: "10px",
          border: `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "#eeeeee"}`,
          background: isDark ? "#1e1e1e" : "#ffffff",
          color: isDark ? "#9ca3af" : "#6b7280",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "all 0.3s ease",
          zIndex: 10,
        }}
      >
        {isDark ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1"  x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22"  y1="4.22"  x2="5.64"  y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1"  y1="12" x2="3"  y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22"  y1="19.78" x2="5.64"  y2="18.36"/>
            <line x1="18.36" y1="5.64"  x2="19.78" y2="4.22"/>
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        )}
      </button>

      {/* ── Card ─────────────────────────────────────────────────────── */}
      <div
        style={{
          width: "100%",
          maxWidth: "440px",
          backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
          borderRadius: "14px",
          border: `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "#e4e8f0"}`,
          boxShadow: isDark
            ? "0 24px 64px rgba(0,0,0,0.5)"
            : "0 24px 64px rgba(15,28,46,0.10)",
          padding: "44px 40px 40px",
          transition: "background 0.4s ease, border-color 0.4s ease",
        }}
      >
        {/* ── UniAsk Logo — identical to Sidebar ────────────────────── */}
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <p
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: "36px",
              fontWeight: "900",
              letterSpacing: "-0.05em",
              margin: 0,
              lineHeight: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
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
          <div
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "11px",
              fontWeight: "600",
              textTransform: "uppercase",
              letterSpacing: "2.5px",
              color: isDark ? "#4b5563" : "#9ca3af",
              marginTop: "8px",
            }}
          >
            Administration Portal
          </div>
        </div>

        {/* ── Heading ───────────────────────────────────────────────── */}
        <h1
          style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: "26px",
            fontWeight: "800",
            color: isDark ? "#ffffff" : "#1f2937",
            margin: "0 0 6px",
            textAlign: "center",
          }}
        >
          Sign In
        </h1>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "14px",
            color: isDark ? "#9ca3af" : "#6b7280",
            textAlign: "center",
            marginBottom: "32px",
            fontWeight: "400",
          }}
        >
          Get access to the UniAsk Administration Portal
        </p>

        {/* ── Error banner ──────────────────────────────────────────── */}
        {error && (
          <div
            style={{
              backgroundColor: isDark ? "#2c1515" : "#fff1f0",
              border: `1px solid ${isDark ? "#ff6b6b" : "#ff4d4f"}`,
              borderRadius: "8px",
              padding: "12px 16px",
              marginBottom: "20px",
              fontSize: "13px",
              fontFamily: "'DM Sans', sans-serif",
              color: isDark ? "#ff6b6b" : "#ff4d4f",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8"  x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* ── Email field ───────────────────────────────────────── */}
          <div style={{ marginBottom: "18px" }}>
            <label
              htmlFor="signin-email"
              style={{
                display: "block",
                fontSize: "12px",
                fontWeight: "600",
                color: isDark ? "#9ca3af" : "#6b7280",
                marginBottom: "7px",
                fontFamily: "'DM Sans', sans-serif",
              }}
            >
              Email
            </label>
            <input
              id="signin-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@university.edu"
              autoComplete="email"
              style={{
                width: "100%",
                padding: "11px 14px",
                borderRadius: "10px",
                border: `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "#e4e8f0"}`,
                backgroundColor: isDark ? "#121212" : "#f0f2f7",
                color: isDark ? "#ffffff" : "#1f2937",
                fontSize: "14px",
                fontFamily: "'DM Sans', sans-serif",
                outline: "none",
                transition: "border-color 0.3s",
                boxSizing: "border-box",
              }}
              onFocus={(e) => (e.target.style.borderColor = "#1A9BB3")}
              onBlur={(e)  => (e.target.style.borderColor = isDark ? "rgba(255,255,255,0.1)" : "#e4e8f0")}
            />
          </div>

          {/* ── Password field ────────────────────────────────────── */}
          <div style={{ marginBottom: "28px" }}>
            <label
              htmlFor="signin-password"
              style={{
                display: "block",
                fontSize: "12px",
                fontWeight: "600",
                color: isDark ? "#9ca3af" : "#6b7280",
                marginBottom: "7px",
                fontFamily: "'DM Sans', sans-serif",
              }}
            >
              Password
            </label>
            <div style={{ position: "relative" }}>
              <input
                id="signin-password"
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                style={{
                  width: "100%",
                  padding: "11px 42px 11px 14px",
                  borderRadius: "10px",
                  border: `1px solid ${isDark ? "rgba(255,255,255,0.1)" : "#e4e8f0"}`,
                  backgroundColor: isDark ? "#121212" : "#f0f2f7",
                  color: isDark ? "#ffffff" : "#1f2937",
                  fontSize: "14px",
                  fontFamily: "'DM Sans', sans-serif",
                  outline: "none",
                  transition: "border-color 0.3s",
                  boxSizing: "border-box",
                }}
                onFocus={(e) => (e.target.style.borderColor = "#1A9BB3")}
                onBlur={(e)  => (e.target.style.borderColor = isDark ? "rgba(255,255,255,0.1)" : "#e4e8f0")}
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                style={{
                  position: "absolute",
                  right: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: isDark ? "#4b5563" : "#9ca3af",
                  padding: "2px",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                {showPass ? (
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* ── Submit button ─────────────────────────────────────── */}
          <button
            id="signin-submit-btn"
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "13px",
              borderRadius: "10px",
              border: "none",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              fontSize: "15px",
              fontWeight: "700",
              fontFamily: "'DM Sans', sans-serif",
              color: "#ffffff",
              letterSpacing: "0.2px",
              background: loading
                ? (isDark ? "#4b5563" : "#9ca3af")
                : "linear-gradient(135deg, #1A9BB3 0%, #3D81F6 100%)",
              boxShadow: loading
                ? "none"
                : "0 4px 16px rgba(26,155,179,0.35)",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "opacity 0.3s",
            }}
          >
            {loading ? (
              <>
                <span
                  style={{
                    width: "15px",
                    height: "15px",
                    border: "2.5px solid rgba(255,255,255,0.35)",
                    borderTopColor: "#fff",
                    borderRadius: "50%",
                    display: "inline-block",
                    animation: "ua-spin 0.75s linear infinite",
                    marginRight: "8px",
                  }}
                />
                Signing in…
              </>
            ) : (
              <>
                Sign In
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: "8px" }}>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </>
            )}
          </button>
        </form>
      </div>

      <style>{`
        @keyframes ua-spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
