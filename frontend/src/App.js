import { BrowserRouter, Routes, Route } from "react-router-dom";
import "@/App.css";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import LogAnalyzer from "@/pages/LogAnalyzer";
import AIDiagnosis from "@/pages/AIDiagnosis";
import Reports from "@/pages/Reports";
import { Toaster } from "@/components/ui/sonner";

function App() {
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
