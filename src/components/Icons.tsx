/**
 * Sophia · Biblioteca de ícones em linha (line icons).
 *
 * Todos foram desenhados para combinar com o design aconchegante:
 * traços finos (1.6px), curvas suaves, sem preenchimento agressivo.
 * Substitui o uso de emojis na UI por elementos visuais consistentes.
 */

import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const baseProps = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  width: 22,
  height: 22,
  "aria-hidden": true
};

export function IconHome(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M3.5 11l8.5-7 8.5 7" />
      <path d="M5.5 9.5V20h13V9.5" />
      <path d="M10 20v-5h4v5" />
    </svg>
  );
}

export function IconChat(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 5h14a2 2 0 012 2v8a2 2 0 01-2 2h-7l-4 3v-3H5a2 2 0 01-2-2V7a2 2 0 012-2z" />
      <path d="M8.5 11h.01M12 11h.01M15.5 11h.01" />
    </svg>
  );
}

export function IconBook(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M4 5.5A2.5 2.5 0 016.5 3H20v14H6.5A2.5 2.5 0 004 19.5V5.5z" />
      <path d="M4 19.5a2.5 2.5 0 012.5-2.5H20v4H6.5A2.5 2.5 0 014 18.5z" />
    </svg>
  );
}

export function IconHeart(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 20s-7-4.4-9-8.5C1 7.6 3.5 4 7 4c2 0 3.5 1 5 3 1.5-2 3-3 5-3 3.5 0 6 3.6 4 7.5C19 15.6 12 20 12 20z" />
    </svg>
  );
}

export function IconHeartFilled(props: IconProps) {
  return (
    <svg {...baseProps} fill="currentColor" stroke="none" {...props}>
      <path d="M12 20s-7-4.4-9-8.5C1 7.6 3.5 4 7 4c2 0 3.5 1 5 3 1.5-2 3-3 5-3 3.5 0 6 3.6 4 7.5C19 15.6 12 20 12 20z" />
    </svg>
  );
}

export function IconMother(props: IconProps) {
  // Silhueta de mãe com bebê — linhas suaves
  return (
    <svg {...baseProps} {...props}>
      <circle cx="9.5" cy="6.5" r="2.5" />
      <path d="M5 21v-4a4.5 4.5 0 014.5-4.5h2A4.5 4.5 0 0116 17v4" />
      <circle cx="15.5" cy="11.5" r="1.6" />
      <path d="M14 17v-2.5a1.5 1.5 0 013 0V17" />
    </svg>
  );
}

export function IconBaby(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="9" r="4.5" />
      <path d="M9.5 9.5h.01M14.5 9.5h.01" />
      <path d="M10.5 11.5c.6.6 2.4.6 3 0" />
      <path d="M5.5 21c.5-3 3-5 6.5-5s6 2 6.5 5" />
    </svg>
  );
}

export function IconBottle(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M9 3h6" />
      <path d="M9.5 3.5v3l-1 1.5a3 3 0 00-.5 1.7V19a2 2 0 002 2h4a2 2 0 002-2V9.7a3 3 0 00-.5-1.7l-1-1.5v-3" />
      <path d="M8 12h8" />
    </svg>
  );
}

export function IconBrain(props: IconProps) {
  // Coração-cérebro: usado para "saúde emocional"
  return (
    <svg {...baseProps} {...props}>
      <path d="M9.5 4.5A3 3 0 006.5 7v0A3 3 0 005 10v0a3 3 0 001 6h0a3 3 0 003 3 3 3 0 003-3v-15A2.5 2.5 0 009.5 4.5z" />
      <path d="M14.5 4.5A3 3 0 0117.5 7v0A3 3 0 0119 10v0a3 3 0 01-1 6h0a3 3 0 01-3 3 3 3 0 01-3-3" />
    </svg>
  );
}

export function IconCalendar(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <rect x="3.5" y="5" width="17" height="15" rx="2" />
      <path d="M3.5 9.5h17M8 3v4M16 3v4" />
      <circle cx="8" cy="14" r="0.8" fill="currentColor" />
      <circle cx="12" cy="14" r="0.8" fill="currentColor" />
      <circle cx="16" cy="14" r="0.8" fill="currentColor" />
    </svg>
  );
}

export function IconStar(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 17l-5.2 2.7 1-5.9L3.5 9.7l5.9-.8L12 3.5z" />
    </svg>
  );
}

export function IconStarFilled(props: IconProps) {
  return (
    <svg {...baseProps} fill="currentColor" stroke="none" {...props}>
      <path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 17l-5.2 2.7 1-5.9L3.5 9.7l5.9-.8L12 3.5z" />
    </svg>
  );
}

export function IconBookmark(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M6 4h12v17l-6-4-6 4V4z" />
    </svg>
  );
}

export function IconLibrary(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M4 5v14M8 5v14M14 4l-2 16M19 6l3 13" />
    </svg>
  );
}

export function IconScale(props: IconProps) {
  // Balança / aviso legal
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 4v16M5 8h14" />
      <path d="M5 8l-2 6c1 1 3 1 4 0l-2-6zM19 8l-2 6c1 1 3 1 4 0l-2-6z" />
    </svg>
  );
}

export function IconShield(props: IconProps) {
  // Privacidade
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}

export function IconDocument(props: IconProps) {
  // Termos / documento
  return (
    <svg {...baseProps} {...props}>
      <path d="M6 3h9l4 4v14a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z" />
      <path d="M14 3v5h5" />
      <path d="M8 13h8M8 17h6" />
    </svg>
  );
}

export function IconTrash(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M4 6.5h16M9 6.5V4a1 1 0 011-1h4a1 1 0 011 1v2.5" />
      <path d="M5.5 6.5l1 13a1 1 0 001 1h9a1 1 0 001-1l1-13" />
      <path d="M10 11v6M14 11v6" />
    </svg>
  );
}

export function IconKeyRound(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="9" cy="14" r="4" />
      <path d="M12 13l8-8M17 8l3 3M14 11l3 3" />
    </svg>
  );
}

export function IconSettings(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1 1 0 00.2 1.1l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1 1 0 00-1.1-.2 1 1 0 00-.6 1V20a2 2 0 11-4 0v-.1a1 1 0 00-.6-1 1 1 0 00-1.1.2l-.1.1A2 2 0 114.5 16.4l.1-.1a1 1 0 00.2-1.1 1 1 0 00-1-.6H3.6a2 2 0 110-4h.1a1 1 0 00.9-.6 1 1 0 00-.2-1.1l-.1-.1A2 2 0 117.6 4.5l.1.1a1 1 0 001.1.2H9a1 1 0 00.6-1V3.6a2 2 0 114 0v.1a1 1 0 00.6 1 1 1 0 001.1-.2l.1-.1a2 2 0 112.8 2.8l-.1.1a1 1 0 00-.2 1.1V9a1 1 0 001 .6h.1a2 2 0 110 4H20a1 1 0 00-.6 1z" />
    </svg>
  );
}

export function IconLogout(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M9 4H5a1 1 0 00-1 1v14a1 1 0 001 1h4" />
      <path d="M16 8l4 4-4 4" />
      <path d="M20 12H10" />
    </svg>
  );
}

export function IconBell(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M6 9a6 6 0 0112 0c0 5 2 6 2 7H4c0-1 2-2 2-7z" />
      <path d="M10 19a2 2 0 004 0" />
    </svg>
  );
}

export function IconArrowRight(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function IconArrowLeft(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M19 12H5M11 6l-6 6 6 6" />
    </svg>
  );
}

export function IconLeaf(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 19c0-7 5-13 14-13 0 9-6 14-13 14-1-2-1-3-1-1z" />
      <path d="M5 19s4-4 9-7" />
    </svg>
  );
}

export function IconFlower(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="2.2" />
      <path d="M12 9.8V5a3 3 0 010-2 3 3 0 010 2v4.8M12 14.2V19a3 3 0 010 2 3 3 0 010-2v-4.8" />
      <path d="M9.8 12H5a3 3 0 01-2 0 3 3 0 012 0h4.8M14.2 12H19a3 3 0 012 0 3 3 0 01-2 0h-4.8" />
    </svg>
  );
}

export function IconSparkle(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 4l1.6 4.4L18 10l-4.4 1.6L12 16l-1.6-4.4L6 10l4.4-1.6L12 4z" />
      <path d="M19 16l.7 1.8L21.5 18.5l-1.8.7L19 21l-.7-1.8L16.5 18.5l1.8-.7L19 16z" />
    </svg>
  );
}

export function IconMoon(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M19 14a8 8 0 01-9-9 8 8 0 109 9z" />
    </svg>
  );
}

export function IconCloudRain(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M7 16h11a4 4 0 000-8 6 6 0 00-11 1.5A4 4 0 007 16z" />
      <path d="M9 19l-1 2M13 19l-1 2M17 19l-1 2" />
    </svg>
  );
}

export function IconSun(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="3.5" />
      <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M18.4 5.6L17 7M7 17l-1.4 1.4" />
    </svg>
  );
}

export function IconCheckCircle(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12.5l3 3 5-6" />
    </svg>
  );
}

export function IconAlertCircle(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5M12 16h.01" />
    </svg>
  );
}

export function IconInfo(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5" />
      <circle cx="12" cy="8" r="0.8" fill="currentColor" />
    </svg>
  );
}

export function IconHands(props: IconProps) {
  // Mãos acolhendo
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 13.5V9a2 2 0 014 0v3" />
      <path d="M9 12V7a2 2 0 014 0v5" />
      <path d="M13 12V8a2 2 0 014 0v6c0 3.5-2 6-5 6h-2c-2.5 0-4-1.5-5-3.5L4 12.5a1.5 1.5 0 012.5-1.7l1.5 1.7" />
    </svg>
  );
}

export function IconMail(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="M4 7l8 6 8-6" />
    </svg>
  );
}

export function IconLock(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <rect x="4.5" y="10" width="15" height="10" rx="2.5" />
      <path d="M8 10V7a4 4 0 018 0v3" />
      <circle cx="12" cy="15" r="1.4" fill="currentColor" />
    </svg>
  );
}

export function IconPaperPlane(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M3 11l18-7-7 18-2-8-9-3z" />
    </svg>
  );
}

export function IconBath(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M3 11h18" />
      <path d="M5 11v6a3 3 0 003 3h8a3 3 0 003-3v-6" />
      <path d="M7 11V7a3 3 0 016 0v4" />
      <circle cx="13" cy="6.5" r="1.2" />
    </svg>
  );
}

export function IconUmbilical(props: IconProps) {
  // Gota
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 3.5C9 8 6.5 11.5 6.5 14.5a5.5 5.5 0 0011 0c0-3-2.5-6.5-5.5-11z" />
    </svg>
  );
}

export function IconStethoscope(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 4v6a4 4 0 008 0V4" />
      <path d="M9 14v3a4 4 0 008 0v-2" />
      <circle cx="17" cy="11.5" r="1.5" />
    </svg>
  );
}

export function IconSyringe(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M14 4l6 6" />
      <path d="M17 7l-9 9-3-1-1-3 9-9" />
      <path d="M3 21l4-4M7 13l1.5 1.5M11 9l1.5 1.5" />
    </svg>
  );
}

export function IconPalm(props: IconProps) {
  // Folha de palmeira / planta — usado para autocuidado, calma
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 21V11" />
      <path d="M12 11c-2-3-5-3-7 0M12 11c2-3 5-3 7 0M12 11c-1-3-3-4-5-3M12 11c1-3 3-4 5-3" />
    </svg>
  );
}

export function IconSeed(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 21V13" />
      <path d="M12 13C9 9 11 4 17 4c0 6-5 8-5 9z" />
      <path d="M12 13C15 11 13 7 7 8c1 6 5 5 5 5z" />
    </svg>
  );
}

export function IconRose(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 21V13" />
      <circle cx="12" cy="9" r="4" />
      <path d="M10 9c0-1.5 1-2.5 2-2.5s2 1 2 2.5-1 2-2 2-2-.5-2-2z" />
    </svg>
  );
}

export function IconSmile(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8.5 14c1 1.3 2.2 2 3.5 2s2.5-.7 3.5-2" />
      <circle cx="9" cy="10" r="0.9" fill="currentColor" />
      <circle cx="15" cy="10" r="0.9" fill="currentColor" />
    </svg>
  );
}

export function IconTired(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8.5 15c1-.6 2.2-.9 3.5-.9s2.5.3 3.5.9" />
      <path d="M7.5 9.5l2 1M14.5 10.5l2-1" />
    </svg>
  );
}

export function IconWaves(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M3 8c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 2 2" />
      <path d="M3 13c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 2 2" />
      <path d="M3 18c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 2 2" />
    </svg>
  );
}

export function IconWindBreath(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M4 8h12a3 3 0 100-6" />
      <path d="M4 14h16a3 3 0 010 6" />
      <path d="M4 20h6" />
    </svg>
  );
}

export function IconNotebook(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 4h13a1 1 0 011 1v15a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z" />
      <path d="M9 4v17M12 9h4M12 13h4" />
    </svg>
  );
}

export function IconCheckList(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M4 7l2 2 3-3M4 13l2 2 3-3M4 19l2 2 3-3" />
      <path d="M13 8h7M13 14h7M13 20h7" />
    </svg>
  );
}

export function IconUsers(props: IconProps) {
  // Rede de apoio
  return (
    <svg {...baseProps} {...props}>
      <circle cx="9" cy="8" r="3" />
      <circle cx="17" cy="9" r="2.4" />
      <path d="M3 19c0-3 2.7-5 6-5s6 2 6 5" />
      <path d="M14 19c.5-2 1.7-3 4-3s3.5 1 4 3" />
    </svg>
  );
}

export function IconUser(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 3.5-7 8-7s8 3 8 7" />
    </svg>
  );
}

export function IconClipboard(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M9 4h6v3H9z" />
      <path d="M6 6h3v1h6V6h3a1 1 0 011 1v13a1 1 0 01-1 1H6a1 1 0 01-1-1V7a1 1 0 011-1z" />
    </svg>
  );
}

export function IconHospital(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M4 21V8l8-4 8 4v13" />
      <path d="M4 21h16" />
      <path d="M12 9v6M9 12h6" />
    </svg>
  );
}

export function IconBabyCarriage(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M3 11h12V6a5 5 0 00-10 0" />
      <path d="M3 11h17l-2 5h-9l-3-5" />
      <circle cx="8" cy="19" r="2" />
      <circle cx="16" cy="19" r="2" />
    </svg>
  );
}

export function IconShoppingBag(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 7h14l-1 13a1 1 0 01-1 1H7a1 1 0 01-1-1L5 7z" />
      <path d="M9 7V5a3 3 0 016 0v2" />
    </svg>
  );
}

export function IconWarmDrink(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M5 9h12v8a4 4 0 01-4 4H9a4 4 0 01-4-4V9z" />
      <path d="M17 11h2a3 3 0 010 6h-2" />
      <path d="M8 6c-.5-1 .5-2 0-3M11 6c-.5-1 .5-2 0-3M14 6c-.5-1 .5-2 0-3" />
    </svg>
  );
}

export function IconHeartHands(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 16s-5-3-5-7a3 3 0 015-2 3 3 0 015 2c0 4-5 7-5 7z" />
      <path d="M5 18l3 3M19 18l-3 3" />
    </svg>
  );
}

export function IconCalendarHeart(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <rect x="3.5" y="5" width="17" height="15" rx="2" />
      <path d="M3.5 9.5h17M8 3v4M16 3v4" />
      <path d="M12 17s-2.5-1.5-2.5-3.5A1.5 1.5 0 0112 12.5a1.5 1.5 0 012.5 1A3 3 0 0112 17z" />
    </svg>
  );
}

export function IconPlus(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

export function IconEyeOpen(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export function IconEyeClosed(props: IconProps) {
  return (
    <svg {...baseProps} {...props}>
      <path d="M3 3l18 18" />
      <path d="M10.6 6.1A10.5 10.5 0 0112 6c6.5 0 10 7 10 7a17.4 17.4 0 01-3.1 4M6.6 6.6C3.7 8.5 2 12 2 12s3.5 7 10 7c1.7 0 3.2-.4 4.5-1" />
    </svg>
  );
}
