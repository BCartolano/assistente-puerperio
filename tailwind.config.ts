import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/pages/**/*.{js,ts,jsx,tsx,mdx}", "./src/components/**/*.{js,ts,jsx,tsx,mdx}", "./src/app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        roseComfort: "#F4C2C2",
        roseComfortSoft: "#FBE5E5",
        roseComfortDeep: "#C97777",
        sageComfort: "#A8BCA1",
        sageComfortSoft: "#E3ECE0",
        sageComfortDeep: "#6F8A68"
      }
    }
  },
  plugins: []
};

export default config;
