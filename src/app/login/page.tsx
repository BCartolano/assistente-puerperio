"use client";

import Link from "next/link";
import Image from "next/image";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    const formData = new FormData(e.currentTarget);
    const body = {
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? "")
    };
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = (await res.json()) as { message?: string; error?: string };
    if (res.ok) {
      router.push("/inicio");
      router.refresh();
      return;
    }
    setMessage(data.error ?? "Falha ao entrar.");
    setLoading(false);
  }

  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="login-hero">
          <div className="login-hero-illustration-wrap">
            <Image
              src="/images/sophia-mae-bebe.png"
              alt="Mãe segurando ternamente seu bebê, cercada por flores e folhas"
              width={900}
              height={1100}
              priority
              className="login-hero-image"
            />
          </div>
          <p className="login-hero-caption">
            Aqui, cada conversa é um passo de acolhimento.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form-panel">
          <div className="login-floating-hearts" aria-hidden>
            <span className="heart heart-1">♥</span>
            <span className="heart heart-2">♥</span>
            <span className="heart heart-3">♥</span>
          </div>

          <h1 className="login-kicker">
            Olá, eu sou a <span>Sophia</span> <span className="login-emoji">💕</span>
          </h1>
          <p className="login-subtext">
            Sua assistente de informação e acolhimento no puerpério
          </p>

          <div className="login-field">
            <label className="login-label" htmlFor="email">
              E-mail
            </label>
            <div className="login-input-wrap">
              <IconMail className="login-input-icon" />
              <input
                id="email"
                name="email"
                type="email"
                placeholder="seu@email.com"
                className="login-input has-icon"
                autoComplete="email"
                required
              />
            </div>
          </div>

          <div className="login-field">
            <label className="login-label" htmlFor="password">
              Senha
            </label>
            <div className="login-input-wrap">
              <IconLock className="login-input-icon" />
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Digite sua senha"
                className="login-input has-icon has-trailing"
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="login-input-trailing"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
              >
                {showPassword ? <IconEyeOff /> : <IconEye />}
              </button>
            </div>
          </div>

          <button disabled={loading} className="login-submit" type="submit">
            <span>{loading ? "Entrando..." : "Entrar"}</span>
            {!loading && <IconHeart className="login-submit-icon" />}
          </button>

          {message && <p className="login-message">{message}</p>}

          <div className="login-divider">
            <span />
            <IconHeartSmall />
            <span />
          </div>

          <div className="login-actions">
            <Link className="login-action-link" href="/esqueci-senha">
              <IconKey /> Esqueceu a senha?
            </Link>
            <Link className="login-action-link" href="/cadastro">
              <IconUserPlus /> Criar conta
            </Link>
          </div>

          <p className="login-footer-note">
            Conteúdo educativo e de acolhimento. A Sophia <strong>não substitui</strong>{" "}
            consulta médica, psicológica ou de outros profissionais de saúde.
          </p>
        </form>
      </section>
    </main>
  );
}

function IconMail({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" width="18" height="18" className={className} aria-hidden>
      <rect x="3" y="5" width="18" height="14" rx="3" stroke="currentColor" strokeWidth="1.6" />
      <path d="M4 7l8 6 8-6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconLock({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" width="18" height="18" className={className} aria-hidden>
      <rect x="4.5" y="10" width="15" height="10" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 10V7a4 4 0 018 0v3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="12" cy="15" r="1.4" fill="currentColor" />
    </svg>
  );
}

function IconEye() {
  return (
    <svg viewBox="0 0 24 24" fill="none" width="18" height="18" aria-hidden>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" stroke="currentColor" strokeWidth="1.6" />
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

function IconEyeOff() {
  return (
    <svg viewBox="0 0 24 24" fill="none" width="18" height="18" aria-hidden>
      <path d="M3 3l18 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path
        d="M10.6 6.1A10.5 10.5 0 0112 6c6.5 0 10 7 10 7a17.4 17.4 0 01-3.1 4M6.6 6.6C3.7 8.5 2 12 2 12s3.5 7 10 7c1.7 0 3.2-.4 4.5-1"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconHeart({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16" className={className} aria-hidden>
      <path d="M12 21s-7-4.5-9.5-9C.8 8.4 2.6 4 6.6 4c2 0 3.5 1.1 4.4 2.4h1c.9-1.3 2.4-2.4 4.4-2.4 4 0 5.8 4.4 4.1 8-2.5 4.5-9.5 9-9.5 9z" />
    </svg>
  );
}

function IconHeartSmall() {
  return (
    <svg viewBox="0 0 24 24" fill="#e58faf" width="14" height="14" aria-hidden>
      <path d="M12 21s-7-4.5-9.5-9C.8 8.4 2.6 4 6.6 4c2 0 3.5 1.1 4.4 2.4h1c.9-1.3 2.4-2.4 4.4-2.4 4 0 5.8 4.4 4.1 8-2.5 4.5-9.5 9-9.5 9z" />
    </svg>
  );
}

function IconKey() {
  return (
    <svg viewBox="0 0 24 24" fill="none" width="14" height="14" aria-hidden>
      <circle cx="8" cy="15" r="4" stroke="currentColor" strokeWidth="1.6" />
      <path d="M11 13l9-9M17 7l3 3M14 10l3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconUserPlus() {
  return (
    <svg viewBox="0 0 24 24" fill="none" width="14" height="14" aria-hidden>
      <circle cx="10" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M3 20c0-3.5 3-6 7-6s7 2.5 7 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M19 8v6M16 11h6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
