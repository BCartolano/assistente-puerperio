import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconMother,
  IconBottle,
  IconMoon,
  IconHeart,
  IconLeaf,
  IconWarmDrink,
  IconUsers,
  IconBath,
  IconFlower,
  IconArrowRight,
  IconChat
} from "@/components/Icons";

const conteudos = [
  { Icon: IconMother, title: "Os primeiros 40 dias", desc: "O que esperar do resguardo, repouso e cuidados básicos.", badge: "Essencial", href: "/conteudo/primeiros-40-dias" },
  { Icon: IconBottle, title: "Amamentação sem culpa", desc: "Pega correta, livre demanda e dicas para fissuras.", badge: "Popular", href: "/conteudo/amamentacao" },
  { Icon: IconMoon, title: "Sono do bebê", desc: "Ritmos, sonecas e o famoso 'sono leve' nas primeiras semanas.", badge: "Novo", href: "/conteudo/sono-do-bebe" },
  { Icon: IconHeart, title: "Saúde emocional materna", desc: "Baby blues, ansiedade e quando buscar acolhimento.", badge: "Cuidado", href: "/saude-emocional" },
  { Icon: IconLeaf, title: "Autocuidado possível", desc: "Pequenos gestos que cabem na rotina e fazem diferença.", badge: "Gentil", href: "/conteudo/autocuidado" },
  { Icon: IconWarmDrink, title: "Alimentação no puerpério", desc: "Comidas que ajudam na recuperação e na produção de leite.", badge: "Energia", href: "/conteudo/alimentacao-pos-parto" },
  { Icon: IconUsers, title: "Rede de apoio", desc: "Como pedir ajuda sem culpa e organizar o que delegar.", badge: "Apoio", href: "/conteudo/rede-de-apoio" },
  { Icon: IconBath, title: "Banho do recém-nascido", desc: "Passo a passo seguro para o primeiro banho em casa.", badge: "Prático", href: "/conteudo/banho-do-bebe" },
  { Icon: IconFlower, title: "Sexualidade no pós-parto", desc: "Conversa franca sobre desejo, corpo e tempo de cada uma.", badge: "Honesto", href: "/conteudo/sexualidade-pos-parto" }
];

export default async function DicasPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Dicas e Conteúdos</h1>
            <p>Conteúdos curtos e acolhedores para te apoiar nessa fase.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Conversar com Sophia
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <h3 className="section-title">Para você ler hoje</h3>
        <p className="section-subtitle">Selecionados pela Sophia com base nos primeiros meses pós-parto.</p>

        <div className="tile-grid cols-3">
          {conteudos.map((c) => (
            <Link key={c.title} href={c.href} className="tile">
              <div className="tile-icon">
                <c.Icon />
              </div>
              <span className="tile-badge rose">{c.badge}</span>
              <h4 className="tile-title">{c.title}</h4>
              <p className="tile-desc">{c.desc}</p>
              <span className="tile-arrow">
                Ler <IconArrowRight style={{ width: 14, height: 14 }} />
              </span>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
