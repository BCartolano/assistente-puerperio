import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentSession } from "@/lib/auth";
import { SophiaSidebar } from "@/components/SophiaSidebar";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import { DisclaimerMedico } from "@/components/DisclaimerMedico";
import {
  IconBottle,
  IconMoon,
  IconBath,
  IconUmbilical,
  IconBaby,
  IconSyringe,
  IconShoppingBag,
  IconStethoscope,
  IconChat,
  IconArrowRight
} from "@/components/Icons";

const guias = [
  { Icon: IconBottle, title: "Amamentação", desc: "Pega, livre demanda e ordenha.", href: "/conteudo/amamentacao" },
  { Icon: IconMoon, title: "Sono seguro", desc: "Posições, ambiente e ABC do sono.", href: "/conteudo/sono-do-bebe" },
  { Icon: IconBath, title: "Banho do bebê", desc: "Temperatura, segurança e rotina.", href: "/conteudo/banho-do-bebe" },
  { Icon: IconUmbilical, title: "Coto umbilical", desc: "Limpeza, sinais de alerta e cuidados diários.", href: "/conteudo/coto-umbilical" },
  { Icon: IconBaby, title: "Cólicas", desc: "Massagens, posições e quando se preocupar.", href: "/conteudo/colicas" },
  { Icon: IconSyringe, title: "Vacinas", desc: "Calendário do bebê nos primeiros meses.", href: "/conteudo/vacinas" },
  { Icon: IconShoppingBag, title: "Estímulos seguros", desc: "Brincadeiras simples por idade.", href: "/conteudo/estimulos-seguros" },
  { Icon: IconStethoscope, title: "Sinais de alerta", desc: "Febre, alimentação e quando ir ao pediatra.", href: "/conteudo/sinais-alerta" }
];

export default async function CuidadosBebePage() {
  const session = await getCurrentSession();
  if (!session) redirect("/login");

  return (
    <div className="app-shell no-aside">
      <SophiaSidebar />
      <main className="app-main">
        <header className="app-main-header">
          <div>
            <h1>Cuidados com o Bebê</h1>
            <p>Tudo sobre seu bebê, com passos simples e linguagem acolhedora.</p>
          </div>
          <Link href="/conversar" className="btn-primary">
            <IconChat style={{ width: 16, height: 16 }} />
            Tirar dúvida agora
          </Link>
        </header>

        <DisclaimerMedico variant="compact" />

        <section className="hero-conversa" style={{ marginBottom: 18 }}>
          <div className="hero-conversa-image">
            <SophiaAvatar size="xl" ring={false} />
          </div>
          <div className="hero-conversa-content">
            <h2>Cada bebê tem seu ritmo</h2>
            <p>
              Comparar cansa. Use os guias como apoio, e confie no seu olhar
              de mãe. Quando algo te preocupar, eu fico aqui.
            </p>
            <Link href="/conversar" className="btn-primary">
              Conversar com a Sophia
              <IconArrowRight style={{ width: 16, height: 16 }} />
            </Link>
          </div>
        </section>

        <h3 className="section-title">Guias rápidos</h3>
        <p className="section-subtitle">Vá direto ao tema que está te preocupando hoje.</p>
        <div className="tile-grid cols-3">
          {guias.map((g) => (
            <Link key={g.title} href={g.href} className="tile">
              <div className="tile-icon">
                <g.Icon />
              </div>
              <h4 className="tile-title">{g.title}</h4>
              <p className="tile-desc">{g.desc}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
