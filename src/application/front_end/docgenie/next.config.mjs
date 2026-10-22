/** @type {import('next').NextConfig} */
const nextConfig = {
  // self-contained build for the Docker image (`next dev` is unaffected)
  output: "standalone",
};

export default nextConfig;
