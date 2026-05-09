"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  IconCalendarHeart,
  IconBook,
  IconHeart,
  IconBell,
  IconSparkle,
  IconCheckCircle,
  IconShield,
  IconArrowRight,
  IconInfo
} from "@/components/Icons";

const STORAGE_KEY = "sophia.consent.v1";

type Consent = {
  version: 1;
  acceptedAt: string;
  finalidades: {
    lembretes: boolean;
    conteudosEducativos: boolean;
    rotinasPuerperio: boolean;
    alertasInformativos: boolean;
    infoMunicipios: boolean;
  };
  obrigatorias: {
    contaIdentificacao: boolean;
    seguranca: boolean;
    iaTransparencia: boolean;
  };
};

const defaultConsent: Consent = {
  version: 1,
  acceptedAt: "",
  finalidades: {
    lembretes: true,
    conteudosEducativos: true,
    rotinasPuerperio: true,
    alertasInformativos: true,
    infoMunicipios: true
  },
  obrigatorias: {
    contaIdentificacao: true,
    seguranca: true,
    iaTransparencia: true
  }
};

export function ConsentManager() {
  const [consent, setConsent] = useState<Consent>(defaultConsent);
  const [salvo, setSalvo] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Consent;
        if (parsed?.version === 1) setConsent(parsed);
      }
    } catch {
      // estado padrão
    }
  }, []);

  function toggleFinalidade(key: keyof Consent["finalidades"]) {
    setConsent((c) => ({
      ...c,
      finalidades: { ...c.finalidades, [key]: !c.finalidades[key] }
    }));
  }

  function salvar() {
    const final = { ...consent, acceptedAt: new Date().toISOString() };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(final));
    setConsent(final);
    setSalvo(new Date().toLocaleString("pt-BR"));
  }

  const finalidades: {
    key: keyof Consent["finalidades"];
    Icon: typeof IconCalendarHeart;
    title: string;
    desc: string;
    base: string;
  }[] = [
    {
      key: "lembretes",
      Icon: IconCalendarHeart,
      title: "Lembretes de consultas e exames",
      desc: "Data, hora, local, profissional. Servem só pra te avisar — não viram propaganda.",
      base: "Consentimento (LGPD art. 7º, I e art. 11, I — dado sensível de saúde)"
    },
    {
      key: "conteudosEducativos",
      Icon: IconBook,
      title: "Conteúdos educativos materno-infantis",
      desc: "Pra te sugerir leituras alinhadas ao seu momento (puerpério inicial, amamentação, sono...).",
      base: "Consentimento (LGPD art. 7º, I)"
    },
    {
      key: "rotinasPuerperio",
      Icon: IconHeart,
      title: "Organização e rotinas do puerpério",
      desc: "Marcos da sua jornada, anotações, sentimentos do dia. Servem pra dar continuidade ao acolhimento.",
      base: "Consentimento (LGPD art. 11, I — dado sensível de saúde)"
    },
    {
      key: "alertasInformativos",
      Icon: IconBell,
      title: "Alertas e orientações informativas",
      desc: "Avisos importantes (recall de produto, campanha de vacinação local). Sem promoção comercial.",
      base: "Consentimento (LGPD art. 7º, I)"
    },
    {
      key: "infoMunicipios",
      Icon: IconSparkle,
      title: "Informações gerais por município",
      desc: "UBS próxima, contatos públicos do SUS, campanhas locais. A gente usa só sua cidade — não te localizamos em tempo real.",
      base: "Consentimento (LGPD art. 7º, I)"
    }
  ];

  return (
    <>
      <section className="page-section">
        <h2 className="page-title">Aqui você decide</h2>
        <p className="page-subtitle">
          Cada item abaixo só é usado se você deixar marcado. As mudanças
          valem pra próxima vez que você abrir o app.
        </p>

        <div className="list-stack" style={{ marginTop: 16 }}>
          {finalidades.map((f) => (
            <article key={f.key} className="list-row">
              <div className="list-icon"><f.Icon /></div>
              <div className="list-text">
                <h4>{f.title}</h4>
                <p>{f.desc}</p>
                <p style={{ marginTop: 4, fontSize: 11.5, color: "var(--texto-mute)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                  Base legal: {f.base}
                </p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={consent.finalidades[f.key]}
                  onChange={() => toggleFinalidade(f.key)}
                />
                <span className="toggle-slider" />
              </label>
            </article>
          ))}
        </div>
      </section>

      <section className="page-section">
        <h2 className="page-title">Sempre ativos (necessários ao serviço)</h2>
        <p className="page-subtitle">
          Esses são essenciais pra a Sophia funcionar com segurança. Não dá
          pra desligar enquanto você tiver conta — mas você pode encerrar
          sua conta a qualquer momento em <Link href="/excluir-meus-dados" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>Excluir meus dados</Link>.
        </p>
        <div className="list-stack" style={{ marginTop: 16 }}>
          <article className="list-row green">
            <div className="list-icon"><IconShield /></div>
            <div className="list-text">
              <h4>Conta e identificação</h4>
              <p>Nome e e-mail pra criar e sustentar sua conta.</p>
              <p style={{ marginTop: 4, fontSize: 11.5, color: "var(--texto-mute)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                Base legal: Execução do contrato (LGPD art. 7º, V)
              </p>
            </div>
            <span style={{ fontSize: 11, color: "var(--verde-forte)", fontWeight: 700, letterSpacing: 0.8, textTransform: "uppercase" }}>Sempre</span>
          </article>
          <article className="list-row green">
            <div className="list-icon"><IconCheckCircle /></div>
            <div className="list-text">
              <h4>Segurança e registros de acesso</h4>
              <p>Manter sua conta protegida e cumprir o Marco Civil (6 meses).</p>
              <p style={{ marginTop: 4, fontSize: 11.5, color: "var(--texto-mute)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                Base legal: Cumprimento de obrigação legal (LGPD art. 7º, II)
              </p>
            </div>
            <span style={{ fontSize: 11, color: "var(--verde-forte)", fontWeight: 700, letterSpacing: 0.8, textTransform: "uppercase" }}>Sempre</span>
          </article>
          <article className="list-row green">
            <div className="list-icon"><IconInfo /></div>
            <div className="list-text">
              <h4>Transparência sobre IA</h4>
              <p>Identificar a Sophia como IA em conversa, conforme princípios de transparência.</p>
              <p style={{ marginTop: 4, fontSize: 11.5, color: "var(--texto-mute)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                Base legal: Boas práticas e PL 2.338/2023 (em tramitação)
              </p>
            </div>
            <span style={{ fontSize: 11, color: "var(--verde-forte)", fontWeight: 700, letterSpacing: 0.8, textTransform: "uppercase" }}>Sempre</span>
          </article>
        </div>
      </section>

      <div className="reminder-card">
        <div>
          <h4>{salvo ? "Consentimento atualizado" : "Pronto pra salvar?"}</h4>
          <p>
            {salvo
              ? `Salvo em ${salvo}. Você pode rever e mudar quando quiser.`
              : "Quando estiver tudo do seu jeito, é só clicar em Salvar."}
          </p>
        </div>
        <button onClick={salvar} type="button" className="btn-primary">
          Salvar preferências
          <IconArrowRight style={{ width: 16, height: 16 }} />
        </button>
      </div>
    </>
  );
}
