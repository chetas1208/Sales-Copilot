// SalesStream Overlook - Content Script
// Injects a glassmorphism overlay into Google Meet

(function() {
  'use strict';

  // Only run on Google Meet pages
  if (!window.location.hostname.includes('meet.google.com')) {
    return;
  }

  // Wait for the page to fully load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOverlay);
  } else {
    initOverlay();
  }

  function initOverlay() {
    // Check if overlay already exists
    if (document.getElementById('salesstream-overlay-container')) {
      return;
    }

    // Create container for Shadow DOM
    const container = document.createElement('div');
    container.id = 'salesstream-overlay-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999999;
      pointer-events: none;
    `;

    // Attach Shadow DOM for style isolation
    const shadow = container.attachShadow({ mode: 'open' });

    // Create the overlay
    const overlay = createOverlayElement();
    shadow.appendChild(overlay);

    // Add styles to Shadow DOM
    const style = document.createElement('style');
    style.textContent = getOverlayStyles();
    shadow.appendChild(style);

    // Append to body
    document.body.appendChild(container);

    // Setup drag functionality
    setupDragging(overlay, container);

    // Setup minimize/expand
    setupControls(overlay);

    console.log('[SalesStream] Overlay initialized');
  }

  function createOverlayElement() {
    const overlay = document.createElement('div');
    overlay.className = 'salesstream-overlay';
    overlay.innerHTML = `
      <div class="overlay-header">
        <div class="header-left">
          <div class="logo">SS</div>
          <h3>SalesStream Overlook</h3>
        </div>
        <div class="header-controls">
          <button class="control-btn minimize-btn" title="Minimize">−</button>
          <button class="control-btn close-btn" title="Close">×</button>
        </div>
      </div>

      <div class="overlay-content">
        <div class="insight-section">
          <div class="section-header">
            <span class="section-icon">🎙️</span>
            <span class="section-title">Live Transcription</span>
          </div>
          <div class="section-content transcript-content">
            <p class="placeholder-text">Waiting for meeting audio...</p>
          </div>
        </div>

        <div class="insight-section">
          <div class="section-header">
            <span class="section-icon">•</span>
            <span class="section-title">Real-time Insights</span>
          </div>
          <div class="section-content">
            <p class="placeholder-text">Listening for conversation context...</p>
          </div>
        </div>

        <div class="insight-section">
          <div class="section-header">
            <span class="section-icon">💡</span>
            <span class="section-title">What to Say Next</span>
          </div>
          <div class="section-content suggestions-list">
            <div class="suggestion-item" style="opacity: 0.5;">
              <span class="bullet">•</span>
              <span>Waiting for conversation to start...</span>
            </div>
          </div>
        </div>

        <div class="insight-section">
          <div class="section-header">
            <span class="section-icon">▸</span>
            <span class="section-title">Next Steps</span>
          </div>
          <div class="section-content">
            <p class="placeholder-text">AI will suggest action items here...</p>
          </div>
        </div>

        <div class="status-bar">
          <span class="status-indicator">●</span>
          <span class="status-text">Connected</span>
        </div>
      </div>
    `;

    return overlay;
  }

  function getOverlayStyles() {
    return `
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      .salesstream-overlay {
        width: 380px;
        max-height: 85vh;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        overflow: hidden;
        pointer-events: all;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }

      .salesstream-overlay.minimized {
        max-height: 60px;
      }

      .salesstream-overlay.minimized .overlay-content {
        display: none;
      }

      .overlay-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        cursor: move;
        user-select: none;
      }

      .header-left {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .logo {
        font-size: 20px;
      }

      h3 {
        font-size: 15px;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      }

      .header-controls {
        display: flex;
        gap: 6px;
      }

      .control-btn {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        font-size: 18px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        padding: 0;
      }

      .control-btn:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
      }

      .overlay-content {
        padding: 16px;
        overflow-y: auto;
        max-height: calc(85vh - 60px);
      }

      .overlay-content::-webkit-scrollbar {
        width: 6px;
      }

      .overlay-content::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 3px;
      }

      .overlay-content::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
      }

      .insight-section {
        margin-bottom: 16px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
      }

      .section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
      }

      .section-icon {
        font-size: 18px;
      }

      .section-title {
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
      }

      .section-content {
        color: rgba(255, 255, 255, 0.9);
        font-size: 13px;
        line-height: 1.6;
      }

      .placeholder-text {
        color: rgba(255, 255, 255, 0.6);
        font-style: italic;
        font-size: 12px;
      }

      .transcript-content {
        max-height: 200px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
      }

      .transcript-content::-webkit-scrollbar {
        width: 4px;
      }

      .transcript-content::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
      }

      .transcript-content::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
      }

      .transcript-line {
        margin: 4px 0;
        padding: 6px 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        font-size: 12px;
        line-height: 1.5;
        animation: slideIn 0.3s ease-out;
      }

      .transcript-line.partial {
        opacity: 0.7;
        font-style: italic;
      }

      .transcript-timestamp {
        color: rgba(255, 255, 255, 0.5);
        font-size: 10px;
        margin-right: 6px;
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(-5px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .suggestions-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .suggestion-item {
        display: flex;
        gap: 8px;
        padding: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
      }

      .suggestion-item:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateX(2px);
      }

      .bullet {
        color: rgba(255, 255, 255, 0.5);
        font-weight: bold;
      }

      .status-bar {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 12px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        font-size: 12px;
      }

      .status-indicator {
        font-size: 10px;
        animation: pulse 2s infinite;
      }

      .status-text {
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
    `;
  }

  function setupDragging(overlay, container) {
    const header = overlay.querySelector('.overlay-header');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);

    function dragStart(e) {
      if (e.target.classList.contains('control-btn')) {
        return; // Don't drag when clicking controls
      }

      initialX = e.clientX - container.offsetLeft;
      initialY = e.clientY - container.offsetTop;
      isDragging = true;
      overlay.style.cursor = 'grabbing';
    }

    function drag(e) {
      if (!isDragging) return;

      e.preventDefault();
      currentX = e.clientX - initialX;
      currentY = e.clientY - initialY;

      // Keep within viewport bounds
      const maxX = window.innerWidth - overlay.offsetWidth;
      const maxY = window.innerHeight - overlay.offsetHeight;

      currentX = Math.max(0, Math.min(currentX, maxX));
      currentY = Math.max(0, Math.min(currentY, maxY));

      container.style.left = currentX + 'px';
      container.style.top = currentY + 'px';
      container.style.right = 'auto';
    }

    function dragEnd() {
      isDragging = false;
      header.style.cursor = 'move';
    }
  }

  function setupControls(overlay) {
    const minimizeBtn = overlay.querySelector('.minimize-btn');
    const closeBtn = overlay.querySelector('.close-btn');

    minimizeBtn.addEventListener('click', () => {
      overlay.classList.toggle('minimized');
      minimizeBtn.textContent = overlay.classList.contains('minimized') ? '+' : '−';
    });

    closeBtn.addEventListener('click', () => {
      const container = document.getElementById('salesstream-overlay-container');
      if (container) {
        container.style.opacity = '0';
        setTimeout(() => container.remove(), 300);
      }
    });
  }

  // ============================================================================
  // WebSocket Connection Manager
  // ============================================================================

  class WebSocketManager {
    constructor() {
      this.ws = null;
      this.reconnectAttempts = 0;
      this.maxReconnectAttempts = 5;
      this.reconnectDelay = 3000;
      this.isConnecting = false;
      this.backendUrl = 'ws://localhost:8000/ws';
    }

    connect() {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
        console.log('Already connected or connecting');
        return;
      }

      this.isConnecting = true;
      console.log('Connecting to backend:', this.backendUrl);

      try {
        this.ws = new WebSocket(this.backendUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected to Meetstream AI backend');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.updateConnectionStatus(true);
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (e) {
            console.error('Failed to parse message:', e);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.updateConnectionStatus(false);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.isConnecting = false;
          this.updateConnectionStatus(false);
          this.attemptReconnect();
        };

      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        this.isConnecting = false;
        this.updateConnectionStatus(false);
      }
    }

    attemptReconnect() {
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.log('Max reconnect attempts reached');
        this.updateConnectionStatus(false, 'Connection failed. Please restart backend.');
        return;
      }

      this.reconnectAttempts++;
      console.log(`Reconnecting... attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
    }

    send(message) {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(message));
      } else {
        console.warn('WebSocket not connected. Cannot send message.');
      }
    }

    handleMessage(message) {
      console.log('Received message:', message.type);

      switch (message.type) {
        case 'connection_established':
          console.log('Connection established:', message.connection_id);
          break;

        case 'live_transcript':
          this.handleLiveTranscript(message);
          break;

        case 'research_started':
          this.showNotification('Research Started', 'AI agents are analyzing the company...');
          break;

        case 'agent_update':
          this.handleAgentUpdate(message);
          break;

        case 'insight':
          this.handleInsight(message);
          break;

        case 'research_completed':
          this.showNotification('Research Complete', 'All insights are ready!');
          break;

        case 'error':
          this.showNotification('Error', message.message, 'error');
          break;

        case 'pong':
          // Keep-alive response
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    }

    handleLiveTranscript(message) {
      const { transcript, new_text, end_of_turn, timestamp, speaker } = message;

      // Use new_text for incremental updates, fallback to transcript
      const textToShow = new_text || transcript;
      if (!textToShow || textToShow.trim() === '') return;

      const overlay = this.getOverlay();
      if (!overlay) return;

      const transcriptContent = overlay.querySelector('.transcript-content');
      if (!transcriptContent) return;

      // Remove placeholder if exists
      const placeholder = transcriptContent.querySelector('.placeholder-text');
      if (placeholder) {
        placeholder.remove();
      }

      // Format timestamp
      const time = new Date(timestamp);
      const timeStr = time.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });

      // Format speaker name (shorten if too long)
      const speakerName = speaker || 'Unknown';
      const shortName = speakerName.length > 15 ? speakerName.substring(0, 12) + '...' : speakerName;

      // Create transcript line
      const transcriptLine = document.createElement('div');
      transcriptLine.className = end_of_turn ? 'transcript-line' : 'transcript-line partial';
      transcriptLine.innerHTML = `
        <span class="transcript-timestamp">${timeStr}</span>
        <span class="transcript-speaker" style="color: #60a5fa; font-weight: 600; margin-right: 6px;">${shortName}:</span>
        <span>${textToShow}</span>
      `;

      transcriptContent.appendChild(transcriptLine);

      // Auto-scroll to bottom
      transcriptContent.scrollTop = transcriptContent.scrollHeight;

      // Keep only last 50 lines
      const lines = transcriptContent.querySelectorAll('.transcript-line');
      if (lines.length > 50) {
        lines[0].remove();
      }
    }

    handleAgentUpdate(message) {
      const { agent_name, status, message: statusMessage } = message;

      if (status === 'started') {
        this.addRealtimeInsight(`[Agent] ${agent_name}: ${statusMessage}`);
      } else if (status === 'completed') {
        this.addRealtimeInsight(`[Done] ${agent_name}: Completed`);
      } else if (status === 'error') {
        this.addRealtimeInsight(`[Error] ${agent_name}: ${statusMessage}`);
      }
    }

    handleInsight(message) {
      const { insight_type, title, content, source, priority } = message;

      console.log('Received insight:', insight_type, title);

      // Add to appropriate section based on insight_type
      if (insight_type === 'company_research' || insight_type === 'competitor_research') {
        this.addInsightToSection('Real-time Insights', title, content, priority);
      } else if (insight_type === 'objection_handling') {
        this.addSuggestedResponse(content);
      } else if (insight_type === 'strategy') {
        this.addNextSteps(content);
      } else {
        this.addInsightToSection('Real-time Insights', title, content, priority);
      }
    }

    addRealtimeInsight(text) {
      const overlay = this.getOverlay();
      if (!overlay) return;

      const insightSection = overlay.querySelector('.insight-section .section-content');
      if (!insightSection) return;

      // Remove placeholder if exists
      const placeholder = insightSection.querySelector('.placeholder-text');
      if (placeholder) {
        placeholder.remove();
      }

      // Add new insight
      const insightElement = document.createElement('p');
      insightElement.style.cssText = 'margin: 6px 0; font-size: 12px; padding: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;';
      insightElement.textContent = text;

      insightSection.appendChild(insightElement);

      // Keep only last 5 insights
      const insights = insightSection.querySelectorAll('p');
      if (insights.length > 5) {
        insights[0].remove();
      }
    }

    addInsightToSection(sectionTitle, title, content, priority) {
      const overlay = this.getOverlay();
      if (!overlay) return;

      // Find section by title
      const sections = overlay.querySelectorAll('.insight-section');
      let targetSection = null;

      sections.forEach(section => {
        const sectionTitleEl = section.querySelector('.section-title');
        if (sectionTitleEl && sectionTitleEl.textContent === sectionTitle) {
          targetSection = section.querySelector('.section-content');
        }
      });

      if (!targetSection) return;

      // Remove placeholder
      const placeholder = targetSection.querySelector('.placeholder-text');
      if (placeholder) {
        placeholder.remove();
      }

      // Add insight card
      const card = document.createElement('div');
      card.style.cssText = 'margin: 10px 0; padding: 10px; background: rgba(255, 255, 255, 0.08); border-radius: 8px; border-left: 3px solid rgba(255, 255, 255, 0.4);';

      const priorityColors = {
        high: '#f87171',
        critical: '#dc2626',
        normal: '#60a5fa',
        low: '#94a3b8'
      };

      card.style.borderLeftColor = priorityColors[priority] || priorityColors.normal;

      card.innerHTML = `
        <div style="font-weight: 600; margin-bottom: 6px; font-size: 13px;">${title}</div>
        <div style="font-size: 12px; line-height: 1.5; white-space: pre-wrap;">${content}</div>
      `;

      targetSection.appendChild(card);
    }

    addSuggestedResponse(text) {
      const overlay = this.getOverlay();
      if (!overlay) return;

      const suggestionsList = overlay.querySelector('.suggestions-list');
      if (!suggestionsList) return;

      // Clear placeholder suggestions (check for "Waiting for conversation")
      const existingSuggestions = suggestionsList.querySelectorAll('.suggestion-item');
      if (existingSuggestions.length > 0) {
        const firstSuggestion = existingSuggestions[0].textContent;
        if (firstSuggestion.includes('Waiting for conversation')) {
          suggestionsList.innerHTML = '';
        }
      }

      // Create new suggestion with timestamp
      const suggestionItem = document.createElement('div');
      suggestionItem.className = 'suggestion-item';
      const timestamp = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });

      suggestionItem.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 4px; width: 100%;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="bullet" style="color: #4ade80;">💬</span>
            <span style="font-size: 9px; color: rgba(255,255,255,0.4);">${timestamp}</span>
          </div>
          <span style="font-size: 13px; line-height: 1.5;">${text}</span>
        </div>
      `;

      // Add to top of list (most recent first)
      suggestionsList.insertBefore(suggestionItem, suggestionsList.firstChild);

      // Keep only last 5 suggestions
      const allSuggestions = suggestionsList.querySelectorAll('.suggestion-item');
      if (allSuggestions.length > 5) {
        allSuggestions[allSuggestions.length - 1].remove();
      }

      // Highlight the latest suggestion briefly
      suggestionItem.style.background = 'rgba(74, 222, 128, 0.15)';
      setTimeout(() => {
        suggestionItem.style.background = '';
      }, 3000);
    }

    addNextSteps(text) {
      const overlay = this.getOverlay();
      if (!overlay) return;

      const sections = overlay.querySelectorAll('.insight-section');
      let nextStepsSection = null;

      sections.forEach(section => {
        const sectionTitleEl = section.querySelector('.section-title');
        if (sectionTitleEl && sectionTitleEl.textContent === 'Next Steps') {
          nextStepsSection = section.querySelector('.section-content');
        }
      });

      if (!nextStepsSection) return;

      // Remove placeholder
      const placeholder = nextStepsSection.querySelector('.placeholder-text');
      if (placeholder) {
        placeholder.remove();
      }

      const contentDiv = document.createElement('div');
      contentDiv.style.cssText = 'font-size: 12px; line-height: 1.6; white-space: pre-wrap;';
      contentDiv.textContent = text;

      nextStepsSection.appendChild(contentDiv);
    }

    showNotification(title, message, type = 'info') {
      // Simple notification in console for now
      console.log(`[${type.toUpperCase()}] ${title}: ${message}`);

      // Could add a toast notification to the overlay here
    }

    updateConnectionStatus(connected, errorMessage = '') {
      const overlay = this.getOverlay();
      if (!overlay) return;

      const statusIndicator = overlay.querySelector('.status-indicator');
      const statusText = overlay.querySelector('.status-text');

      if (statusIndicator && statusText) {
        if (connected) {
          statusIndicator.textContent = '●';
          statusIndicator.style.color = '#4ade80';
          statusText.textContent = 'Connected to AI Backend';
        } else {
          statusIndicator.textContent = '●';
          statusIndicator.style.color = '#f87171';
          statusText.textContent = errorMessage || 'Disconnected - Reconnecting...';
        }
      }
    }

    getOverlay() {
      const container = document.getElementById('salesstream-overlay-container');
      if (!container) return null;

      return container.shadowRoot.querySelector('.salesstream-overlay');
    }

    startResearch(myCompanyUrl, targetCompanyUrl) {
      console.log('Starting research - My Company:', myCompanyUrl, '| Target:', targetCompanyUrl);

      this.send({
        type: 'start_research',
        my_company_url: myCompanyUrl,
        target_company_url: targetCompanyUrl
      });

      // Show status in overlay
      const overlay = this.getOverlay();
      if (overlay) {
        const statusText = overlay.querySelector('.status-text');
        if (statusText) {
          statusText.textContent = 'Web crawler active - Researching companies...';
          statusText.style.color = '#60a5fa';
        }
      }
    }
  }

  // Initialize WebSocket Manager
  const wsManager = new WebSocketManager();

  // Connect when overlay is initialized
  setTimeout(() => {
    wsManager.connect();
  }, 1000);

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'START_RESEARCH') {
      wsManager.startResearch(request.myCompanyUrl, request.targetCompanyUrl);
      sendResponse({ success: true });
    } else if (request.type === 'BOT_STARTED') {
      // Show notification in overlay that bot has been started
      const overlay = wsManager.getOverlay();
      if (overlay) {
        const statusText = overlay.querySelector('.status-text');
        if (statusText) {
          statusText.textContent = `Bot Recording (ID: ${request.botId.substring(0, 8)}...)`;
          statusText.style.color = '#4ade80';
        }
      }
      console.log('[SalesStream] Bot started:', request.botId);
      sendResponse({ success: true });
    }
    return true;
  });

  // Keep connection alive with periodic pings
  setInterval(() => {
    if (wsManager.ws && wsManager.ws.readyState === WebSocket.OPEN) {
      wsManager.send({ type: 'ping' });
    }
  }, 30000); // Ping every 30 seconds

})();
