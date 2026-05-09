"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

export default function EsqueciSenhaPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    const formData = new FormData(e.currentTarget);
    const body = { email: String(formData.get("email") ?? "") };
    const res = await fetch("/api/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = (await res.json()) as { message?: string; error?: string };
    setMessage(data.message ?? data.error ?? "Falha ao enviar e-mail.");
    if (res.ok) setSent(true);
    setLoading(false);
  }

  return (
    <main className="auth-shell">
      <form onSubmit={handleSubmit} className="card auth-card auth-form">
        <h1 className="auth-title">Esqueci minha senha</h1>
        <p className="auth-subtitle">Informe seu e-mail para receber o código.</p>
        <input name="email" type="email" placeholder="Seu e-mail" className="auth-input" required />
        <button disabled={loading} className="btn-primary" type="submit">
          {loading ? "Enviando..." : "Enviar código"}
        </button>
        {message && <p>{message}</p>}

        {sent && (
          <Link href="/verificar-codigo" className="btn-secondary">
            Já recebi o código →
          </Link>
        )}

        <p style={{ textAlign: "center", margin: "10px 0 0" }}>
          <Link className="auth-link" href="/login">
            ← Voltar para o login
          </Link>
        </p>
      </form>
    </main>
  );
}
