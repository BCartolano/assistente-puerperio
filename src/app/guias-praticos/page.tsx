import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconBath,
  IconBottle,
  IconUmbilical,
  IconBaby,
  IconShoppingBag,
  IconClipboard,
  IconWindBreath,
  IconNotebook,
  IconChat
} from "@/components/Icons";

const guias = [
  { Icon: IconBath, title: "Banho do recém-nascido", desc: "Passo a passo seguro para o primeiro banho.", href: "/conteudo/banho-do-bebe" },
  { Icon: IconBottle, title: "Pega da amamentação", desc: "Como identificar a pega correta.", href: "/conteudo/amamentacao" },
  { Icon: IconUmbilical, title: "Limpeza do coto umbilical", desc: "Cuidados diários até a queda.", href: "/conteudo/coto-umbilical" },
  { Icon: IconBaby, title: "Cuidados com o bebê", desc: "Tudo que você precisa saber, com calma.", href: "/cuidados-bebe" },
  { Icon: IconShoppingBag, title: "Mala da maternidade", desc: "Lista do que levar para o parto.", href: "/conteudo/mala-da-maternidade" },
  { Icon: IconClipboard, title: "Plano de parto", desc: "Modelo simples para conversar com sua equipe.", href: "/conteudo/plano-de-parto" },
  { Icon: IconWindBreath, title: "Respiração de 5 min", desc: "Para usar quando a ansiedade bate.", href: "/conteudo/respiracao" },
  { Icon: IconNotebook, title: "Diário de sentimentos", desc: "Registre como você está se sentindo.", href: "/conteudo/diario-sentimentos" }
];

export default async function GuiasPraticosPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Guias Práticos</h1>
            <p>Conteúdos passo a passo para usar no dia a dia.</p>
          </div>
          <Link href="/conversar" className="btn-secondary">
            <IconChat style={{ width: 16, height: 16 }} />
            Pedir ajuda à Sophia
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <h3 className="section-title">Mão na massa</h3>
        <p className="section-subtitle">Cada guia leva direto para o assunto.</p>
        <div className="tile-grid cols-3">
          {guias.map((g) => (
            <Link key={g.title} href={g.href} className="tile">
              <div className="tile-icon"><g.Icon /></div>
              <h4 className="tile-title">{g.title}</h4>
              <p className="tile-desc">{g.desc}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
