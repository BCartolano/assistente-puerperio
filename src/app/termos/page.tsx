import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import {
  IconDocument,
  IconHeart,
  IconHands,
  IconSparkle,
  IconShield,
  IconArrowRight,
  IconCheckCircle,
  IconAlertCircle
} from "@/components/Icons";

const promessas = [
  {
    Icon: IconHeart,
    title: "Acolho com carinho",
    text: "Conversa sem julgamento, escuta atenta, linguagem leve."
  },
  {
    Icon: IconDocument,
    title: "Informo com base oficial",
    text: "Conteúdo educativo a partir de Cadernetas do Ministério da Saúde, Manual Técnico do SUS e bibliografia reconhecida."
  },
  {
    Icon: IconHands,
    title: "Te encaminho quando preciso",
    text: "Quando algo pede um olhar de pertinho, eu te lembro com gentileza dos canais (UBS, SAMU 192, CVV 188)."
  },
  {
    Icon: IconShield,
    title: "Cuido dos seus dados",
    text: "Só uso o que você autorizar, com finalidades claras (LGPD, art. 11)."
  }
];

const naoFaco = [
  "Não dou diagnóstico médico ou psicológico.",
  "Não prescrevo medicamentos, doses, dietas ou condutas.",
  "Não faço terapia, psicoterapia, avaliação psicológica ou plano terapêutico.",
  "Não emito laudos, atestados, receitas ou documentos médico-legais.",
  "Não substituo seu obstetra, pediatra, psicóloga, nutricionista, fisioterapeuta nem qualquer outro profissional habilitado.",
  "Não faço promessas de cura, resultado ou solução para qualquer sintoma."
];

export default async function TermosPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Termos de Uso</h1>
            <p>O que combinamos pra essa relação fluir bem — sem letrinha miúda.</p>
          </div>
          <Link href="/privacidade" className="btn-ghost">
            Política de Privacidade
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </header>

        <section
          className="page-section"
          style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 22, alignItems: "center" }}
        >
          <SophiaAvatar size="lg" alt="Sophia te explicando os termos com leveza" />
          <div>
            <h2 className="page-title">Como a gente combina, em uma linha</h2>
            <p style={{ marginTop: 8, fontSize: 15.5, lineHeight: 1.65 }}>
              Eu, <strong>Sophia</strong>, sou uma assistente virtual (IA) de
              apoio educativo e acolhimento. Você usa o app pra se cuidar e
              eu cuido de te oferecer informação confiável e escuta amorosa
              — <strong>sem substituir profissionais de saúde</strong>.
            </p>
          </div>
        </section>

        <h3 className="section-title">O que eu prometo, na real</h3>
        <p className="section-subtitle">Compromissos simples, em linguagem que cabe na rotina.</p>
        <div className="tile-grid cols-2">
          {promessas.map((p) => (
            <article key={p.title} className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon">
                <p.Icon />
              </div>
              <h4 className="tile-title">{p.title}</h4>
              <p className="tile-desc">{p.text}</p>
            </article>
          ))}
        </div>

        <section className="page-section" style={{ marginTop: 24 }}>
          <h2 className="page-title">O que eu não faço</h2>
          <p className="page-subtitle">
            Pra te proteger, e em respeito à Lei do Ato Médico (12.842/2013)
            e às Resoluções do CFP.
          </p>
          <div className="list-stack" style={{ marginTop: 14 }}>
            {naoFaco.map((item) => (
              <article key={item} className="list-row">
                <div className="list-icon" style={{ background: "#fff5e6", color: "#a06a32" }}>
                  <IconAlertCircle />
                </div>
                <div className="list-text">
                  <p style={{ margin: 0, fontSize: 14, lineHeight: 1.5 }}>{item}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">O que esperamos da nossa convivência</h2>
          <ul style={{ marginTop: 14, paddingLeft: 20, lineHeight: 1.8, color: "var(--texto)" }}>
            <li>
              Use o app para apoio educativo e acolhimento. Em emergências,
              <strong> sempre </strong>procure SAMU 192 ou serviço de urgência.
            </li>
            <li>
              Mantenha sua senha em segredo. Sua conta é sua.
            </li>
            <li>
              Não use a Sophia para finalidade ilícita ou que cause dano a
              outras pessoas.
            </li>
            <li>
              Não tente extrair, copiar ou reutilizar conteúdos do app fora
              do seu uso pessoal — eles existem pra te servir.
            </li>
            <li>
              Se você for menor de 18 anos, peça acompanhamento de uma
              pessoa adulta de confiança.
            </li>
          </ul>
        </section>

        <section className="page-section">
          <h2 className="page-title">Em caso de emergência</h2>
          <div className="tile-grid cols-3" style={{ marginTop: 14 }}>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon"><IconAlertCircle /></div>
              <h4 className="tile-title">SAMU — 192</h4>
              <p className="tile-desc">Emergência médica, 24h, gratuito.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconHeart /></div>
              <h4 className="tile-title">CVV — 188</h4>
              <p className="tile-desc">Apoio emocional, sigiloso, 24h.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon"><IconSparkle /></div>
              <h4 className="tile-title">UBS / Disque-Saúde — 136</h4>
              <p className="tile-desc">Orientação sobre serviços do SUS.</p>
            </article>
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">Mudanças nestes termos</h2>
          <p style={{ marginTop: 8, lineHeight: 1.7, color: "var(--texto)" }}>
            Se algo aqui mudar, eu aviso por dentro do app, em local
            visível, antes de aplicar. Você pode aceitar, ajustar
            consentimentos, ou pedir saída — sem rancor, com cuidado.
          </p>
        </section>

        <section className="reminder-card">
          <div>
            <h4>Tem dúvida?</h4>
            <p>
              Escreve pra <strong>contato@sophia.app</strong> ou volte pra{" "}
              <Link href="/aviso-legal" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
                Aviso Legal
              </Link>{" "}
              pra ver o detalhamento das nossas bases legais.
            </p>
          </div>
          <div className="reminder-icon"><IconCheckCircle /></div>
        </section>
      </main>
    </div>
  );
}
