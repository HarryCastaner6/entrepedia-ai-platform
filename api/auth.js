// Node.js Vercel function for authentication
const jwt = require('jsonwebtoken');

// Helper function to parse request body
function getRawBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      resolve(body);
    });
    req.on('error', reject);
  });
}

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

  if (method === 'POST' && (url.includes('/login') || url === '/api/auth')) {
    try {
      // Parse request body based on content type
      const contentType = req.headers['content-type'] || '';
      let username, password;

      if (req.body) {
        // Body already parsed by Vercel
        if (contentType.includes('application/json')) {
          username = req.body.username;
          password = req.body.password;
        } else {
          // Form data
          username = req.body.username;
          password = req.body.password;
        }
      } else {
        // Manually parse the body
        const rawBody = await getRawBody(req);
        console.log('Raw body:', rawBody);
        console.log('Content-Type:', contentType);

        if (contentType.includes('application/json')) {
          try {
            const body = JSON.parse(rawBody);
            username = body.username;
            password = body.password;
          } catch (parseError) {
            console.log('JSON parse error:', parseError.message);
            res.status(400).json({
              detail: "Invalid JSON in request body"
            });
            return;
          }
        } else if (contentType.includes('application/x-www-form-urlencoded')) {
          // Parse form data
          const params = new URLSearchParams(rawBody);
          username = params.get('username');
          password = params.get('password');
        } else {
          res.status(400).json({
            detail: "Unsupported content type. Use application/json or application/x-www-form-urlencoded"
          });
          return;
        }
      }

      console.log('Username:', username, 'Password provided:', !!password);

      if (!username || !password) {
        res.status(400).json({
          detail: "Username and password are required"
        });
        return;
      }

      if (DEMO_USERS[username] === password) {
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

  if (method === 'POST' && (url.includes('/logout') || (url === '/api/auth' && req.query?.action === 'logout'))) {
    res.status(200).json({
      success: true,
      message: "Logged out successfully"
    });
    return;
  }

  // Default response
  res.status(404).json({ error: "Not found" });
};