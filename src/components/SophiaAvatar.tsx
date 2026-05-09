import Image from "next/image";

type Size = "xs" | "sm" | "md" | "lg" | "xl";

const sizes: Record<Size, number> = {
  xs: 32,
  sm: 44,
  md: 64,
  lg: 96,
  xl: 200
};

type Props = {
  size?: Size;
  alt?: string;
  className?: string;
  ring?: boolean;
};

export function SophiaAvatar({
  size = "md",
  alt = "Ilustração da Sophia abraçando seu bebê",
  className = "",
  ring = true
}: Props) {
  const px = sizes[size];
  return (
    <div
      className={className}
      style={{
        width: px,
        height: px,
        borderRadius: "50%",
        background: "#fff",
        border: ring ? "3px solid #fff" : "none",
        boxShadow: ring ? "0 8px 22px -10px rgba(208, 140, 165, 0.35)" : "none",
        overflow: "hidden",
        display: "grid",
        placeItems: "center",
        flexShrink: 0
      }}
    >
      <Image
        src="/images/sophia-mae-bebe.png"
        alt={alt}
        width={px * 2}
        height={px * 2}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </div>
  );
}
