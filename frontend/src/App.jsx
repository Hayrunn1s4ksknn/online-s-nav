import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import Profile from "./Profile";
import Exams from "./Exams";
import Students from "./Students";
import Courses from "./Courses";
import LandingPage from "./LandingPage";
import Navbar from "./Navbar";
import './App.css'

const API_URL = "http://localhost:8000";

function App() {
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) return;
      try {
      const userRes = await fetch(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${token}` },
      });
        if (!userRes.ok) throw new Error("Kullanıcı bilgisi alınamadı!");
      const userData = await userRes.json();
      setUser(userData);
    } catch (err) {
      setError(err.message);
    }
  };
    fetchUser();
  }, [token]);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
    } else {
      localStorage.removeItem("token");
    }
  }, [token]);

  const handleLogout = () => {
    setToken("");
    setUser(null);
    setError("");
  };

  if (token && !user) return <div>Yükleniyor...</div>;

  return (
    <>
      <Navbar user={user} onLogout={handleLogout} />
      <Routes>
        <Route path="/" element={
          user
            ? (user.role === "admin"
              ? <Navigate to="/dashboard" replace />
              : <Navigate to="/exams" replace />)
            : <LandingPage user={user} />
        } />
        <Route path="/dashboard" element={user ? <Dashboard user={user} /> : <Navigate to="/login" replace />} />
        <Route path="/login" element={!token ? <Login onLogin={setToken} /> : <Navigate to="/" replace />} />
        <Route path="/about" element={<LandingPage section="about" />} />
        <Route path="/mission" element={<LandingPage section="mission" />} />
        <Route path="/vision" element={<LandingPage section="vision" />} />
        <Route path="/profile" element={token ? <Profile user={user} /> : <Navigate to="/login" replace />} />
        <Route path="/exams" element={token ? <Exams user={{...user, token}} /> : <Navigate to="/login" replace />} />
        {user?.role === "admin" && (
          <Route path="/students" element={<Students user={{...user, token}} />} />
        )}
        <Route path="/courses" element={user ? <Courses user={{...user, token}} /> : <Navigate to="/login" replace />} />
      </Routes>
    </>
  );
}

export default App;
