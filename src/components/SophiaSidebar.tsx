"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType, SVGProps } from "react";
import { LogoutButton } from "@/components/profile/LogoutButton";
import { SophiaAvatar } from "@/components/SophiaAvatar";
import {
  IconHome,
  IconChat,
  IconBook,
  IconHeart,
  IconBottle,
  IconCalendar,
  IconStar,
  IconLibrary,
  IconScale,
  IconSettings,
  IconShield,
  IconDocument,
  IconCheckList,
  IconTrash
} from "@/components/Icons";

type IconCmp = ComponentType<SVGProps<SVGSVGElement>>;

type NavItem = {
  href: string;
  label: string;
  Icon: IconCmp;
};

type Section = {
  label?: string;
  items: NavItem[];
};

const sections: Section[] = [
  {
    items: [
      { href: "/inicio", label: "Início", Icon: IconHome },
      { href: "/conversar", label: "Conversar com Sophia", Icon: IconChat },
      { href: "/dicas", label: "Dicas e Conteúdos", Icon: IconBook },
      { href: "/saude-emocional", label: "Saúde Emocional", Icon: IconHeart },
      { href: "/cuidados-bebe", label: "Cuidados com o Bebê", Icon: IconBottle },
      { href: "/minha-jornada", label: "Minha Jornada", Icon: IconCalendar },
      { href: "/favoritos", label: "Favoritos", Icon: IconStar }
    ]
  },
  {
    label: "Transparência",
    items: [
      { href: "/referencias", label: "Referências", Icon: IconLibrary },
      { href: "/aviso-legal", label: "Aviso Legal", Icon: IconScale }
    ]
  },
  {
    label: "Seus dados e privacidade",
    items: [
      { href: "/privacidade", label: "Política de Privacidade", Icon: IconShield },
      { href: "/termos", label: "Termos de Uso", Icon: IconDocument },
      { href: "/consentimento", label: "Gerenciar Consentimento", Icon: IconCheckList },
      { href: "/excluir-meus-dados", label: "Excluir Meus Dados", Icon: IconTrash }
    ]
  },
  {
    label: "Conta",
    items: [
      { href: "/configuracoes", label: "Configurações", Icon: IconSettings }
    ]
  }
];

export function SophiaSidebar() {
  const pathname = usePathname();

  return (
    <aside className="sophia-sidebar">
      <div className="sophia-brand">
        <SophiaAvatar size="lg" className="sophia-brand-logo" ring={false} />
        <h2>Sophia</h2>
        <p>Sua companheira no puerpério</p>
      </div>

      <nav className="sophia-nav" aria-label="Navegação principal">
        {sections.map((section, i) => (
          <div key={i}>
            {section.label && <div className="nav-section-label">{section.label}</div>}
            {section.items.map((item) => {
              const isActive =
                pathname === item.href || pathname?.startsWith(item.href + "/");
              const Icon = item.Icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={isActive ? "active" : ""}
                >
                  <Icon className="nav-icon" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sophia-logout">
        <LogoutButton />
      </div>
    </aside>
  );
}
