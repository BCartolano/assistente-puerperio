import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import {
  IconShield,
  IconHeart,
  IconCalendarHeart,
  IconBell,
  IconBook,
  IconCheckCircle,
  IconArrowRight,
  IconInfo,
  IconHands,
  IconSparkle,
  IconLock
} from "@/components/Icons";

const cards = [
  {
    Icon: IconShield,
    title: "Por que isso importa, na boa",
    text: "Você está dividindo coisas íntimas comigo — saúde, sentimentos, rotina, seu bebê. A LGPD chama isso de dados sensíveis. Por isso, o cuidado com eles é tão importante quanto o cuidado com você."
  },
  {
    Icon: IconCalendarHeart,
    title: "O que você compartilha (e por quê)",
    text: "Lembretes de consultas, organização do puerpério, conteúdos que combinam com seu momento, alertas e infos do seu município — tudo só com a sua autorização. Você pode tirar qualquer permissão a qualquer hora."
  },
  {
    Icon: IconLock,
    title: "Quem pode ver",
    text: "Só você e os sistemas que mantêm o app de pé. Não vendemos, não trocamos, não usamos pra te perseguir com publicidade. Quem entra na sua conta é você, com sua senha."
  },
  {
    Icon: IconBell,
    title: "Por quanto tempo eu guardo",
    text: "Enquanto sua conta existir, pra que tudo funcione bem. Registros de acesso (quando você entrou) ficam guardados por 6 meses, com sigilo, conforme o Marco Civil da Internet."
  },
  {
    Icon: IconHeart,
    title: "Você no controle, sempre",
    text: "Pode acessar, corrigir, exportar ou apagar tudo a qualquer momento. Em Excluir meus dados a gente faz isso juntas — sem burocracia, com cuidado e confirmação."
  },
  {
    Icon: IconHands,
    title: "Quando algo der errado",
    text: "Se houver qualquer incidente que toque seus dados, eu te aviso. Você é a primeira a saber, e a gente passa por isso junto."
  }
];

export default async function PrivacidadePage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Política de Privacidade</h1>
            <p>
              Sem juridiquês. Vou te contar, em linguagem de gente, como
              cuido das suas informações.
            </p>
          </div>
          <Link href="/consentimento" className="btn-secondary">
            Gerenciar consentimento
            <IconArrowRight style={{ width: 16, height: 16 }} />
          </Link>
        </header>

        <section
          className="page-section"
          style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 22, alignItems: "center" }}
        >
          <SophiaAvatar size="lg" alt="Sophia te explicando privacidade com calma" />
          <div>
            <h2 className="page-title">A versão curta, no carinho</h2>
            <p style={{ marginTop: 8, fontSize: 15.5, lineHeight: 1.65 }}>
              Você compartilha comigo coisas íntimas — e eu trato isso como
              sagrado. Só uso o que é necessário, só com a sua permissão, e
              <strong> nunca vendo, nunca compartilho com publicidade</strong>.
              Você pode mudar tudo, ver tudo e apagar tudo a qualquer
              momento. É a sua história.
            </p>
          </div>
        </section>

        <h3 className="section-title">Em 6 cards, o essencial</h3>
        <p className="section-subtitle">Sem letra miúda. Linguagem leve, direto ao que importa.</p>

        <div className="tile-grid cols-3">
          {cards.map((c) => (
            <article key={c.title} className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon">
                <c.Icon />
              </div>
              <h4 className="tile-title">{c.title}</h4>
              <p className="tile-desc">{c.text}</p>
            </article>
          ))}
        </div>

        <section className="page-section" style={{ marginTop: 24 }}>
          <h2 className="page-title">Quais dados eu posso usar (com a sua permissão)</h2>
          <p className="page-subtitle">Cada item só é ativado se você marcar em <em>Gerenciar Consentimento</em>.</p>
          <div className="list-stack" style={{ marginTop: 16 }}>
            <PrivItem
              Icon={IconCalendarHeart}
              title="Lembretes de consultas e exames"
              desc="Data, hora, local, profissional — pra que você não dependa só da memória num momento já cheio. Esses dados servem só pra te avisar."
            />
            <PrivItem
              Icon={IconHeart}
              title="Organização e rotinas do puerpério"
              desc="Marcos da sua jornada, anotações, sentimentos do dia. Servem pra te dar continuidade no acolhimento."
              green
            />
            <PrivItem
              Icon={IconBook}
              title="Conteúdos educativos materno-infantis"
              desc="Pra te sugerir leituras alinhadas com o seu momento. Nada que vire publicidade."
            />
            <PrivItem
              Icon={IconBell}
              title="Alertas e orientações informativas"
              desc="Avisos importantes (recall, campanha de vacinação local, etc), sem promoção comercial."
              green
            />
            <PrivItem
              Icon={IconSparkle}
              title="Informações gerais por município"
              desc="UBS próxima, contatos públicos do SUS, campanhas locais. Não te localizamos em tempo real — só cidade."
            />
          </div>
          <p style={{ marginTop: 14, fontSize: 13, color: "var(--texto-suave)" }}>
            Quer mudar agora? Vai em{" "}
            <Link href="/consentimento" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
              Gerenciar Consentimento
            </Link>
            .
          </p>
        </section>

        <section className="page-section">
          <h2 className="page-title">Seus direitos (LGPD, art. 18)</h2>
          <p className="page-subtitle">Esses direitos são seus por lei. Aqui são fáceis de usar.</p>
          <div className="tile-grid cols-3" style={{ marginTop: 16 }}>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconCheckCircle /></div>
              <h4 className="tile-title">Acessar e ver tudo</h4>
              <p className="tile-desc">Você pede, eu mostro tudo o que existe associado a você.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconCheckCircle /></div>
              <h4 className="tile-title">Corrigir o que estiver errado</h4>
              <p className="tile-desc">Nome trocado, email novo, anotação imprecisa — você ajusta.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconCheckCircle /></div>
              <h4 className="tile-title">Apagar tudo</h4>
              <p className="tile-desc">Sem perguntas constrangedoras — só uma confirmação carinhosa.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconCheckCircle /></div>
              <h4 className="tile-title">Levar com você (portabilidade)</h4>
              <p className="tile-desc">Exporta seus dados num arquivo simples, quando quiser.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconCheckCircle /></div>
              <h4 className="tile-title">Revogar consentimento</h4>
              <p className="tile-desc">Tirou a permissão? Pronto, paramos de usar aquilo.</p>
            </article>
            <article className="tile" style={{ cursor: "default" }}>
              <div className="tile-icon green"><IconCheckCircle /></div>
              <h4 className="tile-title">Falar com a ANPD</h4>
              <p className="tile-desc">Se quiser denunciar algo, você pode procurar a Autoridade Nacional de Proteção de Dados.</p>
            </article>
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">Bases legais e leis em que me apoio</h2>
          <ul style={{ marginTop: 14, paddingLeft: 20, lineHeight: 1.8, color: "var(--texto)" }}>
            <li>
              <strong>LGPD (Lei 13.709/2018)</strong> — dados pessoais
              sensíveis (saúde, dados emocionais, dados sobre o bebê) são
              tratados com base no <em>consentimento específico e
              destacado</em> que você dá em <Link href="/consentimento" style={{ color: "var(--rosa-forte)" }}>Gerenciar Consentimento</Link>.
            </li>
            <li>
              <strong>Marco Civil da Internet (Lei 12.965/2014)</strong> —
              registros de acesso são guardados por 6 meses, sob sigilo,
              podendo ser fornecidos apenas mediante ordem judicial.
            </li>
            <li>
              <strong>CDC (Lei 8.078/1990)</strong> — informação clara,
              sem promessas falsas, sem publicidade enganosa.
            </li>
            <li>
              <strong>Lei do Ato Médico (12.842/2013) e Resoluções do
              CFM/CFP</strong> — Sophia é apoio educativo. Diagnóstico,
              prescrição e psicoterapia são exclusividades de profissionais
              habilitados.
            </li>
          </ul>
        </section>

        <section className="reminder-card">
          <div>
            <h4>Quer falar com uma pessoa?</h4>
            <p>
              Para qualquer dúvida sobre seus dados, escreve pra <strong>privacidade@sophia.app</strong>.
              A gente responde com calma, em até 15 dias.
            </p>
          </div>
          <div className="reminder-icon"><IconInfo /></div>
        </section>
      </main>
    </div>
  );
}

function PrivItem({
  Icon,
  title,
  desc,
  green = false
}: {
  Icon: typeof IconShield;
  title: string;
  desc: string;
  green?: boolean;
}) {
  return (
    <article className={`list-row ${green ? "green" : ""}`}>
      <div className="list-icon"><Icon /></div>
      <div className="list-text">
        <h4>{title}</h4>
        <p>{desc}</p>
      </div>
    </article>
  );
}
