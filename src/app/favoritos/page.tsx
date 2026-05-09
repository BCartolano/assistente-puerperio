import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import {
  IconBottle,
  IconWindBreath,
  IconMoon,
  IconHeart,
  IconStarFilled,
  IconArrowRight
} from "@/components/Icons";

const favoritos = [
  { Icon: IconBottle, title: "Amamentação sem culpa", desc: "Pega correta e dicas para fissuras.", href: "/conteudo/amamentacao", green: false },
  { Icon: IconWindBreath, title: "Respiração de 5 minutos", desc: "Exercício guiado para acalmar.", href: "/conteudo/respiracao", green: true },
  { Icon: IconMoon, title: "Sono do bebê", desc: "Ritmos e sonecas nas primeiras semanas.", href: "/conteudo/sono-do-bebe", green: false },
  { Icon: IconHeart, title: "Autocompaixão", desc: "Lembrete diário pra você, mãe.", href: "/conteudo/autocompaixao", green: true }
];

export default async function FavoritosPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Favoritos</h1>
            <p>Os conteúdos que você salvou pra ter sempre por perto.</p>
          </div>
          <Link href="/dicas" className="btn-ghost">
            Ver mais dicas
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </header>

        <section className="page-section">
          <h2 className="page-title">Salvos por você</h2>
          <p className="page-subtitle">Acesse rapidinho o que mais tem te ajudado.</p>

          <div className="list-stack" style={{ marginTop: 18 }}>
            {favoritos.map((f) => (
              <article key={f.title} className={`list-row ${f.green ? "green" : ""}`}>
                <div className="list-icon">
                  <f.Icon />
                </div>
                <div className="list-text">
                  <h4>{f.title}</h4>
                  <p>{f.desc}</p>
                </div>
                <Link href={f.href} className="list-action">
                  Abrir <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
                </Link>
              </article>
            ))}
          </div>
        </section>

        <section
          className="page-section"
          style={{
            textAlign: "center",
            background: "linear-gradient(180deg, #fff8eb 0%, #fff3e0 100%)",
            border: "1px solid #f0e0c4",
            borderLeft: "4px solid #d4a574"
          }}
        >
          <p style={{ margin: 0, color: "var(--texto)", display: "inline-flex", alignItems: "center", gap: 8 }}>
            <IconStarFilled style={{ width: 18, height: 18, color: "#d4a574" }} />
            Toque na estrela em qualquer conteúdo para guardar aqui.
          </p>
        </section>
      </main>
    </div>
  );
}
