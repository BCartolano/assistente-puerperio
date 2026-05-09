import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconClipboard,
  IconHospital,
  IconScale,
  IconShoppingBag,
  IconWindBreath,
  IconHands,
  IconChat,
  IconArrowRight
} from "@/components/Icons";

const topicos = [
  { Icon: IconClipboard, title: "Plano de parto", desc: "Documento que comunica suas escolhas para a equipe.", href: "/conteudo/plano-de-parto" },
  { Icon: IconHospital, title: "Tipos de parto", desc: "Normal, cesárea, humanizado: prós e cuidados de cada um.", href: "/conteudo/tipos-de-parto" },
  { Icon: IconScale, title: "Seus direitos", desc: "Acompanhante, alojamento conjunto e informação clara.", href: "/conteudo/direitos-da-gestante" },
  { Icon: IconShoppingBag, title: "Mala da maternidade", desc: "Checklist do que levar para você e para o bebê.", href: "/conteudo/mala-da-maternidade" },
  { Icon: IconWindBreath, title: "Respiração no trabalho de parto", desc: "Técnicas para ajudar nas contrações.", href: "/conteudo/respiracao-trabalho-parto" },
  { Icon: IconHands, title: "Acompanhante e doula", desc: "Quem pode estar com você e como se preparar.", href: "/conteudo/acompanhante-doula" }
];

export default async function PartoPage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Parto</h1>
            <p>Informação para você decidir com tranquilidade e segurança.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Tirar dúvidas com Sophia
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <h3 className="section-title">Tudo sobre o grande dia</h3>
        <p className="section-subtitle">Materiais práticos, sem julgamentos.</p>
        <div className="tile-grid cols-3">
          {topicos.map((t) => (
            <Link key={t.title} href={t.href} className="tile">
              <div className="tile-icon"><t.Icon /></div>
              <h4 className="tile-title">{t.title}</h4>
              <p className="tile-desc">{t.desc}</p>
            </Link>
          ))}
        </div>

        <div className="reminder-card" style={{ marginTop: 20 }}>
          <div>
            <h4>Próxima fase</h4>
            <p>Depois do parto vem o puerpério. Já dá uma olhada nos cuidados.</p>
          </div>
          <Link href="/pos-parto" className="btn-secondary">
            Ir para pós-parto
            <IconArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </div>
      </main>
    </div>
  );
}
