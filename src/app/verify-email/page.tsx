import Link from "next/link";
import { prisma } from "@/lib/prisma";

type Props = { searchParams: Promise<{ token?: string }> };

export default async function VerifyEmailPage({ searchParams }: Props) {
  const { token } = await searchParams;

  if (!token) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center p-4">
        <div className="card w-full">
          <p>Token ausente.</p>
        </div>
      </main>
    );
  }

  const verifyToken = await prisma.verifyToken.findUnique({ where: { token } });
  if (!verifyToken || verifyToken.expiresAt < new Date()) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center p-4">
        <div className="card w-full space-y-2">
          <p>Token invalido ou expirado.</p>
          <Link href="/login" className="underline">
            Ir para login
          </Link>
        </div>
      </main>
    );
  }

  await prisma.user.update({
    where: { id: verifyToken.userId },
    data: { emailVerified: true }
  });
  await prisma.verifyToken.delete({ where: { id: verifyToken.id } });

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center p-4">
      <div className="card w-full space-y-2">
        <p>E-mail confirmado com sucesso. Seja bem-vinda!</p>
        <Link href="/login" className="underline">
          Entrar na plataforma
        </Link>
      </div>
    </main>
  );
}
