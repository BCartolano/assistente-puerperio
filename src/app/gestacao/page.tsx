import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconSeed,
  IconRose,
  IconFlower,
  IconBottle,
  IconMother,
  IconChat,
  IconArrowRight
} from "@/components/Icons";

const tris = [
  { Icon: IconSeed, title: "1º trimestre", desc: "Náuseas, sono e adaptação. Cuidados iniciais.", href: "/conteudo/trimestre-1" },
  { Icon: IconRose, title: "2º trimestre", desc: "Energia voltando, exames e movimentos do bebê.", href: "/conteudo/trimestre-2" },
  { Icon: IconFlower, title: "3º trimestre", desc: "Preparação para o parto, plano de parto e mala.", href: "/conteudo/trimestre-3" }
];

export default async function GestacaoPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Gestação</h1>
            <p>Conteúdo educativo para cada trimestre — não substitui pré-natal.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Conversar com a Sophia
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <h3 className="section-title">Cada fase tem seu cuidado</h3>
        <p className="section-subtitle">Toque no trimestre que você está vivendo agora.</p>
        <div className="tile-grid cols-3">
          {tris.map((t) => (
            <Link key={t.title} href={t.href} className="tile">
              <div className="tile-icon green"><t.Icon /></div>
              <h4 className="tile-title">{t.title}</h4>
              <p className="tile-desc">{t.desc}</p>
            </Link>
          ))}
        </div>

        <h3 className="section-title">Próximos passos</h3>
        <div className="list-stack">
          <article className="list-row">
            <div className="list-icon"><IconBottle /></div>
            <div className="list-text">
              <h4>Preparação para o parto</h4>
              <p>Saiba o que esperar do dia do nascimento.</p>
            </div>
            <Link href="/parto" className="list-action">
              Ir para Parto <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>
          <article className="list-row green">
            <div className="list-icon"><IconMother /></div>
            <div className="list-text">
              <h4>Pós-parto</h4>
              <p>Resguardo, amamentação e recuperação.</p>
            </div>
            <Link href="/pos-parto" className="list-action">
              Ir para Pós-parto <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
            </Link>
          </article>
        </div>
      </main>
    </div>
  );
}
