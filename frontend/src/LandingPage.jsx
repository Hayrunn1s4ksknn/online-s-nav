import React from "react";
import { Box, Typography, Button, Grid, Paper } from "@mui/material";

const heroPhoto = "https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=900&q=80";
const aboutPhoto = "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=900&q=80";
const missionPhoto = "https://images.unsplash.com/photo-1510936111840-6cef99faf2a9?auto=format&fit=crop&w=900&q=80";
const visionPhoto = "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=900&q=80";

export default function LandingPage({ section, user }) {
  let content;
  if (section === "about") {
    content = (
      <Grid container spacing={4} alignItems="center" justifyContent="center" sx={{ mt: 6 }}>
        <Grid item xs={12} md={6}><img src={aboutPhoto} alt="about" style={{ width: '100%', borderRadius: 16, boxShadow: 4 }} /></Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>Hakkımızda</Typography>
          <Typography variant="body1" sx={{ fontSize: 18 }}>
            Testoria, gençlerin ve öğrencilerin dijital ortamda sınavlara hazırlanmasını kolaylaştıran modern bir online sınav platformudur. Teknolojiyi ve eğitimi bir araya getiriyoruz.
          </Typography>
        </Grid>
      </Grid>
    );
  } else if (section === "mission") {
    content = (
      <Grid container spacing={4} alignItems="center" justifyContent="center" sx={{ mt: 6 }}>
        <Grid item xs={12} md={6}><img src={missionPhoto} alt="mission" style={{ width: '100%', borderRadius: 16, boxShadow: 4 }} /></Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>Misyonumuz</Typography>
          <Typography variant="body1" sx={{ fontSize: 18 }}>
            Her öğrencinin potansiyelini ortaya çıkarmak için yenilikçi, erişilebilir ve güvenilir sınav deneyimi sunmak.
          </Typography>
        </Grid>
      </Grid>
    );
  } else if (section === "vision") {
    content = (
      <Grid container spacing={4} alignItems="center" justifyContent="center" sx={{ mt: 6 }}>
        <Grid item xs={12} md={6}><img src={visionPhoto} alt="vision" style={{ width: '100%', borderRadius: 16, boxShadow: 4 }} /></Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h4" fontWeight={700} color="primary" gutterBottom>Vizyonumuz</Typography>
          <Typography variant="body1" sx={{ fontSize: 18 }}>
            Türkiye'nin ve dünyanın dört bir yanında gençlerin başarıya ulaşmasını sağlayan lider online sınav platformu olmak.
          </Typography>
        </Grid>
      </Grid>
    );
  } else {
    content = (
      <Box sx={{ textAlign: 'center', py: 8, background: 'linear-gradient(135deg, #e0e7ff 0%, #f0fdfa 100%)', borderRadius: 6, boxShadow: 6 }}>
        <img src={heroPhoto} alt="Testoria Hero" style={{ width: '100%', maxWidth: 600, borderRadius: 24, marginBottom: 32, boxShadow: 8 }} />
        <Typography variant="h2" fontWeight={800} color="primary" gutterBottom>Testoria</Typography>
        <Typography variant="h5" sx={{ mb: 4, color: '#374151' }}>
          Gençler için modern, güvenli ve eğlenceli online sınav platformu
        </Typography>
        <Button variant="contained" color="primary" size="large" href="/login" sx={{ fontWeight: 700, fontSize: 20, px: 5, py: 2, borderRadius: 3 }}>Hemen Başla</Button>
      </Box>
    );
  }
  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto', mt: 6, mb: 6 }}>
      {content}
    </Box>
  );
} 