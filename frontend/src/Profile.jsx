import React from "react";

function Profile({ user }) {
  return (
    <div style={{ maxWidth: 400, margin: "100px auto", padding: 24, border: "1px solid #eee", borderRadius: 8 }}>
      <h2>Profilim</h2>
      <div><b>Kullanıcı adı:</b> {user?.username}</div>
      <div><b>Ad Soyad:</b> {user?.full_name}</div>
      <div><b>Email:</b> {user?.email}</div>
      <div><b>Rol:</b> {user?.role}</div>
    </div>
  );
}

export default Profile; 