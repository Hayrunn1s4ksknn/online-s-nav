import React, { useEffect, useState, useRef } from "react";
import { Box, Typography, Card, CardContent, CardActions, Button, TextField, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Snackbar, Alert, Dialog, DialogTitle, DialogContent, DialogActions, RadioGroup, FormControlLabel, Radio, IconButton, LinearProgress } from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import { Add, Edit, Delete } from "@mui/icons-material";

const EXAMPLE_QUESTIONS = {
  Matematik: [
    { text: "2+2 kaçtır?", options: ["3", "4", "5", "6"], answer: 1 },
    { text: "5*3 kaçtır?", options: ["8", "15", "10", "20"], answer: 1 },
  ],
  Fizik: [
    { text: "Yerçekimi ivmesi kaçtır?", options: ["9.8", "10", "8.9", "7.5"], answer: 0 },
  ],
  Kimya: [
    { text: "Su'nun kimyasal formülü nedir?", options: ["H2O", "CO2", "O2", "NaCl"], answer: 0 },
  ],
};

const EXAMPLE_TITLES = {
  Matematik: "Matematik 101 Test",
  Fizik: "Fizik 101 Test",
  Kimya: "Kimya 101 Test",
};

const EXAMPLE_DESCS = {
  Matematik: "Matematik dersi için otomatik test.",
  Fizik: "Fizik dersi için otomatik test.",
  Kimya: "Kimya dersi için otomatik test.",
};

const EXAM_DURATION = 10 * 60; // 10 dakika (saniye)

const examIllustration = "https://undraw.co/api/illustrations/online_test.svg";
const examPhoto = "https://images.unsplash.com/photo-1510936111840-6cef99faf2a9?auto=format&fit=crop&w=600&q=80";

const gradeOptions = [9, 10, 11, 12];

function Exams({ user }) {
  const token = user?.token;
  const [exams, setExams] = useState([]);
  const [results, setResults] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [newExam, setNewExam] = useState({ title: "", description: "", course_id: "", grade: "", questions: [] });
  const [open, setOpen] = useState(false);
  const [examDialog, setExamDialog] = useState({ open: false, exam: null });
  const [answers, setAnswers] = useState([]);
  const [examResult, setExamResult] = useState(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [timeLeft, setTimeLeft] = useState(EXAM_DURATION);
  const timerRef = useRef();
  const [selectedCourse, setSelectedCourse] = useState("");
  const [selectedGrade, setSelectedGrade] = useState("");

  const fetchData = async () => {
    setLoading(true);
    const examsRes = await fetch("http://localhost:8000/exams");
    const examsData = await examsRes.json();
    setExams(examsData);
    const resultsRes = await fetch("http://localhost:8000/results", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const resultsData = await resultsRes.json();
    setResults(resultsData);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line
  }, []);

  // Kursları çek
  useEffect(() => {
    fetch("http://localhost:8000/courses", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setCourses);
  }, [token]);

  // Kurs seçilince örnek soruları getir
  const handleCourseChange = (e) => {
    const course_id = e.target.value;
    const course = courses.find(c => c.id === Number(course_id));
    setNewExam({
      ...newExam,
      course_id,
      title: course ? course.name + " Test" : "",
      description: course ? course.name + " dersi için test." : "",
      questions: EXAMPLE_QUESTIONS[course?.name] ? EXAMPLE_QUESTIONS[course.name].map(q => ({ ...q })) : [],
    });
  };

  // Soru ve şık düzenleme
  const handleQuestionChange = (qIdx, field, value) => {
    const updated = [...newExam.questions];
    updated[qIdx][field] = value;
    setNewExam({ ...newExam, questions: updated });
  };
  const handleOptionChange = (qIdx, oIdx, value) => {
    const updated = [...newExam.questions];
    updated[qIdx].options[oIdx] = value;
    setNewExam({ ...newExam, questions: updated });
  };
  const handleAddQuestion = () => {
    setNewExam({
      ...newExam,
      questions: [...newExam.questions, { text: "", options: ["", "", "", ""], answer: 0 }],
    });
  };

  const handleExamAdd = async () => {
    if (!newExam.title || !newExam.description || !newExam.course_id || !newExam.grade || newExam.questions.length === 0) return;
    await fetch("http://localhost:8000/exams", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ ...newExam, id: exams.length + 1, course_id: Number(newExam.course_id), grade: Number(newExam.grade) }),
    });
    setMessage("Sınav eklendi!");
    setOpen(true);
    setNewExam({ title: "", description: "", course_id: "", grade: "", questions: [] });
    fetchData();
  };

  // Sınav çözme modalı açılırken sayaç başlat
  const handleOpenExam = (exam) => {
    setExamDialog({ open: true, exam });
    setAnswers(Array(exam.questions.length).fill(-1));
    setExamResult(null);
    setCurrentQ(0);
    setTimeLeft(EXAM_DURATION);
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timerRef.current);
          handleSubmitExam(true);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
  };

  // Sınav çözme modalı kapatılırken sayaç durdur
  const handleCloseExam = () => {
    setExamDialog({ open: false, exam: null });
    setAnswers([]);
    setExamResult(null);
    setCurrentQ(0);
    setTimeLeft(EXAM_DURATION);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  // Sınavı gönder
  const handleSubmitExam = async (auto = false) => {
    if (timerRef.current) clearInterval(timerRef.current);
    const res = await fetch("http://localhost:8000/take_exam", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ exam_id: examDialog.exam.id, answers }),
    });
    const data = await res.json();
    setExamResult({ ...data, timeUsed: EXAM_DURATION - timeLeft, auto });
    setMessage("Sınav tamamlandı! Puanınız: " + data.score);
    setOpen(true);
    fetchData();
  };

  // Soruya şık seç
  const handleSelect = (idx, val) => {
    const newAns = [...answers];
    newAns[idx] = val;
    setAnswers(newAns);
  };

  // Süreyi dakika:saniye formatında göster
  const formatTime = (s) => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;

  // Sınavları filtrele (hem kurs hem sınıf)
  const filteredExams = exams.filter((exam) => {
    let courseMatch = selectedCourse ? String(exam.course_id) === String(selectedCourse) : true;
    let gradeMatch = true;
    if (user?.role === "student") {
      gradeMatch = String(exam.grade) === String(user.grade);
    } else if (selectedGrade) {
      gradeMatch = String(exam.grade) === String(selectedGrade);
    }
    return courseMatch && gradeMatch;
  });

  return (
    <Box sx={{ maxWidth: 900, margin: '40px auto', p: 2, background: 'linear-gradient(135deg, #e0e7ff 0%, #f0fdfa 100%)', borderRadius: 6, boxShadow: 6 }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <img src={examPhoto} alt="Sınavlar" style={{ width: 220, maxWidth: '100%', borderRadius: 16, objectFit: 'cover', marginBottom: 8 }} />
        <Typography variant="h4" gutterBottom fontWeight={700} color="primary">Sınavlar</Typography>
      </Box>
      {/* Kurs ve sınıf filtresi */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField select label="Kurs Filtrele" value={selectedCourse} onChange={e => setSelectedCourse(e.target.value)} SelectProps={{ native: true }} size="small">
          <option value="">Tüm Kurslar</option>
          {courses.map((course) => (
            <option key={course.id} value={course.id}>{course.name}</option>
          ))}
        </TextField>
        {user?.role === "admin" && (
          <TextField select label="Sınıf Filtrele" value={selectedGrade} onChange={e => setSelectedGrade(e.target.value)} SelectProps={{ native: true }} size="small">
            <option value="">Tüm Sınıflar</option>
            {gradeOptions.map(g => <option key={g} value={g}>{g}. Sınıf</option>)}
          </TextField>
        )}
      </Box>
      {user?.role === "admin" && (
        <Card sx={{ mb: 3, borderRadius: 3, boxShadow: 4 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={700} color="primary">Yeni Sınav Ekle</Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <TextField select label="Kurs" fullWidth value={newExam.course_id} onChange={handleCourseChange} SelectProps={{ native: true }}>
                  <option value="">Kurs Seç</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>{course.name}</option>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={3}>
                <TextField select label="Sınıf" fullWidth value={newExam.grade} onChange={e => setNewExam({ ...newExam, grade: e.target.value })} SelectProps={{ native: true }}>
                  <option value="">Sınıf Seç</option>
                  {gradeOptions.map(g => <option key={g} value={g}>{g}. Sınıf</option>)}
                </TextField>
              </Grid>
              <Grid item xs={3}>
                <TextField label="Başlık" fullWidth value={newExam.title} onChange={e => setNewExam({ ...newExam, title: e.target.value })} />
              </Grid>
              <Grid item xs={3}>
                <TextField label="Açıklama" fullWidth value={newExam.description} onChange={e => setNewExam({ ...newExam, description: e.target.value })} />
              </Grid>
            </Grid>
            <Box sx={{ mt: 2 }}>
              {newExam.questions.length > 0 && (
                <Alert severity="info">Bu derse ait {newExam.questions.length} adet hazır soru eklenecek.</Alert>
              )}
            </Box>
            <Grid item xs={12}>
              {newExam.questions.map((q, qIdx) => (
                <Box key={qIdx} sx={{ mb: 2, p: 2, border: '1px solid #eee', borderRadius: 2 }}>
                  <TextField label="Soru" fullWidth sx={{ mb: 1 }} value={q.text} onChange={e => handleQuestionChange(qIdx, 'text', e.target.value)} />
                  <Grid container spacing={1}>
                    {q.options.map((opt, oIdx) => (
                      <Grid item xs={6} key={oIdx}>
                        <TextField label={`Şık ${String.fromCharCode(65 + oIdx)}`} fullWidth value={opt} onChange={e => handleOptionChange(qIdx, oIdx, e.target.value)} />
                      </Grid>
                    ))}
                  </Grid>
                  <TextField label="Doğru Şık (0-3)" type="number" sx={{ mt: 1 }} value={q.answer} onChange={e => handleQuestionChange(qIdx, 'answer', parseInt(e.target.value))} />
                </Box>
              ))}
              <Button startIcon={<AddCircleOutlineIcon />} onClick={handleAddQuestion}>Soru Ekle</Button>
            </Grid>
          </CardContent>
          <CardActions sx={{ px: 3, pb: 2 }}>
            <Button variant="contained" color="success" startIcon={<Add />} onClick={handleExamAdd} sx={{ borderRadius: 2, fontWeight: 600 }}>Sınav Ekle</Button>
          </CardActions>
        </Card>
      )}
      <TableContainer component={Paper} sx={{ mt: 3, borderRadius: 3, boxShadow: 4 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ background: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>ID</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Kurs</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Sınıf</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Başlık</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Açıklama</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>Soru Sayısı</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 16 }}>İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredExams.map((exam) => {
              const course = courses.find(c => c.id === exam.course_id);
              return (
                <TableRow key={exam.id} hover sx={{ transition: '0.2s', ':hover': { background: '#e3f2fd' } }}>
                  <TableCell>{exam.id}</TableCell>
                  <TableCell>{course ? course.name : exam.course_id}</TableCell>
                  <TableCell>{exam.grade}</TableCell>
                  <TableCell>{exam.title}</TableCell>
                  <TableCell>{exam.description}</TableCell>
                  <TableCell>{exam.questions.length}</TableCell>
                  <TableCell>
                    {user?.role === "student" && (
                      <Button sx={{ mt: 2, borderRadius: 2, fontWeight: 600 }} variant="outlined" color="primary" onClick={() => handleOpenExam(exam)}>Sınava Gir</Button>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      <Box sx={{ mt: 5 }}>
        <Typography variant="h5" gutterBottom>Sonuçlar</Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Ders</TableCell>
                <TableCell>Sınav</TableCell>
                <TableCell>Kullanıcı</TableCell>
                <TableCell>Puan</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((result, idx) => {
                const exam = exams.find(e => e.id === result.exam_id);
                return (
                  <TableRow key={idx}>
                    <TableCell>{exam?.course}</TableCell>
                    <TableCell>{exam?.title}</TableCell>
                    <TableCell>{result.username}</TableCell>
                    <TableCell>{result.score}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
      <Snackbar open={open} autoHideDuration={2000} onClose={() => setOpen(false)}>
        <Alert onClose={() => setOpen(false)} severity="success" sx={{ width: '100%' }}>
          {message}
        </Alert>
      </Snackbar>
      {/* Sınav çözme modalı */}
      <Dialog open={examDialog.open} onClose={handleCloseExam} maxWidth="sm" fullWidth>
        <DialogTitle>{examDialog.exam?.title} - Sınavı Çöz</DialogTitle>
        <DialogContent>
          {examDialog.exam && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress variant="determinate" value={100 * timeLeft / EXAM_DURATION} sx={{ mb: 1 }} />
              <Typography color={timeLeft < 60 ? 'error' : 'text.secondary'}>Kalan Süre: {formatTime(timeLeft)}</Typography>
            </Box>
          )}
          {examDialog.exam?.questions && (
            <Box>
              <Typography sx={{ mb: 1 }}>{currentQ + 1}. {examDialog.exam.questions[currentQ].text}</Typography>
              <RadioGroup
                value={answers[currentQ]}
                onChange={e => handleSelect(currentQ, parseInt(e.target.value))}
              >
                {examDialog.exam.questions[currentQ].options.map((opt, oidx) => (
                  <FormControlLabel key={oidx} value={oidx} control={<Radio />} label={opt} />
                ))}
              </RadioGroup>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Button disabled={currentQ === 0} onClick={() => setCurrentQ(currentQ - 1)}>Geri</Button>
                {currentQ < examDialog.exam.questions.length - 1 ? (
                  <Button variant="contained" onClick={() => setCurrentQ(currentQ + 1)} disabled={answers[currentQ] === -1}>Sonraki</Button>
                ) : (
                  <Button variant="contained" color="success" onClick={() => handleSubmitExam(false)} disabled={answers[currentQ] === -1}>Sınavı Bitir</Button>
                )}
              </Box>
            </Box>
          )}
          {examResult && (
            <Box sx={{ mt: 3 }}>
              <Alert severity="info">Sınavınız tamamlandı! Puanınız: {examResult.score} <br />Kullanılan süre: {formatTime(examResult.timeUsed)} {examResult.auto && '(Süre doldu)'}</Alert>
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6">Doğru/Yanlışlar</Typography>
                {examDialog.exam.questions.map((q, idx) => (
                  <Box key={idx} sx={{ mb: 1, p: 1, border: '1px solid #eee', borderRadius: 1, background: answers[idx] === q.answer ? '#e8f5e9' : '#ffebee' }}>
                    <Typography>{idx + 1}. {q.text}</Typography>
                    <Typography>Senin Cevabın: <b>{q.options[answers[idx]] ?? '-'}</b> {answers[idx] === q.answer ? '✅' : '❌'} (Doğru: {q.options[q.answer]})</Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseExam}>Kapat</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Exams; 