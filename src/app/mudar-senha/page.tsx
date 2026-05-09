"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function MudarSenhaPage() {
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
    const currentPassword = String(formData.get("currentPassword") ?? "");
    const newPassword = String(formData.get("newPassword") ?? "");
    const confirmPassword = String(formData.get("confirmPassword") ?? "");

    if (newPassword !== confirmPassword) {
      setMessage("A nova senha e a confirmação precisam ser iguais.");
      setLoading(false);
      return;
    }

    const res = await fetch("/api/auth/change-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentPassword, newPassword })
    });
    const data = (await res.json()) as { message?: string; error?: string };
    setMessage(data.message ?? data.error ?? "Não foi possível alterar a senha.");

    if (res.ok) {
      setSuccess(true);
      setTimeout(() => router.push("/meu-perfil"), 1800);
    }
    setLoading(false);
  }

  return (
    <main className="auth-shell">
      <form onSubmit={handleSubmit} className="card auth-card auth-form">
        <h1 className="auth-title">Mudar senha</h1>
        <p className="auth-subtitle">Altere sua senha com segurança.</p>
        <input name="currentPassword" type="password" placeholder="Senha atual" className="auth-input" required />
        <input name="newPassword" type="password" placeholder="Nova senha" className="auth-input" required minLength={6} />
        <input name="confirmPassword" type="password" placeholder="Confirme a nova senha" className="auth-input" required minLength={6} />
        <button disabled={loading} className="btn-primary" type="submit">
          {loading ? "Alterando..." : "Alterar senha"}
        </button>
        <Link href="/meu-perfil" className="btn-ghost" style={{ textAlign: "center" }}>
          Cancelar
        </Link>
        {message && (
          <p style={{ color: success ? "var(--verde-forte)" : "var(--rosa-forte)", margin: 0 }}>
            {message}
          </p>
        )}
      </form>
    </main>
  );
}
