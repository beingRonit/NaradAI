import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backend = process.env.BACKEND_URL || "http://localhost:8000";
    return [
      {
        source: "/api/agent/:path*",
        destination: `${backend}/api/agent/:path*`,
      },
    ];
  },
};

export default nextConfig;
