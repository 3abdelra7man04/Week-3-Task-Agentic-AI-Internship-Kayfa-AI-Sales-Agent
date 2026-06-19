// ── Knowledge Base — document upload, list, search, delete ───────────────
const KnowledgePage = ({ t, theme, language }) => {
  const { useState, useRef, useCallback, useEffect } = React;

  const [docs, setDocs] = useState([]);
  const [search, setSearch] = useState("");
  const [drag, setDrag] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [toast, setToast] = useState(null); // { type: 'success'|'error', message: string }
  const fileRef = useRef();

  // ── Toast helper ──────────────────────────────────────────────────────────
  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  };

  // ── Fetch file list from backend ──────────────────────────────────────────
  const fetchFiles = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:5000/api/v1/data/list/1");
      if (response.ok) {
        const data = await response.json();
        if (data.all_files) {
          const formattedDocs = data.all_files.map((file) => ({
            id: file._id || file.id || file.asset_id,
            name: file.asset_name || "Unknown Document",
            type: file.asset_type ? file.asset_type.toUpperCase() : "UNKNOWN",
            size: file.asset_size
              ? (file.asset_size / (1024 * 1024)).toFixed(2) + " MB"
              : "0 MB",
            status: file.asset_status
              ? file.asset_status.toLowerCase()
              : "processing",
            uploadedAt: file.asset_pushed_at
              ? new Date(file.asset_pushed_at).toLocaleString()
              : "Unknown",
            uploadedBy: file.asset_uploader_admin_name || "Unknown",
          }));
          setDocs(
            formattedDocs.sort(
              (a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt)
            )
          );
        }
      } else if (response.status === 400) {
        setDocs([]);
      } else {
        console.error("Failed to fetch files. HTTP status:", response.status);
      }
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
    const intervalId = setInterval(fetchFiles, 5000);
    return () => clearInterval(intervalId);
  }, [fetchFiles]);

  // ── Core upload function — sends files to /api/v1/data/upload/{project_id} ─
  const uploadFiles = useCallback(
    async (files) => {
      if (!files || files.length === 0) return;

      setUploading(true);
      const projectId = "1";
      let successCount = 0;
      let failCount = 0;

      for (const file of files) {
        // Validate file type client-side
        const ext = file.name.split(".").pop().toLowerCase();
        if (!["pdf", "txt"].includes(ext)) {
          showToast("error", `"${file.name}" is not supported. Use PDF or TXT.`);
          failCount++;
          continue;
        }

        const formData = new FormData();
        // The file field — matches UploadFile in FastAPI
        formData.append("file", file);
        // Pydantic model sent as a JSON string in a form field
        formData.append(
          "process_request",
          JSON.stringify({ chunk_size: 500, chunk_overlap: 50, do_reset: false })
        );
        // Uploader info — uses the default admin from the scheme defaults
        formData.append(
          "upload_request",
          JSON.stringify({
            uploader_admin_id: "123456789123456789aaaaaa",
            uploader_admin_name: "Admin",
          })
        );

        try {
          const response = await fetch(
            `http://localhost:5000/api/v1/data/upload/${projectId}`,
            { method: "POST", body: formData }
          );

          if (response.ok) {
            successCount++;
          } else {
            const errData = await response.json().catch(() => ({}));
            console.error("Upload failed:", errData);
            failCount++;
          }
        } catch (error) {
          console.error("Network error uploading file:", error);
          failCount++;
        }
      }

      // Reset file input
      if (fileRef.current) fileRef.current.value = "";
      setUploading(false);

      // Refresh list and show result toast
      await fetchFiles();

      if (successCount > 0 && failCount === 0) {
        showToast(
          "success",
          `${successCount} file${successCount > 1 ? "s" : ""} uploaded successfully! Processing in background…`
        );
      } else if (successCount > 0 && failCount > 0) {
        showToast(
          "error",
          `${successCount} uploaded, ${failCount} failed. Check console for details.`
        );
      } else {
        showToast("error", `Upload failed. Check that the backend is running.`);
      }
    },
    [fetchFiles]
  );

  // ── Button click → open file picker ──────────────────────────────────────
  const handleButtonClick = () => {
    if (fileRef.current) fileRef.current.click();
  };

  // ── Hidden input onChange ─────────────────────────────────────────────────
  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) uploadFiles(files);
  };

  // ── Drag-and-drop handlers ────────────────────────────────────────────────
  const handleDrop = (e) => {
    e.preventDefault();
    setDrag(false);
    const files = Array.from(e.dataTransfer.files || []);
    if (files.length > 0) uploadFiles(files);
  };

  const deleteDoc = async (id) => {
    try {
      const projectId = "1";
      const url = `http://localhost:5000/api/v1/data/delete/${projectId}/${id}`;
      console.log("Calling DELETE endpoint:", url);
      const response = await fetch(url, {
        method: "DELETE"
      });
      if (response.ok) {
        setDocs(docs.filter((d) => d.id !== id));
        showToast("success", "File deleted successfully");
      } else {
        const errData = await response.json().catch(() => ({}));
        showToast("error", "Failed to delete file");
        console.error("Delete failed:", errData);
      }
    } catch (error) {
      console.error("Network error deleting file:", error);
      showToast("error", "Network error while deleting file");
    }
  };

  const filtered = docs.filter((d) =>
    (d.name || "").toLowerCase().includes(search.toLowerCase())
  );

  const statusBadge = (s) => {
    let badgeStyle = {};
    if (s === "indexed" || s === "success") {
      badgeStyle = {
        backgroundColor:
          theme === "dark" ? "rgba(34, 197, 94, 0.1)" : "#f0fdf4",
        color: theme === "dark" ? "#4ade80" : "#166534",
      };
    } else if (s === "processing" || s === "indexing") {
      badgeStyle = {
        backgroundColor:
          theme === "dark"
            ? "rgba(26, 155, 179, 0.1)"
            : "rgba(26, 155, 179, 0.05)",
        color: "#1A9BB3",
      };
    } else {
      badgeStyle = {
        backgroundColor:
          theme === "dark" ? "rgba(239, 68, 68, 0.1)" : "#fef2f2",
        color: theme === "dark" ? "#f87171" : "#991b1b",
      };
    }
    return (
      <span
        style={{
          ...badgeStyle,
          padding: "4px 12px",
          borderRadius: "8px",
          fontSize: "11px",
          fontWeight: "bold",
        }}
      >
        {t(s) || s}
      </span>
    );
  };

  return (
    <div
      className="content"
      style={{
        padding: "24px",
        minHeight: "100vh",
        backgroundColor: theme === "dark" ? "#121212" : "#ffffff",
        color: theme === "dark" ? "#ffffff" : "#374151",
        transition: "all 0.4s ease-in-out",
        direction: language === "ar" ? "rtl" : "ltr",
        position: "relative",
      }}
    >
      {/* ── Toast Notification ─────────────────────────────────────────── */}
      {toast && (
        <div
          style={{
            position: "fixed",
            top: "24px",
            right: "24px",
            zIndex: 9999,
            padding: "14px 20px",
            borderRadius: "12px",
            fontWeight: "600",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
            animation: "slideIn 0.3s ease",
            backgroundColor:
              toast.type === "success"
                ? theme === "dark"
                  ? "#052e16"
                  : "#f0fdf4"
                : theme === "dark"
                  ? "#450a0a"
                  : "#fef2f2",
            color:
              toast.type === "success"
                ? theme === "dark"
                  ? "#4ade80"
                  : "#166534"
                : theme === "dark"
                  ? "#f87171"
                  : "#991b1b",
            border: `1px solid ${toast.type === "success"
              ? theme === "dark"
                ? "#166534"
                : "#bbf7d0"
              : theme === "dark"
                ? "#991b1b"
                : "#fecaca"
              }`,
          }}
        >
          <span style={{ fontSize: "18px" }}>
            {toast.type === "success" ? "✅" : "❌"}
          </span>
          {toast.message}
        </div>
      )}

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "30px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "24px", fontWeight: "900", margin: "0" }}>
            {language === "ar" ? "المكتبة" : "Knowledge Base"}
          </h2>
          <div
            style={{
              fontSize: "13px",
              color: theme === "dark" ? "#9ca3af" : "#6b7280",
              marginTop: "5px",
            }}
          >
            {docs.length} {t("documents")}
          </div>
        </div>
        <button
          id="upload-document-btn"
          onClick={handleButtonClick}
          disabled={uploading}
          style={{
            backgroundColor: uploading ? "#6b7280" : "#1A9BB3",
            color: "white",
            padding: "12px 24px",
            borderRadius: "12px",
            border: "none",
            fontWeight: "bold",
            cursor: uploading ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            boxShadow:
              theme === "dark"
                ? "none"
                : "0 4px 12px rgba(26, 155, 179, 0.2)",
            transition: "all 0.3s",
            opacity: uploading ? 0.7 : 1,
          }}
        >
          {uploading ? (
            <>
              <span
                style={{
                  width: "16px",
                  height: "16px",
                  border: "2px solid rgba(255,255,255,0.4)",
                  borderTopColor: "white",
                  borderRadius: "50%",
                  display: "inline-block",
                  animation: "spin 0.8s linear infinite",
                }}
              />
              {t("uploading") || "Uploading…"}
            </>
          ) : (
            <>
              <Icon.Upload size={18} />
              {t("uploadDocument") || "Upload Document"}
            </>
          )}
        </button>
      </div>

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileRef}
        style={{ display: "none" }}
        multiple
        accept=".pdf,.txt"
        onChange={handleFileInputChange}
      />

      {/* ── Drop Zone ───────────────────────────────────────────────────── */}
      <div
        style={{
          border: `2px dashed ${drag
            ? "#1A9BB3"
            : theme === "dark"
              ? "#374151"
              : "#e5e7eb"
            }`,
          backgroundColor: drag
            ? theme === "dark"
              ? "rgba(26, 155, 179, 0.1)"
              : "rgba(26, 155, 179, 0.05)"
            : theme === "dark"
              ? "#1e1e1e"
              : "#f9fafb",
          padding: "50px 20px",
          borderRadius: "20px",
          textAlign: "center",
          cursor: "pointer",
          marginBottom: "30px",
          transition: "all 0.3s ease",
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <div style={{ color: "#1A9BB3", marginBottom: "15px" }}>
          <Icon.Upload size={40} />
        </div>
        <div style={{ fontWeight: "900", fontSize: "18px" }}>
          {t("dropFilesHere") || "Drop files here"}
        </div>
        <div style={{ fontSize: "13px", color: "#9ca3af", marginTop: "8px" }}>
          {t("dropFilesHint") || "Supports PDF and TXT files"}
        </div>
      </div>

      {/* ── Search Bar ─────────────────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "14px 20px",
          backgroundColor: theme === "dark" ? "#1e1e1e" : "#f3f4f6",
          borderRadius: "15px",
          marginBottom: "30px",
          border: `1px solid ${theme === "dark" ? "#333" : "#e5e7eb"}`,
        }}
      >
        <Icon.Search size={20} style={{ opacity: 0.4 }} />
        <input
          placeholder={t("searchDocuments") || "Search documents…"}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            background: "none",
            border: "none",
            outline: "none",
            color: "inherit",
            width: "100%",
            fontWeight: "bold",
          }}
        />
      </div>

      {/* ── Documents Table ─────────────────────────────────────────────── */}
      <div
        className="card"
        style={{
          backgroundColor: theme === "dark" ? "#1e1e1e" : "#ffffff",
          borderRadius: "20px",
          overflow: "hidden",
          border: `1px solid ${theme === "dark" ? "#333" : "#f3f4f6"}`,
          boxShadow:
            theme === "dark" ? "none" : "0 10px 25px -5px rgba(0,0,0,0.05)",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            textAlign: language === "ar" ? "right" : "left",
          }}
        >
          <thead>
            <tr
              style={{
                backgroundColor:
                  theme === "dark" ? "rgba(255,255,255,0.03)" : "#f9fafb",
              }}
            >
              {[
                t("document") || "Document",
                t("size") || "Size",
                t("status") || "Status",
                t("uploadedBy") || "Uploaded By",
                t("date") || "Date",
                t("actions") || "Actions",
              ].map((h, i) => (
                <th
                  key={i}
                  style={{
                    padding: "20px",
                    fontSize: "11px",
                    textTransform: "uppercase",
                    color: "#9ca3af",
                    letterSpacing: "1px",
                    fontWeight: 600,
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td
                  colSpan="6"
                  style={{
                    textAlign: "center",
                    padding: "50px",
                    color: "#9ca3af",
                  }}
                >
                  <Icon.Database
                    size={48}
                    style={{ opacity: 0.5, marginBottom: "15px" }}
                  />
                  <div
                    style={{
                      fontSize: "16px",
                      fontWeight: "bold",
                      color: theme === "dark" ? "#fff" : "#333",
                    }}
                  >
                    No Documents Found
                  </div>
                  <div style={{ fontSize: "13px", marginTop: "5px" }}>
                    {search
                      ? "No documents match your search."
                      : "Upload your first document to see it listed here."}
                  </div>
                </td>
              </tr>
            ) : (
              filtered.map((doc) => (
                <tr
                  key={doc.id}
                  style={{
                    borderTop: `1px solid ${theme === "dark" ? "#333" : "#f3f4f6"
                      }`,
                    transition: "background 0.2s",
                  }}
                >
                  {/* Document name */}
                  <td style={{ padding: "20px" }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >
                      <div
                        style={{
                          padding: "5px 10px",
                          borderRadius: "8px",
                          background:
                            "linear-gradient(135deg, #1A9BB3 0%, #3D81F6 100%)",
                          color: "white",
                          fontSize: "10px",
                          fontWeight: "bold",
                        }}
                      >
                        {doc.type}
                      </div>
                      <span style={{ fontWeight: "bold", fontSize: "14px" }}>
                        {doc.name}
                      </span>
                    </div>
                  </td>

                  {/* Size */}
                  <td
                    style={{
                      padding: "20px",
                      fontSize: "13px",
                      color: "#9ca3af",
                    }}
                  >
                    {doc.size}
                  </td>

                  {/* Status */}
                  <td style={{ padding: "20px" }}>{statusBadge(doc.status)}</td>

                  {/* Uploaded By */}
                  <td
                    style={{
                      padding: "20px",
                      fontSize: "13px",
                      color: theme === "dark" ? "#aaa" : "#6b7280",
                    }}
                  >
                    {doc.uploadedBy}
                  </td>

                  {/* Date */}
                  <td
                    style={{
                      padding: "20px",
                      fontSize: "13px",
                      color: "#9ca3af",
                    }}
                  >
                    {doc.uploadedAt}
                  </td>

                  {/* Actions */}
                  <td style={{ padding: "20px" }}>
                    <div style={{ display: "flex", gap: "10px" }}>
                      <button
                        style={{
                          background: "none",
                          border: "none",
                          color: "#9ca3af",
                          cursor: "pointer",
                          padding: "5px",
                        }}
                      >
                        <Icon.Eye size={20} />
                      </button>
                      <button
                        onClick={() => deleteDoc(doc.id)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "#ef4444",
                          cursor: "pointer",
                          padding: "5px",
                        }}
                      >
                        <Icon.Trash size={20} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(-10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};