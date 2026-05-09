import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import { getAllFontes } from "@/lib/referencias";
import { topicos } from "@/lib/topicos";
import { IconLibrary, IconChat, IconHeart, IconArrowRight } from "@/components/Icons";

export default async function ReferenciasPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  const fontes = getAllFontes();

  const topicosPorFonte: Record<string, { slug: string; titulo: string }[]> = {};
  for (const topico of Object.values(topicos)) {
    if (!topico.referencias) continue;
    for (const ref of topico.referencias) {
      if (!topicosPorFonte[ref.fonte]) topicosPorFonte[ref.fonte] = [];
      const list = topicosPorFonte[ref.fonte];
      if (!list.find((t) => t.slug === topico.slug)) {
        list.push({ slug: topico.slug, titulo: topico.titulo });
      }
    }
  }

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Referências</h1>
            <p>Bases oficiais e bibliografia que sustentam todo o conteúdo da Sophia.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Conversar com Sophia
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <section className="page-section">
          <h2 className="page-title">Por que isso importa?</h2>
          <p style={{ marginTop: 8, fontSize: 16, lineHeight: 1.65, color: "var(--texto)" }}>
            A Sophia foi construída sobre fontes confiáveis: cadernetas
            oficiais do Ministério da Saúde, manuais técnicos do SUS e
            bibliografia reconhecida sobre puerpério. Aqui você consulta
            quais documentos embasam cada tema, com transparência total.
          </p>
        </section>

        <section className="page-section">
          <h2 className="page-title">Bibliografia</h2>
          <p className="page-subtitle">
            Quatro pilares de cuidado integral durante a gestação, parto e puerpério.
          </p>

          <div style={{ marginTop: 22, display: "grid", gap: 18 }}>
            {fontes.map((fonte) => {
              const topicosCitados = topicosPorFonte[fonte.id] ?? [];
              return (
                <article
                  key={fonte.id}
                  className="page-section"
                  style={{ background: "#fff", padding: 22 }}
                >
                  <div style={{ display: "flex", gap: 18, alignItems: "flex-start" }}>
                    <div
                      style={{
                        width: 56,
                        height: 56,
                        borderRadius: 16,
                        background: "var(--rosa-creme)",
                        color: "var(--rosa-forte)",
                        display: "grid",
                        placeItems: "center",
                        flexShrink: 0
                      }}
                    >
                      <IconLibrary style={{ width: 26, height: 26 }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <p
                        style={{
                          margin: 0,
                          fontSize: 11,
                          textTransform: "uppercase",
                          letterSpacing: 0.6,
                          color: "var(--verde-forte)",
                          fontWeight: 700
                        }}
                      >
                        {fonte.tipo}
                      </p>
                      <h3 style={{ margin: "4px 0 6px", color: "var(--texto)" }}>
                        {fonte.titulo}
                      </h3>
                      <p style={{ margin: 0, fontSize: 14, color: "var(--texto-suave)" }}>
                        {fonte.autoria} · {fonte.ano}
                      </p>
                      <p style={{ margin: "12px 0 0", color: "var(--texto)", lineHeight: 1.65 }}>
                        {fonte.descricao}
                      </p>

                      {topicosCitados.length > 0 && (
                        <div style={{ marginTop: 16 }}>
                          <p
                            style={{
                              margin: "0 0 8px",
                              fontSize: 11,
                              fontWeight: 700,
                              color: "var(--rosa-forte)",
                              textTransform: "uppercase",
                              letterSpacing: 0.6
                            }}
                          >
                            Tópicos baseados nesta fonte ({topicosCitados.length})
                          </p>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                            {topicosCitados.map((t) => (
                              <Link
                                key={t.slug}
                                href={`/conteudo/${t.slug}`}
                                style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: 6,
                                  padding: "6px 12px",
                                  borderRadius: 999,
                                  background: "var(--rosa-creme)",
                                  border: "1px solid var(--borda)",
                                  fontSize: 13,
                                  color: "var(--texto)",
                                  textDecoration: "none"
                                }}
                              >
                                <IconHeart style={{ width: 12, height: 12, color: "var(--rosa-forte)" }} />
                                {t.titulo}
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">Como usamos essas fontes</h2>
          <ul style={{ marginTop: 14, paddingLeft: 20, lineHeight: 1.8, color: "var(--texto)" }}>
            <li>Cada tópico cita explicitamente quais fontes embasam o conteúdo, com trechos representativos.</li>
            <li>A Sophia (chat) usa esses materiais como base de conhecimento para te direcionar.</li>
            <li>
              Isso <strong>não substitui acompanhamento profissional</strong>. Sempre que possível,
              procure sua equipe de saúde — UBS mais próxima, obstetra, pediatra e psicóloga
              perinatal.
            </li>
          </ul>
        </section>

        <div className="reminder-card">
          <div>
            <h4>Tem dúvida sobre algum assunto?</h4>
            <p>Conta pra Sophia. Ela vai te direcionar para o conteúdo mais próximo do que você precisa.</p>
          </div>
          <Link href="/conversar" className="btn-secondary">
            Falar com Sophia
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </div>
      </main>
    </div>
  );
}
