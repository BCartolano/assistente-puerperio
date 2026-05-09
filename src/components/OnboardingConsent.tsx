"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import {
  IconShield,
  IconCalendarHeart,
  IconBook,
  IconHeart,
  IconBell,
  IconCheckCircle,
  IconArrowRight,
  IconSparkle
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

export function readConsent(): Consent | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Consent;
    return parsed?.version === 1 ? parsed : null;
  } catch {
    return null;
  }
}

export function clearConsent() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}

export function OnboardingConsent() {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const [consent, setConsent] = useState<Consent>(defaultConsent);

  useEffect(() => {
    const existing = readConsent();
    if (!existing) {
      setOpen(true);
    }
  }, []);

  if (!open) return null;

  function next() {
    setStep((s) => Math.min(s + 1, slides.length - 1));
  }

  function prev() {
    setStep((s) => Math.max(s - 1, 0));
  }

  function aceitar() {
    const final: Consent = {
      ...consent,
      acceptedAt: new Date().toISOString()
    };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(final));
    setOpen(false);
  }

  function toggleFinalidade(key: keyof Consent["finalidades"]) {
    setConsent((c) => ({
      ...c,
      finalidades: { ...c.finalidades, [key]: !c.finalidades[key] }
    }));
  }

  const slides: { illu: React.ReactNode; render: React.ReactNode }[] = [
    {
      illu: (
        <SophiaAvatar
          size="lg"
          alt="Sophia te dando boas-vindas"
        />
      ),
      render: (
        <>
          <h3>Antes da gente começar, posso te contar uma coisa importante?</h3>
          <p>
            Eu sou a <strong>Sophia</strong>, uma assistente virtual (uma IA)
            que existe pra te acolher e oferecer informação educativa sobre
            puerpério, gestação e cuidados com o bebê.
          </p>
          <p style={{ marginTop: 8 }}>
            Quero ser <strong>transparente</strong> com você sobre como cuido
            das suas informações. Vou te explicar em <strong>4 cards rápidos</strong> —
            depois é só decidir o que faz sentido pra você.
          </p>
        </>
      )
    },
    {
      illu: <IconShield style={{ width: 110, height: 110, color: "var(--rosa-forte)" }} />,
      render: (
        <>
          <h3>Eu sou uma IA, não uma profissional de saúde</h3>
          <p>
            Eu não dou diagnóstico, não receito remédio, nem substituo sua
            equipe de saúde. Eu acolho, escuto e ofereço conteúdo educativo
            baseado em fontes oficiais.
          </p>
          <div className="consent-list">
            <div className="consent-item">
              <div className="consent-item-icon"><IconCheckCircle /></div>
              <div>
                <h4>Educativo e acolhedor</h4>
                <p>Apoio emocional educativo e orientações gerais de bem-estar.</p>
              </div>
            </div>
            <div className="consent-item">
              <div className="consent-item-icon"><IconHeart /></div>
              <div>
                <h4>Sempre ao seu lado</h4>
                <p>Se algo te preocupar, te ajudo a entender e te lembro do SAMU 192 e do CVV 188 quando fizer sentido.</p>
              </div>
            </div>
          </div>
        </>
      )
    },
    {
      illu: <IconCalendarHeart style={{ width: 110, height: 110, color: "var(--rosa-forte)" }} />,
      render: (
        <>
          <h3>Os dados que você compartilha comigo</h3>
          <p>
            A LGPD chama dados sobre saúde de <strong>dados sensíveis</strong>.
            Por isso eu só uso o que é necessário e <strong>com sua permissão</strong>.
            Marque abaixo o que você autoriza:
          </p>
          <div className="consent-list">
            <ConsentToggle
              icon={<IconCalendarHeart />}
              title="Lembretes de consultas e exames"
              desc="Data, hora, local, profissional. Servem só pra te avisar."
              checked={consent.finalidades.lembretes}
              onToggle={() => toggleFinalidade("lembretes")}
            />
            <ConsentToggle
              icon={<IconBook />}
              title="Conteúdos educativos materno-infantis"
              desc="Pra te sugerir leituras adequadas ao seu momento."
              checked={consent.finalidades.conteudosEducativos}
              onToggle={() => toggleFinalidade("conteudosEducativos")}
            />
            <ConsentToggle
              icon={<IconHeart />}
              title="Organização e rotinas do puerpério"
              desc="Acompanhar marcos e te dar apoio na sua jornada."
              checked={consent.finalidades.rotinasPuerperio}
              onToggle={() => toggleFinalidade("rotinasPuerperio")}
            />
            <ConsentToggle
              icon={<IconBell />}
              title="Alertas e orientações informativas"
              desc="Avisos importantes (sem promoção, sem spam)."
              checked={consent.finalidades.alertasInformativos}
              onToggle={() => toggleFinalidade("alertasInformativos")}
            />
            <ConsentToggle
              icon={<IconSparkle />}
              title="Informações gerais por município"
              desc="UBS próximas, campanhas locais, contatos públicos."
              checked={consent.finalidades.infoMunicipios}
              onToggle={() => toggleFinalidade("infoMunicipios")}
            />
          </div>
          <p style={{ fontSize: 12.5, marginTop: 6, color: "var(--texto-suave)" }}>
            Você pode mudar qualquer uma dessas opções depois em{" "}
            <Link href="/consentimento" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
              Gerenciar Consentimento
            </Link>
            .
          </p>
        </>
      )
    },
    {
      illu: <IconCheckCircle style={{ width: 110, height: 110, color: "var(--verde-forte)" }} />,
      render: (
        <>
          <h3>Quanto tempo guardo, quem vê e como apagar</h3>
          <p>Resumo simples, sem juridiquês:</p>
          <div className="consent-list">
            <div className="consent-item">
              <div className="consent-item-icon"><IconShield /></div>
              <div>
                <h4>Quem vê seus dados</h4>
                <p>Só você e os sistemas que mantêm o app no ar. Nunca vendemos nem compartilhamos com fins de marketing.</p>
              </div>
            </div>
            <div className="consent-item">
              <div className="consent-item-icon"><IconCalendarHeart /></div>
              <div>
                <h4>Por quanto tempo</h4>
                <p>Enquanto sua conta existir. Registros de acesso por 6 meses (Marco Civil), com sigilo e segurança.</p>
              </div>
            </div>
            <div className="consent-item">
              <div className="consent-item-icon"><IconHeart /></div>
              <div>
                <h4>Você no controle</h4>
                <p>Pode acessar, corrigir, exportar ou apagar tudo a qualquer momento, em <em>Excluir meus dados</em>.</p>
              </div>
            </div>
          </div>
          <p style={{ fontSize: 12.5, marginTop: 4, color: "var(--texto-suave)" }}>
            Quer ler tudo com calma? Veja a{" "}
            <Link href="/privacidade" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
              Política de Privacidade
            </Link>{" "}
            e os{" "}
            <Link href="/termos" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
              Termos de Uso
            </Link>
            . Tudo escrito de um jeito leve.
          </p>
        </>
      )
    }
  ];

  const isLast = step === slides.length - 1;
  const current = slides[step];

  return (
    <div className="consent-overlay" role="dialog" aria-modal="true" aria-label="Boas-vindas e consentimento">
      <div className="consent-card">
        <div className="consent-illu">{current.illu}</div>

        <div className="consent-body">
          <div className="consent-progress" aria-hidden>
            {slides.map((_, i) => (
              <span
                key={i}
                className={i === step ? "active" : i < step ? "done" : ""}
              />
            ))}
          </div>

          {current.render}

          <div className="consent-actions">
            <div className="left">
              {step > 0 && (
                <button type="button" className="consent-back" onClick={prev}>
                  ← Voltar
                </button>
              )}
            </div>
            <div className="right">
              {!isLast && (
                <button type="button" className="btn-primary" onClick={next}>
                  Continuar <IconArrowRight style={{ width: 16, height: 16 }} />
                </button>
              )}
              {isLast && (
                <button type="button" className="btn-primary" onClick={aceitar}>
                  <IconCheckCircle style={{ width: 16, height: 16 }} />
                  Concordar e começar
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConsentToggle({
  icon,
  title,
  desc,
  checked,
  onToggle
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  checked: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="consent-toggle-row">
      <div style={{ width: 32, height: 32, borderRadius: 10, background: "#fff", color: "var(--rosa-forte)", display: "grid", placeItems: "center", flexShrink: 0, border: "1px solid var(--borda)" }}>
        {icon}
      </div>
      <div className="info">
        <h4>{title}</h4>
        <p>{desc}</p>
      </div>
      <label className="toggle">
        <input type="checkbox" checked={checked} onChange={onToggle} />
        <span className="toggle-slider" />
      </label>
    </div>
  );
}
