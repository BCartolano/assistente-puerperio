import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconHome,
  IconBottle,
  IconMoon,
  IconHeart,
  IconUmbilical,
  IconUsers,
  IconChat,
  IconArrowRight,
  IconLeaf
} from "@/components/Icons";

const fases = [
  { Icon: IconHome, title: "Resguardo (40 dias)", desc: "Repouso, recuperação física e emocional.", href: "/conteudo/resguardo" },
  { Icon: IconBottle, title: "Amamentação", desc: "Pega correta, livre demanda e fissuras.", href: "/conteudo/amamentacao" },
  { Icon: IconMoon, title: "Sono fragmentado", desc: "Ritmos do bebê e como você pode descansar.", href: "/conteudo/sono-fragmentado" },
  { Icon: IconHeart, title: "Saúde emocional", desc: "Baby blues, ansiedade e quando buscar acolhimento.", href: "/saude-emocional" },
  { Icon: IconUmbilical, title: "Recuperação do corpo", desc: "Lóquios, pontos, retorno do ciclo.", href: "/conteudo/recuperacao-corpo" },
  { Icon: IconUsers, title: "Rede de apoio", desc: "Aceitar e organizar a ajuda das pessoas próximas.", href: "/conteudo/rede-de-apoio" }
];

export default async function PosPartoPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Pós-Parto</h1>
            <p>Apoio para os primeiros dias com o bebê e para você.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Conversar agora
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <section className="hero-conversa" style={{ marginBottom: 18 }}>
          <div className="hero-conversa-image">
            <SophiaAvatar size="xl" ring={false} />
          </div>
          <div className="hero-conversa-content">
            <h2>Você também precisa de cuidado</h2>
            <p>O puerpério não é só do bebê. Veja nossos atalhos para cuidar de você.</p>
            <Link href="/saude-emocional" className="btn-secondary">
              Cuidar de mim
              <IconArrowRight style={{ width: 16, height: 16 }} />
            </Link>
          </div>
        </section>

        <h3 className="section-title">O que esperar</h3>
        <p className="section-subtitle">Temas frequentes que a Sophia separou pra você.</p>
        <div className="tile-grid cols-3">
          {fases.map((f) => (
            <Link key={f.title} href={f.href} className="tile">
              <div className="tile-icon"><f.Icon /></div>
              <h4 className="tile-title">{f.title}</h4>
              <p className="tile-desc">{f.desc}</p>
            </Link>
          ))}
        </div>

        <div className="reminder-card" style={{ marginTop: 20 }}>
          <div>
            <h4>Lembrete carinhoso</h4>
            <p>Você acabou de fazer um milagre. Seu corpo merece reverência. Aceite ajuda — sem pesar.</p>
          </div>
          <div className="reminder-icon"><IconLeaf /></div>
        </div>
      </main>
    </div>
  );
}
