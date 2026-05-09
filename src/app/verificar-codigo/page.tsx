"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function VerificarCodigoPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    setSuccess(false);

    const formData = new FormData(e.currentTarget);
    const code = String(formData.get("code") ?? "");
    const mode = String(formData.get("mode") ?? "email");

    const res = await fetch("/api/auth/verify-code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: code, mode })
    });
    const data = (await res.json()) as { message?: string; error?: string };
    setMessage(data.message ?? data.error ?? "Não foi possível verificar.");

    if (res.ok) {
      setSuccess(true);
      if (mode === "reset") {
        setTimeout(() => router.push(`/reset-password?token=${encodeURIComponent(code)}`), 1500);
      } else {
        setTimeout(() => router.push("/login"), 1800);
      }
    }
    setLoading(false);
  }

  return (
    <main className="auth-shell">
      <form onSubmit={handleSubmit} className="card auth-card auth-form">
        <h1 className="auth-title">Verificar código</h1>
        <p className="auth-subtitle">Digite o código enviado por e-mail.</p>
        <select name="mode" className="auth-input" defaultValue="reset">
          <option value="reset">Redefinir minha senha</option>
          <option value="email">Verificar meu e-mail</option>
        </select>
        <input name="code" placeholder="Código de verificação" className="auth-input" required />
        <button disabled={loading} className="btn-secondary" type="submit">
          {loading ? "Verificando..." : "Confirmar"}
        </button>
        {message && (
          <p style={{ color: success ? "var(--verde-forte)" : "var(--rosa-forte)", margin: 0 }}>
            {message}
          </p>
        )}

        <p style={{ textAlign: "center", margin: "10px 0 0", fontSize: 13 }}>
          Não recebeu?{" "}
          <Link className="auth-link" href="/esqueci-senha" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
            Reenviar código
          </Link>
        </p>
        <p style={{ textAlign: "center", margin: 0 }}>
          <Link className="auth-link" href="/login">
            ← Voltar para o login
          </Link>
        </p>
      </form>
    </main>
  );
}
