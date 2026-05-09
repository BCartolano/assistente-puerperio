import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { ConfiguracoesPanel } from "@/components/ConfiguracoesPanel";
import { IconUser, IconArrowRight } from "@/components/Icons";

export default async function ConfiguracoesPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Configurações</h1>
            <p>Ajuste a Sophia do seu jeitinho.</p>
          </div>
          <Link href="/meu-perfil" className="btn-ghost">
            <IconUser style={{ width: 14, height: 14 }} />
            Ver meu perfil
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </header>

        <ConfiguracoesPanel name={session.name} email={session.email} />
      </main>
    </div>
  );
}
