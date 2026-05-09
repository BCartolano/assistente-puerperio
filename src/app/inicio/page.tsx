import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import { OnboardingConsent } from "@/components/OnboardingConsent";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconBook,
  IconHeart,
  IconBottle,
  IconCalendar,
  IconBell,
  IconArrowRight,
  IconHeartFilled,
  IconLeaf,
  IconSmile,
  IconTired,
  IconCloudRain,
  IconWaves
} from "@/components/Icons";

const apoio = [
  {
    Icon: IconBook,
    title: "Dicas e Conteúdos",
    desc: "Artigos e dicas para te ajudar no puerpério.",
    href: "/dicas"
  },
  {
    Icon: IconHeart,
    title: "Saúde Emocional",
    desc: "Cuide da sua mente e do seu bem-estar.",
    href: "/saude-emocional"
  },
  {
    Icon: IconBottle,
    title: "Cuidados com o Bebê",
    desc: "Tudo sobre o seu bebê, passo a passo.",
    href: "/cuidados-bebe"
  },
  {
    Icon: IconCalendar,
    title: "Minha Jornada",
    desc: "Acompanhe evolução e conquistas.",
    href: "/minha-jornada"
  }
];

const moods = [
  { label: "Bem", Icon: IconSmile, tone: "rose", href: "/conversar" },
  { label: "Cansada", Icon: IconTired, tone: "amber", href: "/conversar" },
  { label: "Sobrecarregada", Icon: IconWaves, tone: "blue", href: "/saude-emocional" },
  { label: "Triste", Icon: IconCloudRain, tone: "lilac", href: "/saude-emocional" }
];

export default async function InicioPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  const firstName = session.name?.split(" ")[0] ?? "mamãe";

  return (
    <>
      <OnboardingConsent />
      <div className="app-shell">
        <SophiaSidebar />

        <main className="app-main">
          <header className="app-main-header">
            <div>
              <h1>
                Olá, {firstName}!
                <IconHeartFilled
                  className="heart-accent"
                  style={{ width: 22, height: 22 }}
                />
              </h1>
              <p>Que bom ter você aqui. Como podemos te apoiar hoje?</p>
            </div>
            <div className="header-actions">
              <Link href="/favoritos" className="notif-bell" aria-label="Favoritos e notificações">
                <IconBell style={{ width: 20, height: 20 }} />
                <span className="notif-badge">3</span>
              </Link>
              <Link href="/meu-perfil" className="user-chip">
                <SophiaAvatar
                  size="xs"
                  className="user-chip-avatar"
                  alt="Foto da Sophia"
                  ring={false}
                />
                <span>{firstName}</span>
              </Link>
            </div>
          </header>

          <DisclaimerMedico variant="compact" />

          <section className="hero-conversa">
            <div className="hero-conversa-image">
              <SophiaAvatar size="xl" alt="Ilustração da Sophia abraçando seu bebê" ring={false} />
            </div>
            <div className="hero-conversa-content">
              <h2>Conversar com a Sophia</h2>
              <p>
                Fale sobre suas dúvidas, sentimentos e desafios. Estou aqui
                pra te escutar com calma e carinho — no seu tempo.
              </p>
              <Link href="/conversar" className="btn-primary">
                Iniciar conversa
                <IconArrowRight style={{ width: 16, height: 16 }} />
              </Link>
            </div>
          </section>

          <h3 className="section-title">Apoio para cada momento</h3>
          <div className="tile-grid">
            {apoio.map((a) => (
              <Link key={a.title} href={a.href} className="tile">
                <div className="tile-icon">
                  <a.Icon />
                </div>
                <h4 className="tile-title">{a.title}</h4>
                <p className="tile-desc">{a.desc}</p>
                <span className="tile-arrow">
                  <IconArrowRight style={{ width: 14, height: 14 }} />
                </span>
              </Link>
            ))}
          </div>

          <h3 className="section-title">Como você está se sentindo hoje?</h3>
          <p className="section-subtitle">É importante reconhecer seus sentimentos.</p>
          <div className="mood-group">
            {moods.map((m) => (
              <Link
                key={m.label}
                href={m.href}
                className={`mood-btn tone-${m.tone}`}
              >
                <m.Icon className="mood-icon" />
                <span>{m.label}</span>
              </Link>
            ))}
          </div>

          <div className="reminder-card" style={{ marginTop: 24 }}>
            <div>
              <h4>Lembrete de cuidado</h4>
              <p>
                Você merece cuidado, descanso e apoio. Pequenos passos
                contam. Respira fundo — eu estou aqui.
              </p>
            </div>
            <div className="reminder-icon">
              <IconLeaf />
            </div>
          </div>
        </main>

        <aside className="app-right">
          <div className="right-card">
            <h3>Botões</h3>
            <div className="stack">
              <Link href="/conversar" className="btn-primary">
                Conversar com Sophia
              </Link>
              <Link href="/dicas" className="btn-secondary">
                Ver dicas
              </Link>
              <Link href="/minha-jornada" className="btn-ghost">
                Minha jornada
              </Link>
            </div>
          </div>

          <div className="right-card">
            <h3>Conteúdos rápidos</h3>
            <div className="right-tabs">
              <Link href="/dicas" className="active">Dicas</Link>
              <Link href="/saude-emocional">Emocional</Link>
              <Link href="/cuidados-bebe">Bebê</Link>
            </div>
            <Link href="/conteudo/amamentacao" className="mini-content-card">
              <span className="mini-tag">Dica</span>
              <p className="mini-title">Amamentação: primeiros passos com confiança</p>
              <p className="mini-desc">
                Tudo que você precisa saber pra começar bem, com leveza.
              </p>
            </Link>
          </div>
        </aside>
      </div>
    </>
  );
}
