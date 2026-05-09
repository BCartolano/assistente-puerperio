import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconCloudRain,
  IconWindBreath,
  IconNotebook,
  IconHands,
  IconHeart,
  IconUsers,
  IconSmile,
  IconTired,
  IconWaves,
  IconChat,
  IconLeaf
} from "@/components/Icons";

const recursos = [
  { Icon: IconCloudRain, title: "Baby blues x depressão", desc: "Como diferenciar a tristeza passageira de algo que pede acolhimento.", href: "/conteudo/baby-blues" },
  { Icon: IconWindBreath, title: "Respiração de 5 minutos", desc: "Exercício guiado para acalmar quando tudo aperta.", href: "/conteudo/respiracao" },
  { Icon: IconNotebook, title: "Diário de sentimentos", desc: "Escrever liberta. Registre como você está em poucas palavras.", href: "/conteudo/diario-sentimentos" },
  { Icon: IconHands, title: "Quando buscar acolhimento profissional", desc: "Sinais para conversar com obstetra, doula ou psicóloga.", href: "/conteudo/quando-procurar-ajuda" },
  { Icon: IconHeart, title: "Autocompaixão", desc: "Você está fazendo o melhor que pode. Respira, mãe.", href: "/conteudo/autocompaixao" },
  { Icon: IconUsers, title: "Conversa com o parceiro", desc: "Roteiro para falar de divisão de tarefas e carga mental.", href: "/conteudo/conversa-com-parceiro" }
];

const moods = [
  { label: "Bem", Icon: IconSmile, tone: "rose" },
  { label: "Cansada", Icon: IconTired, tone: "amber" },
  { label: "Sobrecarregada", Icon: IconWaves, tone: "blue" },
  { label: "Triste", Icon: IconCloudRain, tone: "lilac" },
  { label: "Irritada", Icon: IconCloudRain, tone: "coral" },
  { label: "Acolhida", Icon: IconHeart, tone: "green" }
];

export default async function SaudeEmocionalPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Saúde Emocional</h1>
            <p>Cuide de você com a mesma ternura que cuida do seu bebê.</p>
          </div>
          <Link href="/conversar" className="btn-secondary">
            <IconChat style={{ width: 16, height: 16 }} />
            Falar com a Sophia
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <section className="page-section">
          <h2 className="page-title">Como você está se sentindo agora?</h2>
          <p className="page-subtitle">Reconhecer o sentimento já é um cuidado.</p>
          <div className="mood-group">
            {moods.map((m) => (
              <Link key={m.label} href="/conversar" className={`mood-btn tone-${m.tone}`}>
                <m.Icon className="mood-icon" />
                {m.label}
              </Link>
            ))}
          </div>
        </section>

        <h3 className="section-title">Recursos para hoje</h3>
        <p className="section-subtitle">Conteúdos rápidos, gentis e práticos para qualquer momento do dia.</p>
        <div className="tile-grid cols-3">
          {recursos.map((r) => (
            <Link key={r.title} href={r.href} className="tile">
              <div className="tile-icon green">
                <r.Icon />
              </div>
              <h4 className="tile-title">{r.title}</h4>
              <p className="tile-desc">{r.desc}</p>
            </Link>
          ))}
        </div>

        <div className="reminder-card" style={{ marginTop: 24 }}>
          <div>
            <h4>Lembrete do dia</h4>
            <p>Você não precisa dar conta de tudo sozinha. Pedir ajuda também é cuidar do bebê.</p>
          </div>
          <div className="reminder-icon"><IconLeaf /></div>
        </div>
      </main>
    </div>
  );
}
