import { NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";

const schema = z.object({
  token: z.string().min(1),
  mode: z.enum(["email", "reset"])
});

export async function POST(req: Request) {
  const parsed = schema.safeParse(await req.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Dados inválidos." }, { status: 400 });
  }

  if (parsed.data.mode === "email") {
    const verifyToken = await prisma.verifyToken.findUnique({ where: { token: parsed.data.token } });
    if (!verifyToken || verifyToken.expiresAt < new Date()) {
      return NextResponse.json({ error: "Código inválido ou expirado." }, { status: 400 });
    }
    await prisma.user.update({ where: { id: verifyToken.userId }, data: { emailVerified: true } });
    await prisma.verifyToken.delete({ where: { id: verifyToken.id } });
    return NextResponse.json({ message: "E-mail verificado com sucesso." });
  }

  const resetToken = await prisma.passwordResetToken.findUnique({ where: { token: parsed.data.token } });
  if (!resetToken || resetToken.expiresAt < new Date()) {
    return NextResponse.json({ error: "Código inválido ou expirado." }, { status: 400 });
  }
  return NextResponse.json({ message: "Código de reset válido. Você já pode redefinir sua senha." });
}
