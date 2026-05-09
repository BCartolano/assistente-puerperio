import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DeleteAccountFlow } from "@/components/DeleteAccountFlow";

export default async function ExcluirMeusDadosPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Excluir meus dados</h1>
            <p>
              Sem perguntas constrangedoras. Se você quiser ir embora, eu
              respeito — e cuido pra que tudo seja apagado com cuidado.
            </p>
          </div>
        </header>

        <DeleteAccountFlow email={session.email} name={session.name} />
      </main>
    </div>
  );
}
