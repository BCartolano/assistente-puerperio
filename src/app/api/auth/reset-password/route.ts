import bcrypt from "bcryptjs";
import { NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";

const schema = z.object({
  token: z.string().min(1),
  password: z.string().min(6)
});

export async function POST(req: Request) {
  const parsed = schema.safeParse(await req.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Dados invalidos." }, { status: 400 });
  }

  const resetToken = await prisma.passwordResetToken.findUnique({
    where: { token: parsed.data.token }
  });
  if (!resetToken || resetToken.expiresAt < new Date()) {
    return NextResponse.json({ error: "Token invalido ou expirado." }, { status: 400 });
  }

  const passwordHash = await bcrypt.hash(parsed.data.password, 10);
  await prisma.user.update({
    where: { id: resetToken.userId },
    data: { passwordHash }
  });

  await prisma.passwordResetToken.delete({ where: { id: resetToken.id } });
  return NextResponse.json({ message: "Senha redefinida com sucesso." });
}
