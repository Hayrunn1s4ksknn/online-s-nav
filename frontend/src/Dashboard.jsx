import React from "react";
import { Box, Button, Typography, Grid, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";
import SchoolIcon from '@mui/icons-material/School';
import QuizIcon from '@mui/icons-material/Quiz';
import PeopleIcon from '@mui/icons-material/People';

const photos = {
  students: "https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=600&q=80", // gençler
  exams: "https://images.unsplash.com/photo-1510936111840-6cef99faf2a9?auto=format&fit=crop&w=600&q=80", // sınav/çalışan genç
  courses: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=600&q=80", // teknoloji
};

export default function Dashboard({ user }) {
  const navigate = useNavigate();
  if (!user) return null;
  if (user.role !== "admin") {
    return (
      <Box sx={{ mt: 8, textAlign: 'center' }}>
        <Typography variant="h4">Hoş geldin, {user.full_name || user.username}!</Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>Sistemdeki sınavlara katılmak için menüyü kullanabilirsin.</Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto', mt: 8, background: 'linear-gradient(135deg, #e0e7ff 0%, #f0fdfa 100%)', borderRadius: 6, p: 4, boxShadow: 6 }}>
      <Typography variant="h3" gutterBottom fontWeight={700} color="primary">Admin Paneli</Typography>
      <Typography variant="body1" sx={{ mb: 4, fontSize: 18 }}>Yönetmek istediğiniz bölümü seçin:</Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper elevation={8} sx={{ p: 3, textAlign: 'center', borderRadius: 4, transition: '0.3s', ':hover': { boxShadow: 12, transform: 'scale(1.03)' }, background: 'linear-gradient(120deg, #f0fdfa 60%, #e0e7ff 100%)' }}>
            <img src={photos.students} alt="Öğrenciler" style={{ width: '100%', maxHeight: 140, objectFit: 'cover', borderRadius: 12, marginBottom: 12 }} />
            <PeopleIcon color="primary" sx={{ fontSize: 50, mb: 1 }} />
            <Typography variant="h6" fontWeight={600}>Öğrencileri Yönet</Typography>
            <Button fullWidth variant="contained" sx={{ mt: 2, borderRadius: 2 }} onClick={() => navigate("/students")}>Git</Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={8} sx={{ p: 3, textAlign: 'center', borderRadius: 4, transition: '0.3s', ':hover': { boxShadow: 12, transform: 'scale(1.03)' }, background: 'linear-gradient(120deg, #e0e7ff 60%, #f0fdfa 100%)' }}>
            <img src={photos.exams} alt="Sınavlar" style={{ width: '100%', maxHeight: 140, objectFit: 'cover', borderRadius: 12, marginBottom: 12 }} />
            <QuizIcon color="primary" sx={{ fontSize: 50, mb: 1 }} />
            <Typography variant="h6" fontWeight={600}>Sınavları Yönet</Typography>
            <Button fullWidth variant="contained" sx={{ mt: 2, borderRadius: 2 }} onClick={() => navigate("/exams")}>Git</Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={8} sx={{ p: 3, textAlign: 'center', borderRadius: 4, transition: '0.3s', ':hover': { boxShadow: 12, transform: 'scale(1.03)' }, background: 'linear-gradient(120deg, #f0fdfa 60%, #e0e7ff 100%)' }}>
            <img src={photos.courses} alt="Kurslar" style={{ width: '100%', maxHeight: 140, objectFit: 'cover', borderRadius: 12, marginBottom: 12 }} />
            <SchoolIcon color="primary" sx={{ fontSize: 50, mb: 1 }} />
            <Typography variant="h6" fontWeight={600}>Kursları Yönet</Typography>
            <Button fullWidth variant="contained" sx={{ mt: 2, borderRadius: 2 }} onClick={() => navigate("/courses")}>Git</Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 