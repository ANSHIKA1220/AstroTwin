import type { NextConfig } from "next";

const apiProxyTarget = (
  process.env.API_PROXY_TARGET ?? process.env.NEXT_PUBLIC_API_URL ?? ""
).replace(/\/$/, "");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    if (!apiProxyTarget) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${apiProxyTarget}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
