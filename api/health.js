// Node.js Vercel function for health check

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  res.status(200).json({
    status: "healthy",
    service: "Entrepedia AI Platform",
    version: "1.0.0",
    deployment: "vercel",
    runtime: "nodejs"
  });
};