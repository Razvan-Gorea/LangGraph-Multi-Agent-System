"use client";

import { Rubik } from "next/font/google";

import { useState } from "react";
import styles from "../../styles/Login.module.css";
import { useRouter } from "next/navigation";

const rubik = Rubik({
  subsets: ["latin"],
  weight: ["400"],
});

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSubmit = async(e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    if (!email.trim()) {
      setError("Email is missing");
      return;
    }

    if (!password) {
      setError("Password is missing");
      return;
    }

    const response = await fetch("http://127.0.0.1:8888/user/login",{
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: email,
            password: password,
        }),
    });

    if (response.ok){
        setSuccess(true);
        const resp = await response.json();
        router.push(`/chat_bot/${resp.id}`);
    }
  };

  return (
    <main className={rubik.className}>
      <div className={styles.container}>
        <div className={styles.loginForm}>
          <h2 className={styles.loginTitle}>Login</h2>
          <br />
          <form onSubmit={handleSubmit}>
            <div className={styles.formGroup}>
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                value={email}
                name="new-email"
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <br />
            <div className={styles.formGroup}>
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <p className={styles.error}>{error}</p>}
            {success && <p className={styles.success}>Login successful!</p>}
            <br />
            <button type="submit" className={styles.submitBtn}>
              Login
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
