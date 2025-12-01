// Node.js Vercel function for authentication
const jwt = require('jsonwebtoken');

// Demo credentials
const DEMO_USERS = {
  "admin@entrepedia.ai": "admin123",
  "admin": "admin123",
  "testuser": "test123",
  "test@example.com": "test123"
};

function createAccessToken(data) {
  const secret = process.env.JWT_SECRET_KEY || 'demo-secret-key-for-development';
  const expires = Math.floor(Date.now() / 1000) + (30 * 60); // 30 minutes

  return jwt.sign({
    ...data,
    exp: expires
  }, secret);
}

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Route handling
  const { url, method } = req;

  if (method === 'GET') {
    // Auth info endpoint
    res.status(200).json({
      message: "Entrepedia Authentication API",
      version: "1.0.0",
      status: "operational",
      endpoints: [
        "POST /login - Login with credentials",
        "POST /logout - Logout user",
        "GET / - This info"
      ]
    });
    return;
  }

  if (method === 'POST' && url.includes('/login')) {
    try {
      const body = req.body;
      const username = body.username;
      const password = body.password;

      if (username && password && DEMO_USERS[username] === password) {
        const token = createAccessToken({
          sub: username,
          user_id: 1
        });

        res.status(200).json({
          access_token: token,
          token_type: "bearer"
        });
      } else {
        res.status(401).json({
          detail: "Incorrect username or password"
        });
      }
    } catch (error) {
      res.status(500).json({
        detail: "Login failed: " + error.message
      });
    }
    return;
  }

  if (method === 'POST' && url.includes('/logout')) {
    res.status(200).json({
      success: true,
      message: "Logged out successfully"
    });
    return;
  }

  // Default response
  res.status(404).json({ error: "Not found" });
};