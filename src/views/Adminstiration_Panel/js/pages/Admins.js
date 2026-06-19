// ── Admins — manage admin users, roles, and invite new members ────────────

const AdminsPage = ({ t, theme }) => {
  const { useState } = React;
  const isDark = theme === "dark";

  const [admins, setAdmins] = useState(INIT_ADMINS);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", role: "Viewer" });

  const primaryColor = "#1A9BB3";
  const secondaryColor = "#3D81F6";

  const addAdmin = () => {
    if (!form.name || !form.email) return;
    // تم تعديل مصفوفة الألوان لتكون مشتقة من درجات الهوية (Tale & Blue)
    const colors = ["#1A9BB3", "#3D81F6", "#25A9C2", "#5294FF", "#158296"];
    setAdmins((prev) => [
      ...prev,
      {
        id: Date.now(),
        ...form,
        status: "pending",
        lastLogin: "Never",
        color: colors[prev.length % colors.length],
      },
    ]);
    setModal(false);
    setForm({ name: "", email: "", role: "Viewer" });
  };

  const removeAdmin = (id) => setAdmins(admins.filter((a) => a.id !== id));

  const initials = (name) =>
    name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2);

  const statusLabel = (s) => {
    if (s === "active") return t("active");
    if (s === "inactive") return t("inactive");
    return t("pending");
  };

  // الألوان للحالات مرتبطة بالهوية
  const statusColor = (s) =>
    s === "active"
      ? primaryColor
      : s === "pending"
        ? "#faad14"
        : isDark
          ? "#666"
          : "#9ca3af";
  const statusDot = (s) =>
    s === "active"
      ? primaryColor
      : s === "pending"
        ? "#faad14"
        : isDark
          ? "#444"
          : "#e5e7eb";

  const cardStyle = {
    backgroundColor: isDark ? "#1e1e1e" : "#ffffff",
    borderRadius: "20px",
    border: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
    overflow: "hidden",
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
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "25px",
        }}
      >
        <div
          style={{
            fontSize: "13px",
            fontWeight: "bold",
            color: isDark ? "#9ca3af" : "#6b7280",
          }}
        >
          {admins.length} {t("administrators")}
        </div>
        <button
          style={{
            backgroundColor: primaryColor,
            color: "white",
            border: "none",
            padding: "10px 20px",
            borderRadius: "12px",
            fontWeight: "bold",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
          onClick={() => setModal(true)}
        >
          <Icon.Plus size={16} /> {t("inviteAdmin")}
        </button>
      </div>

      {/* ── Admin table ── */}
      <div className="card" style={cardStyle}>
        <table
          className="admin-table"
          style={{ width: "100%", borderCollapse: "collapse" }}
        >
          <thead>
            <tr
              style={{
                backgroundColor: isDark ? "rgba(255,255,255,0.02)" : "#f9fafb",
                textAlign: "left",
              }}
            >
              <th
                style={{
                  padding: "16px",
                  fontSize: "11px",
                  textTransform: "uppercase",
                  color: "#9ca3af",
                  letterSpacing: "1px",
                }}
              >
                {t("administrator")}
              </th>
              <th
                style={{
                  padding: "16px",
                  fontSize: "11px",
                  textTransform: "uppercase",
                  color: "#9ca3af",
                  letterSpacing: "1px",
                }}
              >
                {t("role")}
              </th>
              <th
                style={{
                  padding: "16px",
                  fontSize: "11px",
                  textTransform: "uppercase",
                  color: "#9ca3af",
                  letterSpacing: "1px",
                }}
              >
                {t("status")}
              </th>
              <th
                style={{
                  padding: "16px",
                  fontSize: "11px",
                  textTransform: "uppercase",
                  color: "#9ca3af",
                  letterSpacing: "1px",
                }}
              >
                {t("lastLogin")}
              </th>
              <th
                style={{
                  padding: "16px",
                  fontSize: "11px",
                  textTransform: "uppercase",
                  color: "#9ca3af",
                  letterSpacing: "1px",
                }}
              >
                {t("actions")}
              </th>
            </tr>
          </thead>
          <tbody>
            {admins.map((a, i) => (
              <tr
                key={a.id}
                style={{
                  borderTop: `1px solid ${isDark ? "#333" : "#f3f4f6"}`,
                }}
              >
                <td style={{ padding: "16px" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "12px",
                    }}
                  >
                    <div
                      className="admin-avatar"
                      style={{
                        background: a.color,
                        width: "36px",
                        height: "36px",
                        borderRadius: "10px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontWeight: "bold",
                        fontSize: "13px",
                      }}
                    >
                      {initials(a.name)}
                    </div>
                    <div>
                      <div
                        style={{
                          fontWeight: "bold",
                          fontSize: "14px",
                          color: isDark ? "#eee" : "#374151",
                        }}
                      >
                        {a.name}
                      </div>
                      <div style={{ fontSize: "11px", color: "#9ca3af" }}>
                        {a.email}
                      </div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: "16px" }}>
                  <span
                    style={{
                      padding: "4px 10px",
                      borderRadius: "6px",
                      fontSize: "11px",
                      fontWeight: "bold",
                      background: a.color + "15",
                      color: a.color,
                    }}
                  >
                    {a.role}
                  </span>
                </td>
                <td style={{ padding: "16px" }}>
                  <span
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      fontSize: "12px",
                      color: statusColor(a.status),
                      fontWeight: "bold",
                    }}
                  >
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        background: statusDot(a.status),
                      }}
                    />
                    {statusLabel(a.status)}
                  </span>
                </td>
                <td
                  style={{
                    padding: "16px",
                    color: "#9ca3af",
                    fontSize: "13px",
                  }}
                >
                  {a.lastLogin}
                </td>
                <td style={{ padding: "16px" }}>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button
                      style={{
                        background: "none",
                        border: "none",
                        color: "#9ca3af",
                        cursor: "pointer",
                      }}
                    >
                      <Icon.Edit size={16} />
                    </button>
                    <button
                      style={{
                        background: "none",
                        border: "none",
                        color: "#ff4d4f",
                        cursor: "pointer",
                      }}
                      onClick={() => removeAdmin(a.id)}
                    >
                      <Icon.Trash size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Invite modal ── */}
      {modal && (
        <div
          className="modal-overlay"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={(e) => e.target === e.currentTarget && setModal(false)}
        >
          <div
            className="modal"
            style={{
              backgroundColor: isDark ? "#1e1e1e" : "white",
              padding: "30px",
              borderRadius: "20px",
              width: "400px",
              boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
            }}
          >
            <div
              style={{
                fontSize: "20px",
                fontWeight: "900",
                marginBottom: "20px",
              }}
            >
              {t("inviteAdministrator")}
            </div>

            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label
                style={{
                  display: "block",
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                  marginBottom: "6px",
                }}
              >
                {t("fullName")}
              </label>
              <input
                style={{
                  width: "100%",
                  padding: "12px",
                  borderRadius: "10px",
                  border: `1px solid ${isDark ? "#333" : "#e5e7eb"}`,
                  backgroundColor: isDark ? "#121212" : "white",
                  color: "inherit",
                  outline: "none",
                }}
                placeholder="Jane Smith"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>

            <div className="form-group" style={{ marginBottom: "15px" }}>
              <label
                style={{
                  display: "block",
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                  marginBottom: "6px",
                }}
              >
                {t("emailAddress")}
              </label>
              <input
                style={{
                  width: "100%",
                  padding: "12px",
                  borderRadius: "10px",
                  border: `1px solid ${isDark ? "#333" : "#e5e7eb"}`,
                  backgroundColor: isDark ? "#121212" : "white",
                  color: "inherit",
                  outline: "none",
                }}
                type="email"
                placeholder="jane@company.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>

            <div className="form-group" style={{ marginBottom: "25px" }}>
              <label
                style={{
                  display: "block",
                  fontSize: "12px",
                  fontWeight: "bold",
                  color: "#9ca3af",
                  marginBottom: "6px",
                }}
              >
                {t("role")}
              </label>
              <select
                style={{
                  width: "100%",
                  padding: "12px",
                  borderRadius: "10px",
                  border: `1px solid ${isDark ? "#333" : "#e5e7eb"}`,
                  backgroundColor: isDark ? "#121212" : "white",
                  color: "inherit",
                  outline: "none",
                }}
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                <option>Super Admin</option>
                <option>Admin</option>
                <option>Editor</option>
                <option>Viewer</option>
              </select>
            </div>

            <div
              style={{
                display: "flex",
                gap: "10px",
                justifyContent: "flex-end",
              }}
            >
              <button
                style={{
                  background: "none",
                  border: "none",
                  padding: "10px 20px",
                  cursor: "pointer",
                  color: "#9ca3af",
                  fontWeight: "bold",
                }}
                onClick={() => setModal(false)}
              >
                {t("cancel")}
              </button>
              <button
                style={{
                  backgroundColor: primaryColor,
                  color: "white",
                  border: "none",
                  padding: "10px 25px",
                  borderRadius: "12px",
                  fontWeight: "bold",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
                onClick={addAdmin}
              >
                <Icon.Check size={16} /> {t("sendInvite")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
