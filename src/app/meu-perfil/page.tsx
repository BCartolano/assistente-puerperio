import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import {
  IconUser,
  IconMail,
  IconLock,
  IconCalendar,
  IconStarFilled,
  IconSettings,
  IconArrowRight
} from "@/components/Icons";

export default async function MeuPerfilPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Meu Perfil</h1>
            <p>Suas informações e atalhos pessoais.</p>
          </div>
          <Link href="/configuracoes" className="btn-ghost">
            <IconSettings style={{ width: 14, height: 14 }} />
            Configurações
          </Link>
        </header>

        <section className="page-section">
          <h2 className="page-title">Informações</h2>

          <div className="list-stack" style={{ marginTop: 18 }}>
            <article className="list-row">
              <div className="list-icon"><IconUser /></div>
              <div className="list-text">
                <h4>Nome</h4>
                <p>{session.name}</p>
              </div>
            </article>
            <article className="list-row green">
              <div className="list-icon"><IconMail /></div>
              <div className="list-text">
                <h4>E-mail</h4>
                <p>{session.email}</p>
              </div>
            </article>
            <article className="list-row">
              <div className="list-icon"><IconLock /></div>
              <div className="list-text">
                <h4>Segurança</h4>
                <p>Mantenha sua senha forte e atualizada.</p>
              </div>
              <Link href="/mudar-senha" className="list-action">
                Mudar senha <IconArrowRight style={{ width: 14, height: 14, display: "inline", verticalAlign: "middle" }} />
              </Link>
            </article>
          </div>
        </section>

        <section className="page-section">
          <h2 className="page-title">Atalhos pessoais</h2>
          <div className="tile-grid cols-3" style={{ marginTop: 18 }}>
            <Link href="/minha-jornada" className="tile">
              <div className="tile-icon"><IconCalendar /></div>
              <h4 className="tile-title">Minha Jornada</h4>
              <p className="tile-desc">Acompanhe seus marcos.</p>
            </Link>
            <Link href="/favoritos" className="tile">
              <div className="tile-icon green"><IconStarFilled /></div>
              <h4 className="tile-title">Favoritos</h4>
              <p className="tile-desc">O que você salvou.</p>
            </Link>
            <Link href="/configuracoes" className="tile">
              <div className="tile-icon"><IconSettings /></div>
              <h4 className="tile-title">Configurações</h4>
              <p className="tile-desc">Notificações e preferências.</p>
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
