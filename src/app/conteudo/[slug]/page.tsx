import Link from "next/link";
import { redirect, notFound } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import { getTopico, getAllSlugs } from "@/lib/topicos";
import { getFonte } from "@/lib/referencias";
import { IconArrowLeft, IconChat, IconArrowRight, IconHeart } from "@/components/Icons";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return getAllSlugs().map((slug) => ({ slug }));
}

export default async function ConteudoPage({ params }: Props) {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  const { slug } = await params;
  const topico = getTopico(slug);
  if (!topico) notFound();

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            {topico.voltarPara && (
              <Link
                href={topico.voltarPara.href}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 13,
                  color: "var(--texto-suave)",
                  textDecoration: "none"
                }}
              >
                <IconArrowLeft style={{ width: 14, height: 14 }} />
                {topico.voltarPara.label}
              </Link>
            )}
            <h1 style={{ marginTop: 6 }}>{topico.titulo}</h1>
            <p>{topico.resumo}</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Conversar
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <section className="page-section">
          {topico.badge && (
            <span className={`tile-badge ${topico.badgeColor === "rose" ? "rose" : ""}`}>
              {topico.badge}
            </span>
          )}
          <h2 className="page-title" style={{ marginTop: 8 }}>Sobre este tema</h2>
          <p style={{ marginTop: 8, fontSize: 16, lineHeight: 1.65, color: "var(--texto)" }}>
            {topico.intro}
          </p>
        </section>

        {topico.secoes.map((sec) => (
          <section key={sec.titulo} className="page-section">
            <h2 className="page-title">{sec.titulo}</h2>
            <ul style={{ marginTop: 14, paddingLeft: 20, lineHeight: 1.75, color: "var(--texto)" }}>
              {sec.itens.map((item, i) => (
                <li key={i} style={{ marginBottom: 8 }}>{item}</li>
              ))}
            </ul>
          </section>
        ))}

        {topico.dicaSophia && (
          <section
            className="page-section"
            style={{
              background: "linear-gradient(135deg, #fde0ea 0%, #fff 100%)",
              border: "1px solid var(--rosa)"
            }}
          >
            <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
              <SophiaAvatar size="md" alt="Sophia te dando uma dica carinhosa" />
              <div>
                <h4 style={{ margin: "0 0 6px", color: "var(--rosa-deep)", fontFamily: "var(--serif)", fontSize: 18 }}>
                  Da Sophia pra você
                </h4>
                <p style={{ margin: 0, color: "var(--texto)", lineHeight: 1.6 }}>{topico.dicaSophia}</p>
              </div>
            </div>
          </section>
        )}

        {topico.referencias && topico.referencias.length > 0 && (
          <section className="page-section">
            <h2 className="page-title">Referências</h2>
            <p className="page-subtitle">Conteúdo construído a partir de fontes oficiais e bibliografia confiável.</p>
            <div style={{ marginTop: 18, display: "grid", gap: 12 }}>
              {topico.referencias.map((ref, i) => {
                const fonte = getFonte(ref.fonte);
                return (
                  <article key={i} className="list-row green" style={{ alignItems: "flex-start" }}>
                    <div className="list-icon"><IconHeart /></div>
                    <div className="list-text">
                      <p
                        style={{
                          margin: 0,
                          fontSize: 11,
                          textTransform: "uppercase",
                          letterSpacing: 0.5,
                          color: "var(--verde-forte)",
                          fontWeight: 700
                        }}
                      >
                        {fonte.tipo}
                      </p>
                      <h4 style={{ margin: "4px 0 4px" }}>{fonte.titulo}</h4>
                      <p style={{ margin: 0, fontSize: 13, color: "var(--texto-suave)" }}>
                        {fonte.autoria} · {fonte.ano}
                      </p>
                      {ref.trecho && (
                        <p style={{ margin: "8px 0 0", fontSize: 14, color: "var(--texto)", fontStyle: "italic" }}>
                          “{ref.trecho}”
                        </p>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
            <p style={{ marginTop: 14, fontSize: 13, color: "var(--texto-suave)" }}>
              Veja a{" "}
              <Link href="/referencias" style={{ color: "var(--rosa-forte)", fontWeight: 600 }}>
                bibliografia completa
              </Link>{" "}
              que sustenta esta plataforma.
            </p>
          </section>
        )}

        {topico.relacionados && topico.relacionados.length > 0 && (
          <section>
            <h3 className="section-title">Continue explorando</h3>
            <div className="tile-grid cols-3">
              {topico.relacionados.map((r) => (
                <Link key={r.slug} href={`/conteudo/${r.slug}`} className="tile">
                  <div className="tile-icon"><IconHeart /></div>
                  <h4 className="tile-title">{r.label}</h4>
                </Link>
              ))}
            </div>
          </section>
        )}

        <div className="reminder-card" style={{ marginTop: 20 }}>
          <div>
            <h4>Quer conversar sobre isso?</h4>
            <p>A Sophia está aqui pra escutar e te apoiar como você precisar.</p>
          </div>
          <Link href="/conversar" className="btn-secondary">
            Falar com a Sophia
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </div>
      </main>
    </div>
  );
}
