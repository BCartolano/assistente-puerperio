"use client";

import Link from "next/link";
import { useState } from "react";
import {
  IconShield,
  IconHeart,
  IconTrash,
  IconCheckCircle,
  IconArrowRight,
  IconAlertCircle,
  IconHands
} from "@/components/Icons";
import { clearConsent } from "@/components/OnboardingConsent";

const STORAGE_KEYS_TO_CLEAR = ["sophia.consent.v1"];

type Step = "convite" | "confirmar" | "feito";

export function DeleteAccountFlow({ email, name }: { email: string; name: string }) {
  const [step, setStep] = useState<Step>("convite");
  const [confirmEmail, setConfirmEmail] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  function handleConfirmar() {
    if (confirmEmail.trim().toLowerCase() !== email.toLowerCase()) {
      setErro("O e-mail não confere com a sua conta. Confere com calma e tenta de novo.");
      return;
    }
    for (const key of STORAGE_KEYS_TO_CLEAR) {
      window.localStorage.removeItem(key);
    }
    clearConsent();
    setStep("feito");
    setErro(null);
  }

  if (step === "feito") {
    return (
      <section
        className="page-section"
        style={{
          textAlign: "center",
          background: "linear-gradient(180deg, #f1f6ee 0%, #e3ece0 100%)",
          border: "1px solid var(--verde)"
        }}
      >
        <div
          style={{
            width: 80,
            height: 80,
            borderRadius: "50%",
            background: "#fff",
            color: "var(--verde-forte)",
            display: "grid",
            placeItems: "center",
            margin: "0 auto 12px",
            border: "1px solid var(--verde)"
          }}
        >
          <IconCheckCircle style={{ width: 36, height: 36 }} />
        </div>
        <h2 className="page-title" style={{ color: "var(--verde-forte)" }}>
          Pedido recebido com cuidado, {name?.split(" ")[0] ?? "amiga"}
        </h2>
        <p style={{ marginTop: 8, fontSize: 15, lineHeight: 1.6, maxWidth: 540, margin: "8px auto 0" }}>
          Suas preferências locais foram apagadas agora. Em até 15 dias,
          tudo o que estiver associado a você nos nossos sistemas será
          apagado também — registros de acesso ficam apenas pelo prazo
          legal de 6 meses (Marco Civil), em sigilo.
        </p>
        <p style={{ marginTop: 14, fontSize: 13, color: "var(--texto-suave)" }}>
          Você vai receber um e-mail de confirmação em <strong>{email}</strong>.
        </p>
        <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 22, flexWrap: "wrap" }}>
          <Link href="/inicio" className="btn-ghost">
            Voltar pro Início
          </Link>
          <Link href="/login" className="btn-primary">
            Sair da conta
            <IconArrowRight style={{ width: 16, height: 16 }} />
          </Link>
        </div>
        <p style={{ marginTop: 18, fontSize: 13, color: "var(--texto-suave)" }}>
          Se mudar de ideia antes da finalização, escreva pra{" "}
          <strong>privacidade@sophia.app</strong> que a gente cancela com carinho.
        </p>
      </section>
    );
  }

  if (step === "confirmar") {
    return (
      <>
        <section
          className="page-section"
          style={{
            background: "linear-gradient(180deg, #fff5e6 0%, #fff0d8 100%)",
            border: "1px solid #f0d9b0",
            borderLeft: "4px solid #d4a574"
          }}
        >
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 14,
                background: "#fff",
                color: "#a06a32",
                display: "grid",
                placeItems: "center",
                flexShrink: 0,
                border: "1px solid #f0d9b0"
              }}
            >
              <IconAlertCircle />
            </div>
            <div>
              <h2 className="page-title" style={{ color: "#8a6a32", marginBottom: 6 }}>
                Confirma com a gente, com calma
              </h2>
              <p style={{ margin: 0, lineHeight: 1.6 }}>
                Vamos apagar a sua conta, suas anotações, suas preferências
                e os registros associados a você. Registros de acesso
                permanecerão por 6 meses, sob sigilo (Marco Civil).
              </p>
            </div>
          </div>
        </section>

        <section className="page-section">
          <h3 style={{ marginTop: 0, fontFamily: "var(--serif)", color: "var(--rosa-deep)" }}>
            Para confirmar, digita seu e-mail
          </h3>
          <p style={{ color: "var(--texto-suave)", marginTop: 4 }}>
            É só pra ter certeza que é você mesma.
          </p>
          <div style={{ marginTop: 14, display: "grid", gap: 10, maxWidth: 480 }}>
            <input
              type="email"
              className="auth-input"
              placeholder={email}
              value={confirmEmail}
              onChange={(e) => {
                setConfirmEmail(e.target.value);
                setErro(null);
              }}
              aria-label="Confirme seu e-mail"
            />
            {erro && (
              <p style={{ margin: 0, fontSize: 13, color: "var(--rosa-deep)" }}>{erro}</p>
            )}
            <div style={{ display: "flex", gap: 10, marginTop: 8, flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={() => setStep("convite")}
                className="btn-ghost"
              >
                Voltar
              </button>
              <button type="button" onClick={handleConfirmar} className="btn-primary">
                <IconTrash style={{ width: 16, height: 16 }} />
                Apagar tudo
              </button>
            </div>
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <section
        className="page-section"
        style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 22, alignItems: "center" }}
      >
        <div
          style={{
            width: 100,
            height: 100,
            borderRadius: "50%",
            background: "var(--rosa-creme)",
            color: "var(--rosa-forte)",
            display: "grid",
            placeItems: "center",
            border: "1px solid var(--borda)"
          }}
        >
          <IconHands style={{ width: 50, height: 50 }} />
        </div>
        <div>
          <h2 className="page-title">Sua decisão é respeitada</h2>
          <p style={{ marginTop: 8, lineHeight: 1.6 }}>
            Você não precisa explicar nada. Posso te contar antes o que vai
            acontecer? Assim você decide com clareza.
          </p>
        </div>
      </section>

      <section className="page-section">
        <h3 style={{ marginTop: 0, fontFamily: "var(--serif)", color: "var(--rosa-deep)" }}>
          O que vai ser apagado
        </h3>
        <div className="list-stack" style={{ marginTop: 14 }}>
          <article className="list-row">
            <div className="list-icon"><IconHeart /></div>
            <div className="list-text">
              <h4>Sua conta e identificação</h4>
              <p>Nome, e-mail, senha — tudo apagado.</p>
            </div>
          </article>
          <article className="list-row">
            <div className="list-icon"><IconShield /></div>
            <div className="list-text">
              <h4>Suas preferências e consentimentos</h4>
              <p>Toggles, lembretes, conteúdos favoritos.</p>
            </div>
          </article>
          <article className="list-row">
            <div className="list-icon"><IconCheckCircle /></div>
            <div className="list-text">
              <h4>Suas anotações e registros sensíveis</h4>
              <p>Diário, marcos da jornada, dados de saúde armazenados.</p>
            </div>
          </article>
        </div>

        <h3 style={{ marginTop: 24, fontFamily: "var(--serif)", color: "var(--rosa-deep)" }}>
          O que fica (por exigência legal, em sigilo)
        </h3>
        <article className="list-row green" style={{ marginTop: 12 }}>
          <div className="list-icon"><IconAlertCircle /></div>
          <div className="list-text">
            <h4>Registros de acesso por 6 meses</h4>
            <p>
              O Marco Civil (Lei 12.965/2014) exige que provedores guardem
              registros de acesso por 6 meses, em sigilo. Eles podem ser
              fornecidos apenas mediante ordem judicial.
            </p>
          </div>
        </article>
      </section>

      <div className="reminder-card">
        <div>
          <h4>Quer continuar?</h4>
          <p>
            Se mudou de ideia, é só voltar — eu fico aqui, sem rancor. Se
            quiser seguir, vamos com cuidado.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link href="/inicio" className="btn-ghost">
            Mudei de ideia
          </Link>
          <button type="button" onClick={() => setStep("confirmar")} className="btn-primary" style={{ background: "linear-gradient(135deg, #d4a574 0%, #b78650 100%)", boxShadow: "0 12px 24px -10px rgba(180, 130, 70, 0.45)" }}>
            <IconTrash style={{ width: 16, height: 16 }} />
            Quero apagar
          </button>
        </div>
      </div>
    </>
  );
}
