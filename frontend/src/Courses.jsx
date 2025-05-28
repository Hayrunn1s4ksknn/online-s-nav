import React, { useEffect, useState } from "react";
import { TextField, Button, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Dialog, DialogTitle, DialogContent, DialogActions, Box, Typography } from "@mui/material";
import { Add, Edit, Delete } from "@mui/icons-material";

function Courses({ user }) {
  const [courses, setCourses] = useState([]);
  const [open, setOpen] = useState(false);
  const [editCourse, setEditCourse] = useState(null);
  const [form, setForm] = useState({ id: "", name: "", description: "" });
  const [error, setError] = useState("");

  const token = localStorage.getItem("token");

  const courseIllustration = "https://undraw.co/api/illustrations/teaching.svg";
  const coursePhoto = "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=600&q=80";

  useEffect(() => {
    fetch("http://localhost:8000/courses", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setCourses);
  }, [token]);

  const handleOpen = (course = null) => {
    setEditCourse(course);
    setForm(course ? { ...course } : { id: "", name: "", description: "" });
    setOpen(true);
    setError("");
  };
  const handleClose = () => setOpen(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSave = () => {
    if (!form.id || !form.name) {
      setError("ID ve isim zorunlu.");
      return;
    }
    const method = editCourse ? "PUT" : "POST";
    const url = editCourse ? `http://localhost:8000/courses/${form.id}` : "http://localhost:8000/courses";
    fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ ...form, id: Number(form.id) }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => Promise.reject(d.detail || "Hata"));
        return res.json();
      })
      .then((course) => {
        if (editCourse) {
          setCourses((prev) => prev.map((c) => (c.id === course.id ? course : c)));
        } else {
          setCourses((prev) => [...prev, course]);
        }
        handleClose();
      })
      .catch(setError);
  };

  const handleDelete = (id) => {
    if (!window.confirm("Kurs silinsin mi?")) return;
    fetch(`http://localhost:8000/courses/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => Promise.reject(d.detail || "Hata"));
        setCourses((prev) => prev.filter((c) => c.id !== id));
      })
      .catch(setError);
  };

  if (user?.role !== "admin") return <div>Erişim yok</div>;

  return (
    <Box sx={{ maxWidth: 900, margin: '40px auto', p: 2, background: 'linear-gradient(135deg, #f0fdfa 0%, #e0e7ff 100%)', borderRadius: 6, boxShadow: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <img src={coursePhoto} alt="Kurslar" style={{ width: 220, maxWidth: '100%', borderRadius: 16, objectFit: 'cover', marginBottom: 8 }} />
        <Typography variant="h4" gutterBottom fontWeight={700} color="primary">Kurslar</Typography>
      </Box>
      <Button
        variant="contained"
        color="success"
        startIcon={<Add />}
        onClick={() => handleOpen()}
        sx={{ mb: 2, borderRadius: 2, fontWeight: 600, fontSize: 16, px: 3, py: 1 }}
      >
        Yeni Kurs Ekle
      </Button>
      <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: 4 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ background: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>ID</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>İsim</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Açıklama</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {courses.map((course) => (
              <TableRow key={course.id} hover sx={{ transition: '0.2s', ':hover': { background: '#e3f2fd' } }}>
                <TableCell>{course.id}</TableCell>
                <TableCell>{course.name}</TableCell>
                <TableCell>{course.description}</TableCell>
                <TableCell>
                  <IconButton color="primary" onClick={() => handleOpen(course)}><Edit /></IconButton>
                  <IconButton color="error" onClick={() => handleDelete(course.id)}><Delete /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={open} onClose={handleClose} PaperProps={{ sx: { borderRadius: 3, p: 1 } }}>
        <DialogTitle sx={{ fontWeight: 700, fontSize: 22 }}>{editCourse ? "Kursu Düzenle" : "Yeni Kurs Ekle"}</DialogTitle>
        <DialogContent sx={{ minWidth: 350, py: 2 }}>
          <TextField label="ID" name="id" value={form.id} onChange={handleChange} fullWidth margin="dense" disabled={!!editCourse} sx={{ mb: 2 }} />
          <TextField label="İsim" name="name" value={form.name} onChange={handleChange} fullWidth margin="dense" sx={{ mb: 2 }} />
          <TextField label="Açıklama" name="description" value={form.description} onChange={handleChange} fullWidth margin="dense" sx={{ mb: 2 }} />
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

export default Courses; 