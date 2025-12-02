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
      console.log('All headers:', JSON.stringify(req.headers, null, 2));
      console.log('Content-Type:', contentType);
      console.log('URL:', url);
      console.log('Method:', method);

      let username, password;

      if (req.body) {
        // Body already parsed by Vercel - try to get username/password directly
        username = req.body.username;
        password = req.body.password;
        console.log('Using pre-parsed body');
      } else {
        // Manually parse the body
        const rawBody = await getRawBody(req);
        console.log('Raw body:', rawBody);

        // Try JSON first
        if (contentType.includes('application/json') || rawBody.trim().startsWith('{')) {
          try {
            const body = JSON.parse(rawBody);
            username = body.username;
            password = body.password;
            console.log('Parsed as JSON');
          } catch (parseError) {
            console.log('JSON parse error:', parseError.message);
            res.status(400).json({
              detail: "Invalid JSON in request body"
            });
            return;
          }
        } else if (contentType.includes('application/x-www-form-urlencoded') || rawBody.includes('username=')) {
          // Parse form data
          const params = new URLSearchParams(rawBody);
          username = params.get('username');
          password = params.get('password');
          console.log('Parsed as form data');
        } else {
          console.log('Unknown content type, trying as JSON fallback');
          try {
            const body = JSON.parse(rawBody);
            username = body.username;
            password = body.password;
          } catch {
            res.status(400).json({
              detail: "Unable to parse request. Please send JSON with username and password fields."
            });
            return;
          }
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