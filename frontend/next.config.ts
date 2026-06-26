import dotenv from "dotenv";
import type { NextConfig } from "next";
import path from "path";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

const nextConfig: NextConfig = {};

export default nextConfig;
