import React, { useEffect, useState } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, IconButton, Box, Typography } from "@mui/material";
import { Add, Edit, Delete } from "@mui/icons-material";

function Students({ user }) {
  const [students, setStudents] = useState([]);
  const [open, setOpen] = useState(false);
  const [editStudent, setEditStudent] = useState(null);
  const [form, setForm] = useState({ username: "", full_name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const token = user?.token;

  const fetchStudents = () => {
    fetch("http://localhost:8000/students", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setStudents);
  };

  useEffect(() => {
    if (user?.role === "admin") fetchStudents();
  }, [user]);

  const handleOpen = (student = null) => {
    setEditStudent(student);
    setForm(student ? { ...student, password: "" } : { username: "", full_name: "", email: "", password: "" });
    setOpen(true);
    setError("");
  };
  const handleClose = () => setOpen(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSave = () => {
    if (!form.username || !form.full_name || !form.email || (!editStudent && !form.password)) {
      setError("Tüm alanlar (şifre hariç) zorunlu. Yeni öğrenci için şifre gerekli.");
      return;
    }
    const method = editStudent ? "PUT" : "POST";
    const url = editStudent ? `http://localhost:8000/students/${form.username}` : "http://localhost:8000/students";
    fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(form),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => Promise.reject(d.detail || "Hata"));
        return res.json();
      })
      .then(() => {
        fetchStudents();
        handleClose();
      })
      .catch(setError);
  };

  const handleDelete = (username) => {
    if (!window.confirm("Öğrenci silinsin mi?")) return;
    fetch(`http://localhost:8000/students/${username}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => Promise.reject(d.detail || "Hata"));
        fetchStudents();
      })
      .catch(setError);
  };

  const studentPhoto = "https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=600&q=80";

  if (user?.role !== "admin") return <div>Erişim yok</div>;

  return (
    <Box sx={{ maxWidth: 900, margin: '40px auto', p: 2, background: 'linear-gradient(135deg, #f0fdfa 0%, #e0e7ff 100%)', borderRadius: 6, boxShadow: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <img src={studentPhoto} alt="Öğrenciler" style={{ width: 220, maxWidth: '100%', borderRadius: 16, objectFit: 'cover', marginBottom: 8 }} />
        <Typography variant="h4" gutterBottom fontWeight={700} color="primary">Öğrenciler</Typography>
      </Box>
      <Button
        variant="contained"
        color="success"
        startIcon={<Add />}
        onClick={() => handleOpen()}
        sx={{ mb: 2, borderRadius: 2, fontWeight: 600, fontSize: 16, px: 3, py: 1 }}
      >
        Yeni Öğrenci Ekle
      </Button>
      <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: 4 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ background: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Kullanıcı Adı</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Ad Soyad</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Email</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Durum</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {students.map((student) => (
              <TableRow key={student.username} hover sx={{ transition: '0.2s', ':hover': { background: '#e3f2fd' } }}>
                <TableCell>{student.username}</TableCell>
                <TableCell>{student.full_name}</TableCell>
                <TableCell>{student.email}</TableCell>
                <TableCell>{student.disabled ? "Pasif" : "Aktif"}</TableCell>
                <TableCell>
                  <IconButton color="primary" onClick={() => handleOpen(student)}><Edit /></IconButton>
                  <IconButton color="error" onClick={() => handleDelete(student.username)}><Delete /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} PaperProps={{ sx: { borderRadius: 3, p: 1 } }}>
        <DialogTitle sx={{ fontWeight: 700, fontSize: 22 }}>{editStudent ? "Öğrenciyi Düzenle" : "Yeni Öğrenci Ekle"}</DialogTitle>
        <DialogContent sx={{ minWidth: 350, py: 2 }}>
          <TextField label="Kullanıcı Adı" name="username" value={form.username} onChange={handleChange} fullWidth margin="dense" disabled={!!editStudent} sx={{ mb: 2 }} />
          <TextField label="Ad Soyad" name="full_name" value={form.full_name} onChange={handleChange} fullWidth margin="dense" sx={{ mb: 2 }} />
          <TextField label="Email" name="email" value={form.email} onChange={handleChange} fullWidth margin="dense" sx={{ mb: 2 }} />
          <TextField label="Şifre" name="password" value={form.password} onChange={handleChange} fullWidth margin="dense" type="password" placeholder={editStudent ? "(Değiştirmek için girin)" : ""} sx={{ mb: 2 }} />
          {error && <Typography color="error" sx={{ mt: 1 }}>{error}</Typography>}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleClose} color="inherit" sx={{ borderRadius: 2 }}>İptal</Button>
          <Button onClick={handleSave} variant="contained" color="success" sx={{ borderRadius: 2 }}>Kaydet</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Students;
 