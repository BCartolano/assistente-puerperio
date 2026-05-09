"use client";

import { useRouter } from "next/navigation";
import { IconLogout } from "@/components/Icons";

type Variant = "sidebar" | "ghost";

type Props = {
  variant?: Variant;
};

export function LogoutButton({ variant = "sidebar" }: Props) {
  const router = useRouter();

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/");
    router.refresh();
  }

  if (variant === "ghost") {
    return (
      <button onClick={handleLogout} className="btn-ghost" type="button">
        <IconLogout style={{ width: 16, height: 16 }} />
        Sair
      </button>
    );
  }

  return (
    <button onClick={handleLogout} type="button">
      <IconLogout style={{ width: 16, height: 16 }} />
      Sair
    </button>
  );
}
