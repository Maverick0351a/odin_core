"""
WebSocket-based real-time conversation viewer
Frontend interface for observing two-model conversations with self-reflection
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from demo_data import create_demo_endpoint_data

frontend_router = APIRouter()

@frontend_router.get("/conversation-viewer/demo")
async def demo_data():
    """Get demo conversation data with reflections"""
    return JSONResponse(create_demo_endpoint_data())

@frontend_router.get("/conversation-viewer", response_class=HTMLResponse)
async def conversation_viewer():
    """Modern ODIN Protocol Conversation Observatory with Self-Reflection UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ODIN Protocol 2.0 - Conversation Observatory</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            :root {
                --primary-bg: #0a0e1a;
                --secondary-bg: #1a1f2e;
                --card-bg: #252a3a;
                --accent-blue: #00d4ff;
                --accent-purple: #8b5cf6;
                --accent-pink: #ec4899;
                --success-green: #10b981;
                --warning-orange: #f59e0b;
                --error-red: #ef4444;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --border-color: #334155;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 50%, #252a3a 100%);
                color: var(--text-primary);
                min-height: 100vh;
                margin: 0;
                overflow-x: hidden;
            }
            
            .glass-effect {
                backdrop-filter: blur(12px);
                background: rgba(37, 42, 58, 0.8);
                border: 1px solid rgba(148, 163, 184, 0.1);
            }
            
            .neon-border {
                position: relative;
                overflow: hidden;
            }
            
            .neon-border::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
                transition: left 0.5s;
                z-index: -1;
            }
            
            .neon-border:hover::before {
                left: 100%;
            }
            
            .gradient-text {
                background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple), var(--accent-pink));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .pulse-animation {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .slide-in {
                animation: slideIn 0.5s ease-out;
            }
            
            @keyframes slideIn {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            .reflection-glow {
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            }
            
            .confidence-gradient {
                background: linear-gradient(90deg, var(--error-red) 0%, var(--warning-orange) 50%, var(--success-green) 100%);
            }
            
            .action-icon-pass { color: var(--success-green); }
            .action-icon-modify { color: var(--warning-orange); }
            .action-icon-reject { color: var(--error-red); }
            
            .feedback-loop {
                position: relative;
            }
            
            .feedback-loop::after {
                content: '↻';
                position: absolute;
                right: -30px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 1.5rem;
                color: var(--accent-blue);
                animation: rotate 2s linear infinite;
            }
            
            @keyframes rotate {
                from { transform: translateY(-50%) rotate(0deg); }
                to { transform: translateY(-50%) rotate(360deg); }
            }
            
            .model-card {
                transition: all 0.3s ease;
            }
            
            .model-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            }
            
            .conversation-turn {
                border-left: 4px solid transparent;
                transition: all 0.3s ease;
            }
            
            .conversation-turn.model-a {
                border-left-color: var(--accent-blue);
            }
            
            .conversation-turn.model-b {
                border-left-color: var(--accent-purple);
            }
            
            .reflection-card {
                border-radius: 12px;
                overflow: hidden;
                position: relative;
            }
            
            .reflection-card.pass {
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            
            .reflection-card.modify {
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
                border: 1px solid rgba(245, 158, 11, 0.3);
            }
            
            .reflection-card.reject {
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            
            .config-input {
                background: rgba(37, 42, 58, 0.8);
                border: 1px solid var(--border-color);
                color: var(--text-primary);
                padding: 12px 16px;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            
            .config-input:focus {
                outline: none;
                border-color: var(--accent-blue);
                box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
            }
            
            .action-button {
                background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
            }
            
            .action-button:disabled {
                background: var(--border-color);
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .status-indicator {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .status-active {
                background: rgba(16, 185, 129, 0.2);
                color: var(--success-green);
                border: 1px solid rgba(16, 185, 129, 0.3);
            }
            
            .status-processing {
                background: rgba(245, 158, 11, 0.2);
                color: var(--warning-orange);
                border: 1px solid rgba(245, 158, 11, 0.3);
            }
            
            .status-completed {
                background: rgba(139, 92, 246, 0.2);
                color: var(--accent-purple);
                border: 1px solid rgba(139, 92, 246, 0.3);
            }
            
            .timeline-connector {
                position: relative;
                margin: 0 auto;
                width: 2px;
                height: 30px;
                background: linear-gradient(to bottom, var(--accent-blue), var(--accent-purple));
            }
            
            .timeline-connector::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 8px;
                height: 8px;
                background: var(--accent-blue);
                border-radius: 50%;
                box-shadow: 0 0 10px var(--accent-blue);
            }
            
            .scroll-area {
                scrollbar-width: thin;
                scrollbar-color: var(--accent-blue) transparent;
            }
            
            .scroll-area::-webkit-scrollbar {
                width: 6px;
            }
            
            .scroll-area::-webkit-scrollbar-track {
                background: transparent;
            }
            
            .scroll-area::-webkit-scrollbar-thumb {
                background: var(--accent-blue);
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="min-h-screen p-6">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-5xl font-bold gradient-text mb-4">
                    🧠 ODIN Protocol 2.0
                </h1>
                <p class="text-xl text-secondary mb-2">
                    AI Conversation Observatory with Self-Reflection
                </p>
                <p class="text-secondary">
                    Watch AI models think, communicate, and self-correct in real-time
                </p>
            </div>
            
            <!-- Model Configuration Cards -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <!-- Model A Configuration -->
                <div class="glass-effect rounded-xl p-6 model-card">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
                            🤖
                        </div>
                        <div>
                            <h3 class="text-xl font-semibold">Model A Configuration</h3>
                            <p class="text-secondary text-sm">Primary conversation agent</p>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <input type="text" id="modelA" placeholder="Model name (e.g., gpt-4o)" 
                               value="gpt-4o" class="config-input w-full">
                        <input type="text" id="roleA" placeholder="Role (e.g., critical analyst)" 
                               value="critical analyst" class="config-input w-full">
                        <textarea id="promptA" placeholder="System prompt" rows="3" 
                                  class="config-input w-full resize-none">You are a critical analyst who questions assumptions and seeks deeper understanding.</textarea>
                    </div>
                    
                    <div class="mt-4 p-3 rounded-lg bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm text-secondary">Confidence Level</span>
                            <span id="confidenceA" class="text-sm font-medium">0%</span>
                        </div>
                        <div class="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div id="confidenceBarA" class="h-full confidence-gradient transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Model B Configuration -->
                <div class="glass-effect rounded-xl p-6 model-card">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                            🎭
                        </div>
                        <div>
                            <h3 class="text-xl font-semibold">Model B Configuration</h3>
                            <p class="text-secondary text-sm">Secondary conversation agent</p>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <input type="text" id="modelB" placeholder="Model name (e.g., gemini-1.5-flash)" 
                               value="gemini-1.5-flash" class="config-input w-full">
                        <input type="text" id="roleB" placeholder="Role (e.g., optimistic supporter)" 
                               value="optimistic supporter" class="config-input w-full">
                        <textarea id="promptB" placeholder="System prompt" rows="3" 
                                  class="config-input w-full resize-none">You are an optimistic supporter who finds positive aspects and builds on ideas.</textarea>
                    </div>
                    
                    <div class="mt-4 p-3 rounded-lg bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm text-secondary">Confidence Level</span>
                            <span id="confidenceB" class="text-sm font-medium">0%</span>
                        </div>
                        <div class="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div id="confidenceBarB" class="h-full confidence-gradient transition-all duration-500" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Conversation Controls -->
            <div class="glass-effect rounded-xl p-6 mb-8">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <input type="text" id="topic" placeholder="Initial conversation topic" 
                           value="The future of artificial intelligence" class="config-input">
                    <input type="number" id="maxTurns" placeholder="Max turns" value="10" min="1" max="50" class="config-input">
                    <select id="mediatorModel" class="config-input">
                        <option value="gemini-1.5-flash">Gemini 1.5 Flash (Mediator)</option>
                        <option value="gpt-4o">GPT-4O (Mediator)</option>
                    </select>
                </div>
                
                <div class="flex flex-wrap gap-4 items-center">
                    <button onclick="startConversation()" class="action-button">
                        🚀 Start Conversation
                    </button>
                    <button onclick="nextTurn()" id="nextTurnBtn" class="action-button" disabled>
                        ▶️ Next Turn
                    </button>
                    <button onclick="toggleReflection()" id="reflectionToggle" class="action-button">
                        🧠 Show Reflections
                    </button>
                    <button onclick="loadDemo()" class="action-button" style="background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple));">
                        🎭 Load Demo
                    </button>
                    
                    <div id="statusIndicators" class="flex gap-3 ml-auto">
                        <span class="status-indicator status-active" id="conversationStatus">Ready</span>
                        <span class="status-indicator" id="turnCounter">Turn: 0</span>
                    </div>
                </div>
            </div>
            
            <!-- Main Content Grid -->
            <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <!-- Conversation Timeline (2/3 width) -->
                <div class="xl:col-span-2">
                    <div class="glass-effect rounded-xl p-6">
                        <div class="flex items-center gap-3 mb-6">
                            <div class="w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-teal-500 flex items-center justify-center">
                                💬
                            </div>
                            <h3 class="text-xl font-semibold">Conversation Timeline</h3>
                        </div>
                        
                        <div id="conversationArea" class="scroll-area h-96 overflow-y-auto space-y-4">
                            <div class="text-center text-secondary py-12">
                                <div class="text-6xl mb-4">🤖</div>
                                <p class="text-lg">Configure models and start a conversation</p>
                                <p class="text-sm">Watch AI agents think and communicate in real-time</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Self-Reflection Logs (1/3 width) -->
                <div>
                    <div class="glass-effect rounded-xl p-6">
                        <div class="flex items-center gap-3 mb-6">
                            <div class="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                                🧠
                            </div>
                            <h3 class="text-xl font-semibold">Self-Reflection Logs</h3>
                        </div>
                        
                        <div id="reflectionArea" class="scroll-area h-96 overflow-y-auto space-y-3">
                            <div class="text-center text-secondary py-12">
                                <div class="text-4xl mb-3">🔍</div>
                                <p class="text-sm">Mediator evaluations will appear here</p>
                                <p class="text-xs">Pass • Modify • Reject actions</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        
        <script>
            let currentConversationId = null;
            let reflectionMode = false;
            let turnCounter = 0;
            
            // UI State Management
            function updateConfidence(model, confidence) {
                const percentage = Math.round(confidence * 100);
                document.getElementById(`confidence${model}`).textContent = `${percentage}%`;
                document.getElementById(`confidenceBar${model}`).style.width = `${percentage}%`;
            }
            
            function showToast(message, type = 'info') {
                const toast = document.createElement('div');
                toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 slide-in ${
                    type === 'success' ? 'bg-green-500' : 
                    type === 'error' ? 'bg-red-500' : 
                    type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                } text-white`;
                toast.textContent = message;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }
            
            // Conversation Management
            async function startConversation() {
                const request = {
                    model_a: {
                        name: document.getElementById('modelA').value,
                        role: document.getElementById('roleA').value,
                        system_prompt: document.getElementById('promptA').value,
                        thinking_style: "analytical"
                    },
                    model_b: {
                        name: document.getElementById('modelB').value,
                        role: document.getElementById('roleB').value,
                        system_prompt: document.getElementById('promptB').value,
                        thinking_style: "creative"
                    },
                    mediator_model: document.getElementById('mediatorModel').value,
                    conversation_style: "collaborative_with_reflection",
                    initial_topic: document.getElementById('topic').value,
                    max_turns: parseInt(document.getElementById('maxTurns').value),
                    enable_reflection: true
                };
                
                try {
                    const response = await fetch('/conversation/mediated/start', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(request)
                    });
                    
                    const data = await response.json();
                    currentConversationId = data.conversation_id;
                    turnCounter = 0;
                    
                    // Update UI state
                    document.getElementById('nextTurnBtn').disabled = false;
                    document.getElementById('conversationStatus').textContent = 'Active';
                    document.getElementById('conversationStatus').className = 'status-indicator status-active';
                    
                    // Clear areas
                    document.getElementById('conversationArea').innerHTML = '';
                    document.getElementById('reflectionArea').innerHTML = '';
                    
                    // Add initial topic
                    addConversationTurn({
                        type: 'topic',
                        content: request.initial_topic,
                        timestamp: new Date().toISOString()
                    });
                    
                    showToast('Conversation started successfully!', 'success');
                    
                } catch (error) {
                    showToast('Failed to start conversation: ' + error.message, 'error');
                }
            }
            
            async function nextTurn() {
                if (!currentConversationId) return;
                
                const button = document.getElementById('nextTurnBtn');
                button.disabled = true;
                button.textContent = '⏳ Processing...';
                
                try {
                    const response = await fetch(`/conversation/mediated/${currentConversationId}/turn`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ enable_reflection: reflectionMode })
                    });
                    
                    const data = await response.json();
                    turnCounter++;
                    
                    // Display conversation turn
                    addConversationTurn(data);
                    
                    // Process reflections if enabled
                    if (data.reflections) {
                        for (const reflection of data.reflections) {
                            addReflectionCard(reflection);
                        }
                    }
                    
                    // Update confidence levels
                    if (data.model_a?.confidence) {
                        updateConfidence('A', data.model_a.confidence);
                    }
                    if (data.model_b?.confidence) {
                        updateConfidence('B', data.model_b.confidence);
                    }
                    
                    // Update status
                    document.getElementById('turnCounter').textContent = `Turn: ${turnCounter}`;
                    
                    if (data.conversation_status === 'completed') {
                        button.textContent = '✅ Completed';
                        document.getElementById('conversationStatus').textContent = 'Completed';
                        document.getElementById('conversationStatus').className = 'status-indicator status-completed';
                        showToast('Conversation completed!', 'success');
                    } else {
                        button.disabled = false;
                        button.textContent = '▶️ Next Turn';
                    }
                    
                } catch (error) {
                    showToast('Failed to process turn: ' + error.message, 'error');
                    button.disabled = false;
                    button.textContent = '▶️ Next Turn';
                }
            }
            
            function toggleReflection() {
                reflectionMode = !reflectionMode;
                const button = document.getElementById('reflectionToggle');
                
                if (reflectionMode) {
                    button.textContent = '🧠 Hide Reflections';
                    button.style.background = 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))';
                    showToast('Self-reflection mode enabled', 'info');
                } else {
                    button.textContent = '🧠 Show Reflections';
                    button.style.background = 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))';
                    showToast('Self-reflection mode disabled', 'info');
                }
            }
            
            async function loadDemo() {
                try {
                    showToast('Loading demo data...', 'info');
                    
                    const response = await fetch('/conversation-viewer/demo');
                    const demoData = await response.json();
                    
                    // Clear existing content
                    document.getElementById('conversationArea').innerHTML = '';
                    document.getElementById('reflectionArea').innerHTML = '';
                    
                    // Update configuration with demo models
                    document.getElementById('modelA').value = demoData.conversation.models.model_a.name;
                    document.getElementById('roleA').value = demoData.conversation.models.model_a.role;
                    document.getElementById('modelB').value = demoData.conversation.models.model_b.name;
                    document.getElementById('roleB').value = demoData.conversation.models.model_b.role;
                    document.getElementById('topic').value = demoData.conversation.topic;
                    
                    // Update status
                    document.getElementById('conversationStatus').textContent = 'Demo Mode';
                    document.getElementById('conversationStatus').className = 'status-indicator status-processing';
                    document.getElementById('turnCounter').textContent = `Turns: ${demoData.summary.total_turns}`;
                    
                    // Enable reflection mode
                    reflectionMode = true;
                    document.getElementById('reflectionToggle').textContent = '🧠 Hide Reflections';
                    document.getElementById('reflectionToggle').style.background = 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))';
                    
                    // Add topic introduction
                    addConversationTurn({
                        type: 'topic',
                        content: demoData.conversation.topic,
                        timestamp: demoData.conversation.created_at
                    });
                    
                    // Animate through turns and reflections
                    let turnIndex = 0;
                    let reflectionIndex = 0;
                    
                    const animationInterval = setInterval(() => {
                        // Add conversation turn
                        if (turnIndex < demoData.conversation.turns.length) {
                            const turn = demoData.conversation.turns[turnIndex];
                            turnCounter = turn.turn_number;
                            addConversationTurn(turn);
                            
                            // Update confidence for the active model
                            if (turn.current_speaker === 'model_a') {
                                updateConfidence('A', turn.thought_process.confidence);
                            } else {
                                updateConfidence('B', turn.thought_process.confidence);
                            }
                            
                            turnIndex++;
                        }
                        
                        // Add reflection (slight delay for realism)
                        setTimeout(() => {
                            if (reflectionIndex < demoData.conversation.reflections.length) {
                                const reflection = demoData.conversation.reflections[reflectionIndex];
                                addReflectionCard(reflection);
                                reflectionIndex++;
                            }
                        }, 500);
                        
                        // Stop animation when done
                        if (turnIndex >= demoData.conversation.turns.length && 
                            reflectionIndex >= demoData.conversation.reflections.length) {
                            clearInterval(animationInterval);
                            
                            // Update final status
                            document.getElementById('conversationStatus').textContent = 'Demo Complete';
                            document.getElementById('conversationStatus').className = 'status-indicator status-completed';
                            
                            showToast(`Demo loaded! ${demoData.summary.total_reflections} reflections processed.`, 'success');
                        }
                    }, 1200); // 1.2 second intervals for dramatic effect
                    
                } catch (error) {
                    showToast('Failed to load demo: ' + error.message, 'error');
                }
            }
            
            // UI Component Builders
            function addConversationTurn(turnData) {
                const conversationArea = document.getElementById('conversationArea');
                
                if (turnData.type === 'topic') {
                    const topicHtml = `
                        <div class="slide-in p-4 rounded-lg bg-gradient-to-r from-indigo-500/20 to-purple-500/20 border border-indigo-500/30">
                            <div class="flex items-center gap-3 mb-2">
                                <div class="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                                    🎯
                                </div>
                                <h4 class="font-semibold">Initial Topic</h4>
                            </div>
                            <p class="text-secondary">${turnData.content}</p>
                        </div>
                    `;
                    conversationArea.innerHTML += topicHtml;
                    return;
                }
                
                const turnHtml = `
                    <div class="slide-in">
                        <div class="timeline-connector"></div>
                        <div class="conversation-turn ${turnData.current_speaker === 'model_a' ? 'model-a' : 'model-b'} 
                                    glass-effect rounded-xl p-6 mb-4">
                            
                            <!-- Turn Header -->
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-full ${
                                        turnData.current_speaker === 'model_a' 
                                        ? 'bg-gradient-to-r from-blue-500 to-cyan-500' 
                                        : 'bg-gradient-to-r from-purple-500 to-pink-500'
                                    } flex items-center justify-center">
                                        ${turnData.current_speaker === 'model_a' ? '🤖' : '🎭'}
                                    </div>
                                    <div>
                                        <h4 class="font-semibold">${turnData.current_speaker === 'model_a' ? turnData.model_a?.name || 'Model A' : turnData.model_b?.name || 'Model B'}</h4>
                                        <p class="text-sm text-secondary">${turnData.current_speaker === 'model_a' ? turnData.model_a?.role || 'Analyst' : turnData.model_b?.role || 'Supporter'}</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <div class="text-sm text-secondary">Turn ${turnCounter}</div>
                                    <div class="text-xs text-secondary">${new Date().toLocaleTimeString()}</div>
                                </div>
                            </div>
                            
                            <!-- Thought Process -->
                            ${turnData.thought_process ? `
                            <div class="mb-4 p-4 rounded-lg bg-black/20 border border-gray-600/30">
                                <h5 class="font-medium mb-2 flex items-center gap-2">
                                    <span>💭</span> Thought Process
                                </h5>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                                    <div><strong>Step:</strong> ${turnData.thought_process.step || 'N/A'}</div>
                                    <div><strong>Confidence:</strong> ${((turnData.thought_process.confidence || 0) * 100).toFixed(1)}%</div>
                                    <div class="md:col-span-2"><strong>Reasoning:</strong> ${turnData.thought_process.reasoning || 'N/A'}</div>
                                </div>
                            </div>
                            ` : ''}
                            
                            <!-- Message Content -->
                            <div class="p-4 rounded-lg bg-white/5 border border-white/10">
                                <h5 class="font-medium mb-2 flex items-center gap-2">
                                    <span>💬</span> Response
                                </h5>
                                <p class="text-primary leading-relaxed">${turnData.message || turnData.response || 'No message content'}</p>
                            </div>
                            
                            <!-- Mediator Analysis -->
                            ${turnData.mediator_analysis ? `
                            <div class="mt-4 p-4 rounded-lg bg-gradient-to-r from-green-500/10 to-teal-500/10 border border-green-500/30">
                                <h5 class="font-medium mb-2 flex items-center gap-2">
                                    <span>⚖️</span> Mediator Analysis
                                </h5>
                                <div class="text-sm space-y-1">
                                    <div><strong>Health:</strong> ${turnData.mediator_analysis.conversation_health}</div>
                                    <div><strong>Direction:</strong> ${turnData.mediator_analysis.next_direction}</div>
                                    <div><strong>Themes:</strong> ${turnData.mediator_analysis.key_themes?.join(', ') || 'None'}</div>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;
                
                conversationArea.innerHTML += turnHtml;
                conversationArea.scrollTop = conversationArea.scrollHeight;
            }
            
            function addReflectionCard(reflection) {
                const reflectionArea = document.getElementById('reflectionArea');
                
                // Clear placeholder if this is the first reflection
                if (reflectionArea.children.length === 1 && reflectionArea.firstElementChild.textContent.includes('Mediator evaluations')) {
                    reflectionArea.innerHTML = '';
                }
                
                const actionIcon = {
                    'pass': '🟢',
                    'modify': '🟡', 
                    'reject': '🔴'
                }[reflection.action_taken] || '⚪';
                
                const reflectionHtml = `
                    <div class="reflection-card ${reflection.action_taken} p-4 mb-3 slide-in ${reflection.action_taken === 'reject' ? 'feedback-loop' : ''}">
                        <!-- Reflection Header -->
                        <div class="flex items-center justify-between mb-3">
                            <div class="flex items-center gap-2">
                                <span class="text-lg">${actionIcon}</span>
                                <span class="font-semibold text-sm uppercase tracking-wide">${reflection.action_taken}</span>
                            </div>
                            <div class="text-xs text-secondary">
                                Iteration ${reflection.iteration_count || 1}
                            </div>
                        </div>
                        
                        <!-- Mediator Info -->
                        <div class="flex items-center gap-2 mb-3">
                            <div class="w-6 h-6 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center text-xs">
                                🧠
                            </div>
                            <span class="text-sm text-secondary">${reflection.mediator_id || 'Mediator AI'}</span>
                        </div>
                        
                        <!-- Confidence Score -->
                        <div class="mb-3">
                            <div class="flex justify-between items-center mb-1">
                                <span class="text-xs text-secondary">Confidence</span>
                                <span class="text-xs font-medium">${((reflection.confidence_score || 0) * 100).toFixed(1)}%</span>
                            </div>
                            <div class="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                <div class="h-full confidence-gradient transition-all duration-500" 
                                     style="width: ${(reflection.confidence_score || 0) * 100}%"></div>
                            </div>
                        </div>
                        
                        <!-- Explanation -->
                        <div class="text-sm text-secondary leading-relaxed">
                            ${reflection.explanation || 'No explanation provided'}
                        </div>
                        
                        <!-- Correction Tags -->
                        ${reflection.correction_tags && reflection.correction_tags.length > 0 ? `
                        <div class="mt-3 flex flex-wrap gap-1">
                            ${reflection.correction_tags.map(tag => 
                                `<span class="text-xs px-2 py-1 rounded-full bg-white/10 text-secondary">${tag}</span>`
                            ).join('')}
                        </div>
                        ` : ''}
                        
                        <!-- Healed Message (if modified) -->
                        ${reflection.action_taken === 'modify' && reflection.healed_message ? `
                        <div class="mt-3 p-3 rounded-lg bg-white/5 border border-white/10">
                            <div class="text-xs text-secondary mb-1">✨ Healed Output:</div>
                            <div class="text-sm">${reflection.healed_message}</div>
                        </div>
                        ` : ''}
                    </div>
                `;
                
                reflectionArea.innerHTML += reflectionHtml;
                reflectionArea.scrollTop = reflectionArea.scrollHeight;
                
                // Add visual effect for rejected messages
                if (reflection.action_taken === 'reject') {
                    setTimeout(() => {
                        const cards = reflectionArea.querySelectorAll('.reflection-card.reject');
                        const latestCard = cards[cards.length - 1];
                        if (latestCard) {
                            latestCard.classList.add('reflection-glow');
                            setTimeout(() => latestCard.classList.remove('reflection-glow'), 2000);
                        }
                    }, 100);
                }
            }
            
            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                // Add some sample reflections for demo purposes
                if (window.location.hash === '#demo') {
                    setTimeout(() => {
                        addReflectionCard({
                            action_taken: 'pass',
                            mediator_id: 'demo-mediator',
                            confidence_score: 0.85,
                            explanation: 'Message meets quality standards with high confidence.',
                            iteration_count: 1
                        });
                        
                        setTimeout(() => {
                            addReflectionCard({
                                action_taken: 'modify',
                                mediator_id: 'demo-mediator',
                                confidence_score: 0.65,
                                explanation: 'Message contains uncertain language patterns that should be refined.',
                                correction_tags: ['low-confidence-language', 'clarity-improvement'],
                                healed_message: 'The research clearly demonstrates significant improvements in efficiency.',
                                iteration_count: 1
                            });
                        }, 1000);
                        
                        setTimeout(() => {
                            addReflectionCard({
                                action_taken: 'reject',
                                mediator_id: 'demo-mediator',
                                confidence_score: 0.35,
                                explanation: 'Message rejected due to potential hallucination and low confidence indicators.',
                                correction_tags: ['potential-hallucination', 'critical-quality-issues'],
                                iteration_count: 2
                            });
                        }, 2000);
                    }, 1000);
                }
            });
        </script>
    </body>
    </html>
    """
