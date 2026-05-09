import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { IconNotebook, IconChat, IconArrowRight } from "@/components/Icons";

type Stage = {
  date: string;
  title: string;
  desc: string;
  done?: boolean;
};

const timeline: Stage[] = [
  { date: "Semana 1", title: "Chegada do bebê", desc: "Resguardo, amamentação inicial e descanso. Você está indo bem.", done: true },
  { date: "Semana 2", title: "Primeira consulta do bebê", desc: "Pediatra, peso e reforço sobre amamentação.", done: true },
  { date: "Semana 4", title: "Check-in emocional", desc: "Hora de conversar com a Sophia sobre como você está se sentindo." },
  { date: "Semana 6", title: "Revisão pós-parto", desc: "Consulta com seu obstetra/ginecologista para avaliar recuperação." },
  { date: "Mês 3", title: "Volta ao corpo aos poucos", desc: "Atividade física leve com liberação médica. Sem pressa." },
  { date: "Mês 6", title: "Introdução alimentar", desc: "Marco do bebê: novos sabores, novas rotinas." }
];

export default async function MinhaJornadaPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Minha Jornada</h1>
            <p>Cada passo importa. Acompanhe seus marcos com gentileza.</p>
          </div>
          <Link href="/conversar" className="btn-secondary">
            <IconChat style={{ width: 16, height: 16 }} />
            Registrar com Sophia
          </Link>
        </header>

        <section className="page-section">
          <h2 className="page-title">Linha do tempo do puerpério</h2>
          <p className="page-subtitle">Marcos sugeridos. Você pode pular, repetir ou voltar quando precisar.</p>

          <div className="journey" style={{ marginTop: 24 }}>
            {timeline.map((step) => (
              <article key={step.title} className={`journey-item ${step.done ? "done" : ""}`}>
                <p className="journey-date">{step.date}</p>
                <h4>{step.title}</h4>
                <p>{step.desc}</p>
              </article>
            ))}
          </div>
        </section>

        <div className="reminder-card">
          <div>
            <h4>Diário do dia</h4>
            <p>Que tal escrever uma frase sobre como você está agora? Eu posso te ajudar.</p>
          </div>
          <Link href="/conteudo/diario-sentimentos" className="btn-primary">
            <IconNotebook style={{ width: 16, height: 16 }} />
            Escrever
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </div>
      </main>
    </div>
  );
}
