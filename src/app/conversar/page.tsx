import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { ChatSophia } from "@/components/ChatSophia";

export default async function ConversarPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Conversar com a Sophia</h1>
            <p>Um espaço seguro pra falar do que está pesando — e do que está bonito também.</p>
          </div>
        </header>

        <ChatSophia />
      </main>
    </div>
  );
}
