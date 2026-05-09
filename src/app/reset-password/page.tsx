"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

export default function ResetPasswordPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [token, setToken] = useState("");
  const router = useRouter();

  useEffect(() => {
    if (typeof window === "undefined") return;
    setToken(new URLSearchParams(window.location.search).get("token") ?? "");
  }, []);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setSuccess(false);

    const formData = new FormData(e.currentTarget);
    const password = String(formData.get("password") ?? "");
    const confirm = String(formData.get("confirm") ?? "");

    if (password !== confirm) {
      setMessage("A nova senha e a confirmação precisam ser iguais.");
      setLoading(false);
      return;
    }

    const res = await fetch("/api/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password })
    });
    const data = (await res.json()) as { message?: string; error?: string };
    setMessage(data.message ?? data.error ?? "Falha ao redefinir senha.");

    if (res.ok) {
      setSuccess(true);
      setTimeout(() => router.push("/login"), 2000);
    }
    setLoading(false);
  }

  return (
    <main className="auth-shell">
      <form onSubmit={handleSubmit} className="card auth-card auth-form">
        <h1 className="auth-title">Redefinir senha</h1>
        <p className="auth-subtitle">Informe sua nova senha para continuar.</p>
        <input name="password" type="password" placeholder="Nova senha" className="auth-input" required minLength={6} />
        <input name="confirm" type="password" placeholder="Confirme a nova senha" className="auth-input" required minLength={6} />
        <button disabled={loading || !token} className="btn-primary" type="submit">
          {loading ? "Salvando..." : "Salvar nova senha"}
        </button>
        {!token && (
          <p style={{ color: "var(--rosa-forte)", margin: 0 }}>
            Token inválido. <Link href="/esqueci-senha" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>Pedir novo código</Link>
          </p>
        )}
        {message && (
          <p style={{ color: success ? "var(--verde-forte)" : "var(--rosa-forte)", margin: 0 }}>
            {message}
          </p>
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
