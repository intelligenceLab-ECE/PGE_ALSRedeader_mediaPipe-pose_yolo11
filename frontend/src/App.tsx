import { Navigate, Route, Routes } from "react-router-dom";

import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import AslPage from "./pages/AslPage";
import HomePage from "./pages/HomePage";
import SegmentationPage from "./pages/SegmentationPage";

export default function App() {
  return (
    <div className="page-shell">
      <Routes>
        <Route path="/" element={<><Header /><HomePage /><Footer /></>} />
        <Route path="/asl" element={<AslPage />} />
        <Route path="/segmentation" element={<SegmentationPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
