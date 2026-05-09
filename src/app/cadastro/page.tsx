"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function CadastroPage() {
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setSuccess(false);

    const formData = new FormData(e.currentTarget);
    const body = {
      name: String(formData.get("name") ?? ""),
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? "")
    };

    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = (await res.json()) as { message?: string; error?: string };

    if (res.ok) {
      setSuccess(true);
      setMessage(data.message ?? "Conta criada! Redirecionando para o login...");
      setTimeout(() => router.push("/login"), 2200);
    } else {
      setMessage(data.error ?? "Não foi possível cadastrar.");
    }
    setLoading(false);
  }

  return (
    <main className="auth-shell">
      <form onSubmit={handleSubmit} className="card auth-card auth-form">
        <h1 className="auth-title">Criar conta</h1>
        <p className="auth-subtitle">Comece sua jornada com a Sophia.</p>
        <input name="name" placeholder="Seu nome" className="auth-input" required />
        <input name="email" type="email" placeholder="E-mail" className="auth-input" required />
        <input
          name="password"
          type="password"
          placeholder="Senha (mínimo 6 caracteres)"
          className="auth-input"
          required
          minLength={6}
        />
        <button disabled={loading} className="btn-primary" type="submit">
          {loading ? "Criando..." : "Criar conta"}
        </button>
        {message && (
          <p style={{ color: success ? "var(--verde-forte)" : "var(--rosa-forte)", margin: 0 }}>
            {message}
          </p>
        )}
        <p style={{ textAlign: "center", margin: "8px 0 0" }}>
          Já tem uma conta?{" "}
          <Link className="auth-link" href="/login" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
            Entrar
          </Link>
        </p>
      </form>
    </main>
  );
}
