// Node.js Vercel function for AI query/chat API

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

// Function to call Gemini API
async function callGeminiAPI(query, agentType = 'coach') {
  const apiKey = 'AIzaSyB7_gjyyVbSZPLzcrC5vQg0ZGxcLOGpMM8';

  if (!apiKey) {
    throw new Error('Gemini API key not configured. Please set GEMINI_API_KEY environment variable.');
  }

  console.log('Calling Gemini API with agent type:', agentType);

  // Create system prompt based on agent type
  const systemPrompts = {
    coach: `You are an AI Learning Coach. Your role is to:
- Provide personalized learning guidance and study tips
- Motivate and encourage learners
- Break down complex topics into manageable steps
- Suggest effective learning strategies
- Help with time management and study habits
- Be supportive, encouraging, and practical in your responses

Keep responses helpful, motivating, and focused on the learner's growth.`,

    strategist: `You are an AI Learning Strategist. Your role is to:
- Create comprehensive learning plans and strategies
- Analyze learning objectives and map out tactical approaches
- Suggest resource allocation and prioritization
- Design learning pathways for complex subjects
- Provide strategic thinking about education and skill development
- Focus on long-term learning goals and outcomes

Keep responses strategic, detailed, and focused on systematic learning approaches.`
  };

  const systemPrompt = systemPrompts[agentType] || systemPrompts.coach;

  try {
    // Using Gemini REST API
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `${systemPrompt}\n\nUser question: ${query}`
          }]
        }],
        generationConfig: {
          temperature: 0.7,
          topK: 40,
          topP: 0.95,
          maxOutputTokens: 1024,
        },
        safetySettings: [
          {
            category: "HARM_CATEGORY_HARASSMENT",
            threshold: "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            category: "HARM_CATEGORY_HATE_SPEECH",
            threshold: "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold: "BLOCK_MEDIUM_AND_ABOVE"
          },
          {
            category: "HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold: "BLOCK_MEDIUM_AND_ABOVE"
          }
        ]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Gemini API error:', response.status, errorText);
      throw new Error(`Gemini API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();

    if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
      console.error('Invalid Gemini response structure:', data);
      throw new Error('Invalid response from Gemini API');
    }

    const content = data.candidates[0].content.parts[0].text;

    return {
      content,
      agent: agentType,
      metadata: {
        model: 'gemini-pro',
        timestamp: new Date().toISOString(),
        usage: data.usageMetadata || {}
      }
    };

  } catch (error) {
    console.error('Gemini API call failed:', error);
    throw error;
  }
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

  const { url, method } = req;
  console.log('Query API:', method, url);

  // POST /api/query/ask - AI chat endpoint
  if (method === 'POST' && (url === '/api/query/ask' || url.endsWith('/ask'))) {
    try {
      let body;
      if (req.body) {
        body = req.body;
      } else {
        const rawBody = await getRawBody(req);
        body = JSON.parse(rawBody);
      }

      console.log('Query request:', body);

      const { query, agent_type = 'coach', include_knowledge_base = false } = body;

      if (!query || typeof query !== 'string') {
        res.status(400).json({
          success: false,
          error: "Query is required and must be a string"
        });
        return;
      }

      // Call Gemini API
      const aiResponse = await callGeminiAPI(query, agent_type);

      res.status(200).json({
        success: true,
        response: aiResponse,
        knowledge_base_results: include_knowledge_base ? 0 : undefined,
        agent_used: agent_type
      });
      return;

    } catch (error) {
      console.error('Query processing error:', error);
      res.status(500).json({
        success: false,
        error: error.message,
        response: {
          content: "I apologize, but I'm experiencing technical difficulties. Please check that your Gemini API key is properly configured and try again.",
          agent: 'system',
          metadata: {
            error: true,
            timestamp: new Date().toISOString()
          }
        }
      });
      return;
    }
  }

  // GET /api/query/agents - List available agents
  if (method === 'GET' && (url === '/api/query/agents' || url.endsWith('/agents'))) {
    res.status(200).json({
      success: true,
      agents: [
        {
          id: 'coach',
          name: 'Learning Coach',
          description: 'Provides personalized learning guidance, motivation, and study tips',
          icon: 'sparkles'
        },
        {
          id: 'strategist',
          name: 'Learning Strategist',
          description: 'Creates comprehensive learning plans and strategic approaches',
          icon: 'brain'
        }
      ]
    });
    return;
  }

  // Default response for unsupported endpoints
  res.status(404).json({
    success: false,
    error: "Query API endpoint not found",
    available_endpoints: [
      "POST /ask - Chat with AI agents",
      "GET /agents - List available AI agents"
    ]
  });
};