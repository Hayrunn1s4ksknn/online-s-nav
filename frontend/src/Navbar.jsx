import React from "react";
import { AppBar, Toolbar, Typography, Button, Box, IconButton } from "@mui/material";
import { useNavigate } from "react-router-dom";
import SchoolIcon from '@mui/icons-material/School';

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <IconButton edge="start" color="inherit" onClick={() => navigate("/")}> <SchoolIcon sx={{ mr: 1 }} /> </IconButton>
        <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => navigate("/")}>Testoria</Typography>
        <Button color="inherit" onClick={() => navigate("/about")}>Hakkımızda</Button>
        <Button color="inherit" onClick={() => navigate("/mission")}>Misyon</Button>
        <Button color="inherit" onClick={() => navigate("/vision")}>Vizyon</Button>
        {user && user.role === "admin" && (
          <>
            <Button color="inherit" onClick={() => navigate("/students")}>Öğrencileri Yönet</Button>
            <Button color="inherit" onClick={() => navigate("/exams")}>Sınavları Yönet</Button>
            <Button color="inherit" onClick={() => navigate("/courses")}>Kursları Yönet</Button>
          </>
        )}
        {user ? (
          <>
            <Button color="inherit" onClick={() => navigate("/dashboard")}>Panel</Button>
            <Button color="inherit" onClick={onLogout}>Çıkış</Button>
          </>
        ) : (
          <>
            <Button color="inherit" onClick={() => navigate("/login")}>Giriş Yap</Button>
            <Button color="inherit" onClick={() => navigate("/login?register=1")}>Kayıt Ol</Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
} 