import React, { useState } from "react";
import { TextField, Button, Paper, Typography, Box, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";

const API_URL = "http://localhost:8000";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [registerOpen, setRegisterOpen] = useState(false);
  const gradeOptions = [9, 10, 11, 12];
  const [regForm, setRegForm] = useState({ username: "", full_name: "", email: "", password: "", grade: 9 });
  const [regError, setRegError] = useState("");
  const [regSuccess, setRegSuccess] = useState("");

  const handleLogin = async () => {
    setError("");
      const res = await fetch(`${API_URL}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
      });
    if (!res.ok) {
      setError("Kullanıcı adı veya şifre hatalı!");
      return;
    }
      const data = await res.json();
      onLogin(data.access_token);
  };

  const handleRegister = async () => {
    setRegError("");
    setRegSuccess("");
    if (!regForm.username || !regForm.full_name || !regForm.email || !regForm.password || !regForm.grade) {
      setRegError("Tüm alanlar zorunlu.");
      return;
    }
    const res = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(regForm),
    });
    if (!res.ok) {
      const d = await res.json();
      setRegError(d.detail || "Kayıt başarısız.");
      return;
    }
    setRegSuccess("Kayıt başarılı! Giriş yapabilirsiniz.");
    setTimeout(() => {
      setRegisterOpen(false);
      setRegForm({ username: "", full_name: "", email: "", password: "", grade: 9 });
      setRegSuccess("");
    }, 1500);
  };

  return (
    <Box sx={{ maxWidth: 400, margin: "80px auto" }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>Giriş Yap</Typography>
        <TextField label="Kullanıcı Adı" fullWidth margin="normal" value={username} onChange={e => setUsername(e.target.value)} />
        <TextField label="Şifre" type="password" fullWidth margin="normal" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <Typography color="error" sx={{ mt: 1 }}>{error}</Typography>}
        <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={handleLogin}>Giriş Yap</Button>
        <Button fullWidth sx={{ mt: 1 }} onClick={() => setRegisterOpen(true)}>Kayıt Ol</Button>
      </Paper>
      <Dialog open={registerOpen} onClose={() => setRegisterOpen(false)}>
        <DialogTitle>Kayıt Ol</DialogTitle>
        <DialogContent>
          <TextField label="Kullanıcı Adı" fullWidth margin="dense" value={regForm.username} onChange={e => setRegForm(f => ({ ...f, username: e.target.value }))} />
          <TextField label="Ad Soyad" fullWidth margin="dense" value={regForm.full_name} onChange={e => setRegForm(f => ({ ...f, full_name: e.target.value }))} />
          <TextField label="Email" fullWidth margin="dense" value={regForm.email} onChange={e => setRegForm(f => ({ ...f, email: e.target.value }))} />
          <TextField label="Şifre" type="password" fullWidth margin="dense" value={regForm.password} onChange={e => setRegForm(f => ({ ...f, password: e.target.value }))} />
          <TextField select label="Sınıf" fullWidth margin="dense" value={regForm.grade} onChange={e => setRegForm(f => ({ ...f, grade: Number(e.target.value) }))} SelectProps={{ native: true }}>
            {gradeOptions.map(g => <option key={g} value={g}>{g}. Sınıf</option>)}
          </TextField>
          {regError && <Typography color="error" sx={{ mt: 1 }}>{regError}</Typography>}
          {regSuccess && <Typography color="success.main" sx={{ mt: 1 }}>{regSuccess}</Typography>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRegisterOpen(false)}>İptal</Button>
          <Button variant="contained" onClick={handleRegister}>Kayıt Ol</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 