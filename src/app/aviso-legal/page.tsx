import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import {
  IconAlertCircle,
  IconHeart,
  IconArrowRight,
  IconLibrary,
  IconChat,
  IconShield,
  IconDocument
} from "@/components/Icons";

export default async function AvisoLegalPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Aviso Legal</h1>
            <p>O escopo desta plataforma e o respeito ao seu cuidado.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Conversar com Sophia
          </Link>
        </header>

        <section
          className="page-section"
          style={{
            background: "linear-gradient(180deg, #fff8eb 0%, #fff3e0 100%)",
            border: "1px solid #f0e0c4",
            borderLeft: "4px solid #d4a574"
          }}
        >
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
            <div
              style={{
                width: 50,
                height: 50,
                borderRadius: 14,
                background: "#fff",
                color: "#a06a32",
                display: "grid",
                placeItems: "center",
                flexShrink: 0,
                border: "1px solid #f0d9b0"
              }}
            >
              <IconAlertCircle style={{ width: 24, height: 24 }} />
            </div>
            <div>
              <h2 className="page-title" style={{ marginTop: 0, color: "#8a6a32" }}>
                Quem é a Sophia
              </h2>
              <p style={{ lineHeight: 1.7, color: "var(--texto)" }}>
                A Sophia é uma <strong>assistente virtual (IA)</strong> de
                <strong> apoio educativo e acolhimento</strong>, baseada em
                fontes oficiais (Cadernetas da Gestante e da Criança do
                Ministério da Saúde, Manual Técnico do SUS de Pré-Natal e
                Puerpério e bibliografia reconhecida).{" "}
                <strong>
                  Ela não realiza consulta médica, psicológica, diagnóstico,
                  prescrição ou tratamento
                </strong>
                , em conformidade com a{" "}
                <strong>Lei nº 12.842/2013 (Lei do Ato Médico)</strong>,
                Resoluções do CFM/CFP e princípios de transparência de IA
                discutidos no PL 2.338/2023.
              </p>
            </div>
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">O que esta plataforma faz</h2>
          <ul style={{ marginTop: 14, paddingLeft: 20, lineHeight: 1.8, color: "var(--texto)" }}>
            <li>Oferece <strong>conteúdo educativo</strong> sobre gestação, parto, puerpério e cuidados com o bebê.</li>
            <li>Acolhe a mãe em momentos de cansaço, ansiedade ou dúvida — com escuta gentil e não-julgadora.</li>
            <li>Indica, com carinho, <strong>quando vale procurar a equipe de saúde</strong>.</li>
            <li>Aponta canais de apoio em situação de crise: <strong>SAMU 192</strong>, <strong>CVV 188</strong>, ouvidorias e serviços do SUS.</li>
            <li>Cita explicitamente as fontes oficiais que embasam cada tópico.</li>
          </ul>
        </section>

        <section className="page-section">
          <h2 className="page-title">O que esta plataforma NÃO faz</h2>
          <ul style={{ marginTop: 14, paddingLeft: 20, lineHeight: 1.8, color: "var(--texto)" }}>
            <li><strong>Não diagnostica</strong> nenhuma condição clínica, da mãe ou do bebê.</li>
            <li><strong>Não prescreve</strong> medicamentos, suplementos, dosagens ou tratamentos.</li>
            <li><strong>Não faz</strong> psicoterapia, avaliação psicológica ou plano terapêutico individualizado.</li>
            <li><strong>Não substitui</strong> consulta com médico(a), enfermeiro(a), nutricionista, psicólogo(a), fisioterapeuta, fonoaudiólogo(a) ou outros profissionais.</li>
            <li><strong>Não emite</strong> atestados, laudos, receitas ou documentos médico-legais.</li>
            <li><strong>Não promete</strong> cura, resolução de sintomas ou resultados em saúde.</li>
          </ul>
        </section>

        <section className="page-section">
          <h2 className="page-title">Em caso de dúvida ou emergência</h2>
          <div className="tile-grid cols-3" style={{ marginTop: 16 }}>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon"><IconAlertCircle /></div>
              <span className="tile-badge rose">Emergência médica</span>
              <h4 className="tile-title">SAMU — 192</h4>
              <p className="tile-desc">Atendimento gratuito 24h em todo o Brasil.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconHeart /></div>
              <span className="tile-badge">Apoio emocional</span>
              <h4 className="tile-title">CVV — 188</h4>
              <p className="tile-desc">Centro de Valorização da Vida — sigiloso, gratuito, 24h.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon"><IconLibrary /></div>
              <span className="tile-badge rose">Atendimento</span>
              <h4 className="tile-title">UBS / Disque-Saúde — 136</h4>
              <p className="tile-desc">Disque-Saúde do Ministério da Saúde — orientações sobre serviços.</p>
            </article>
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">Bases legais</h2>
          <ul style={{ marginTop: 12, lineHeight: 1.7, color: "var(--texto)", paddingLeft: 20 }}>
            <li><strong>Lei nº 12.842/2013</strong> (Ato Médico) — diagnóstico, prescrição e procedimentos invasivos são privativos do médico.</li>
            <li><strong>Resoluções do CFP</strong> — psicoterapia, avaliação psicológica e plano terapêutico são exclusivos de profissional habilitado.</li>
            <li><strong>LGPD (Lei 13.709/2018)</strong> — base de tratamento dos seus dados, com ênfase em dados sensíveis (saúde).</li>
            <li><strong>Marco Civil da Internet (Lei 12.965/2014)</strong> — registros de acesso por 6 meses, sob sigilo.</li>
            <li><strong>CDC (Lei 8.078/1990)</strong> — informação clara, sem promessas indevidas.</li>
            <li><strong>PL 2.338/2023</strong> — princípios de transparência sobre uso de IA em contextos sensíveis.</li>
          </ul>
        </section>

        <section className="page-section">
          <h2 className="page-title">Documentos relacionados</h2>
          <div className="tile-grid cols-3" style={{ marginTop: 14 }}>
            <Link href="/privacidade" className="tile">
              <div className="tile-icon"><IconShield /></div>
              <h4 className="tile-title">Política de Privacidade</h4>
              <p className="tile-desc">Como cuido das suas informações.</p>
            </Link>
            <Link href="/termos" className="tile">
              <div className="tile-icon"><IconDocument /></div>
              <h4 className="tile-title">Termos de Uso</h4>
              <p className="tile-desc">O combinado entre nós, em linguagem leve.</p>
            </Link>
            <Link href="/referencias" className="tile">
              <div className="tile-icon green"><IconLibrary /></div>
              <h4 className="tile-title">Referências</h4>
              <p className="tile-desc">Bibliografia oficial que sustenta os conteúdos.</p>
            </Link>
          </div>
        </section>

        <section className="reminder-card">
          <div>
            <h4>Quer entender melhor as fontes?</h4>
            <p>Veja a bibliografia completa que sustenta cada tópico do app.</p>
          </div>
          <Link href="/referencias" className="btn-secondary">
            Ver Referências
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </section>
      </main>
    </div>
  );
}
