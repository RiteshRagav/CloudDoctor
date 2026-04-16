import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/App.css";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import LogAnalyzer from "@/pages/LogAnalyzer";
import AIDiagnosis from "@/pages/AIDiagnosis";
import Reports from "@/pages/Reports";
import { Toaster } from "@/components/ui/sonner";

function App() {
  // Remove any dynamically-injected third-party badges
  useEffect(() => {
    const remove = () => {
      const el = document.getElementById("emergent-badge");
      if (el) el.remove();
    };
    remove();
    const observer = new MutationObserver(remove);
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="dark">
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/logs" element={<LogAnalyzer />} />
            <Route path="/diagnosis" element={<AIDiagnosis />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      <Toaster position="bottom-right" theme="dark" richColors />
    </div>
  );
}

export default App;
