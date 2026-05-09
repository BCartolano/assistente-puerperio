import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { ConsentManager } from "@/components/ConsentManager";

export default async function ConsentimentoPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Gerenciar Consentimento</h1>
            <p>
              Você no controle. Ative ou desative o que faz sentido pra
              você — quando quiser.
            </p>
          </div>
        </header>

        <ConsentManager />
      </main>
    </div>
  );
}
