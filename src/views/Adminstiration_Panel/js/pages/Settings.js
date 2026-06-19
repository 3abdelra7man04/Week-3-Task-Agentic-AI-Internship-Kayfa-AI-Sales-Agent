// ── Settings — LLM config, chunking params, feature flags, vector store ───

const SettingsPage = ({ t, theme }) => {
  const { useState } = React;
  const isDark = theme === "dark";
  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";

  // BACKEND: GET /api/settings → load persisted config from DB on mount
  const [settings, setSettings] = useState({
    model: "claude-3-5-sonnet",
    topK: "5",
    chunkSize: "512",
    overlap: "64",
    threshold: "0.7",
    streaming: true,
    citations: true,
    fallback: true,
    logging: true,
  });

  const toggle = (k) => setSettings((s) => ({ ...s, [k]: !s[k] }));

  // مكون الـ Toggle المخصص بالألوان الجديدة
  const Toggle = ({ k }) => (
    <label
      className="toggle-wrap"
      style={{
        position: "relative",
        display: "inline-block",
        width: "40px",
        height: "22px",
        flexShrink: 0,
      }}
    >
      <input
        type="checkbox"
        style={{ opacity: 0, width: 0, height: 0 }}
        checked={settings[k]}
        onChange={() => toggle(k)}
      />
      <span
        style={{
          position: "absolute",
          cursor: "pointer",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: settings[k]
            ? primaryColor
            : isDark
              ? "#333"
              : "#ccc",
          transition: "0.4s",
          borderRadius: "34px",
        }}
      >
        <span
          style={{
            position: "absolute",
            height: "16px",
            width: "16px",
            left: settings[k] ? "20px" : "4px",
            bottom: "3px",
            backgroundColor: "white",
            transition: "0.4s",
            borderRadius: "50%",
          }}
        />
      </span>
    </label>
  );

  const cardStyle = {
    backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
    borderRadius: "20px",
    border: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
    padding: "20px",
    display: "flex",
    flexDirection: "column",
  };

  const inputStyle = {
    width: "100%",
    padding: "10px 14px",
    borderRadius: "10px",
    border: `1px solid ${isDark ? "#333" : "#e5e7eb"}`,
    backgroundColor: isDark ? "#121212" : "#ffffff",
    color: "inherit",
    outline: "none",
    fontSize: "14px",
    marginTop: "6px",
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
      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}
      >
        {/* ── LLM config ── */}
        <div className="card" style={cardStyle}>
          <div
            style={{
              fontWeight: "900",
              fontSize: "16px",
              marginBottom: "15px",
              color: isDark ? "#fff" : "#121212",
            }}
          >
            {t("llmConfiguration")}
          </div>
          <div className="card-body">
            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("model")}
              </label>
              <select
                style={inputStyle}
                value={settings.model}
                onChange={(e) =>
                  setSettings((s) => ({ ...s, model: e.target.value }))
                }
              >
                <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("topKChunks")}
              </label>
              <input
                style={inputStyle}
                type="number"
                min="1"
                max="20"
                value={settings.topK}
                onChange={(e) =>
                  setSettings((s) => ({ ...s, topK: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("confidenceThreshold")}
              </label>
              <input
                style={inputStyle}
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={settings.threshold}
                onChange={(e) =>
                  setSettings((s) => ({ ...s, threshold: e.target.value }))
                }
              />
            </div>
          </div>
        </div>

        {/* ── Chunking & indexing ── */}
        <div className="card" style={cardStyle}>
          <div
            style={{
              fontWeight: "900",
              fontSize: "16px",
              marginBottom: "15px",
              color: isDark ? "#fff" : "#121212",
            }}
          >
            {t("chunkingIndexing")}
          </div>
          <div className="card-body">
            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("chunkSize")}
              </label>
              <input
                style={inputStyle}
                type="number"
                value={settings.chunkSize}
                onChange={(e) =>
                  setSettings((s) => ({ ...s, chunkSize: e.target.value }))
                }
              />
            </div>
            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("chunkOverlap")}
              </label>
              <input
                style={inputStyle}
                type="number"
                value={settings.overlap}
                onChange={(e) =>
                  setSettings((s) => ({ ...s, overlap: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("embeddingModel")}
              </label>
              <select style={inputStyle}>
                <option>text-embedding-3-large</option>
                <option>text-embedding-3-small</option>
                <option>cohere-embed-v3</option>
              </select>
            </div>
          </div>
        </div>

        {/* ── Feature flags ── */}
        <div className="card" style={cardStyle}>
          <div
            style={{
              fontWeight: "900",
              fontSize: "16px",
              marginBottom: "15px",
              color: isDark ? "#fff" : "#121212",
            }}
          >
            {t("featuresTitle")}
          </div>
          <div className="card-body">
            {[
              {
                key: "streaming",
                labelKey: "streamResponses",
                descKey: "streamDesc",
              },
              {
                key: "citations",
                labelKey: "showCitations",
                descKey: "citationsDesc",
              },
              {
                key: "fallback",
                labelKey: "enableFallback",
                descKey: "fallbackDesc",
              },
              {
                key: "logging",
                labelKey: "queryLogging",
                descKey: "loggingDesc",
              },
            ].map((f, index) => (
              <div
                key={f.key}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "12px 0",
                  borderBottom:
                    index < 3
                      ? `1px solid ${isDark ? "#333" : "#f3f4f6"}`
                      : "none",
                }}
              >
                <div>
                  <div style={{ fontSize: "14px", fontWeight: "bold" }}>
                    {t(f.labelKey)}
                  </div>
                  <div style={{ fontSize: "11px", color: "#9ca3af" }}>
                    {t(f.descKey)}
                  </div>
                </div>
                <Toggle k={f.key} />
              </div>
            ))}
          </div>
        </div>

        {/* ── Vector store ── */}
        <div className="card" style={cardStyle}>
          <div
            style={{
              fontWeight: "900",
              fontSize: "16px",
              marginBottom: "15px",
              color: isDark ? "#fff" : "#121212",
            }}
          >
            {t("vectorStore")}
          </div>
          <div className="card-body">
            <div className="form-group">
              <label
                style={{
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                }}
              >
                {t("vectorDatabase")}
              </label>
              <select style={inputStyle}>
                <option>Pinecone</option>
                <option>Weaviate</option>
                <option>Qdrant</option>
                <option>pgvector (Postgres)</option>
                <option>Chroma (local)</option>
              </select>
            </div>
            <div
              style={{
                background: isDark
                  ? "rgba(26, 155, 179, 0.1)"
                  : "rgba(26, 155, 179, 0.05)",
                border: `1px solid ${primaryColor}44`,
                borderRadius: "12px",
                padding: "12px",
                marginTop: "15px",
              }}
            >
              <div
                style={{
                  fontSize: "12px",
                  fontWeight: "900",
                  color: primaryColor,
                  marginBottom: "4px",
                }}
              >
                {t("connectedHealthy")}
              </div>
              <div
                style={{ fontSize: "11px", color: isDark ? "#aaa" : "#6b7280" }}
              >
                {t("vectorStats")}
              </div>
            </div>
            <button
              style={{
                marginTop: "15px",
                width: "100%",
                backgroundColor: "transparent",
                border: `1px solid ${isDark ? "#444" : "#e5e7eb"}`,
                color: isDark ? "#ccc" : "#666",
                padding: "10px",
                borderRadius: "10px",
                fontWeight: "bold",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              <Icon.Refresh size={16} /> {t("reindexAll")}
            </button>
          </div>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginTop: "30px",
        }}
      >
        <button
          style={{
            backgroundColor: primaryColor,
            color: "white",
            border: "none",
            padding: "12px 30px",
            borderRadius: "14px",
            fontWeight: "900",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            boxShadow: "0 4px 14px rgba(26, 155, 179, 0.3)",
          }}
        >
          <Icon.Check size={18} /> {t("saveAllSettings")}
        </button>
      </div>
    </div>
  );
};
