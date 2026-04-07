// Popup script for SalesStream extension

document.addEventListener('DOMContentLoaded', function() {
  const myCompanyUrlInput = document.getElementById('myCompanyUrl');
  const targetCompanyUrlInput = document.getElementById('targetCompanyUrl');
  const startResearchBtn = document.getElementById('startResearch');
  const statusMessage = document.getElementById('statusMessage');
  const startBotBtn = document.getElementById('startBot');
  const botStatusMessage = document.getElementById('botStatusMessage');

  // Load saved data
  chrome.storage.local.get(['myCompanyUrl', 'targetCompanyUrl'], function(data) {
    if (data.myCompanyUrl) {
      myCompanyUrlInput.value = data.myCompanyUrl;
    }
    if (data.targetCompanyUrl) {
      targetCompanyUrlInput.value = data.targetCompanyUrl;
    }
  });

  startResearchBtn.addEventListener('click', function() {
    const myCompanyUrl = myCompanyUrlInput.value.trim();
    const targetCompanyUrl = targetCompanyUrlInput.value.trim();

    // Validation
    if (!myCompanyUrl && !targetCompanyUrl) {
      showStatus('Please enter at least one company URL', 'error');
      return;
    }

    // Validate URL formats
    try {
      if (myCompanyUrl) new URL(myCompanyUrl);
      if (targetCompanyUrl) new URL(targetCompanyUrl);
    } catch (e) {
      showStatus('Please enter valid URLs (include https://)', 'error');
      return;
    }

    // Save to storage
    chrome.storage.local.set({
      myCompanyUrl: myCompanyUrl,
      targetCompanyUrl: targetCompanyUrl
    });

    // Show loading status
    showStatus('Starting web crawler and AI analysis...', 'info');
    startResearchBtn.disabled = true;
    startResearchBtn.textContent = 'Researching...';

    // Send message to content script
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs[0]) {
        const currentTab = tabs[0];

        // Check if we're on a Google Meet page
        if (!currentTab.url || !currentTab.url.includes('meet.google.com/')) {
          startResearchBtn.disabled = false;
          startResearchBtn.textContent = 'Start Research';
          showStatus('Please open a Google Meet page first!', 'error');
          return;
        }

        console.log('Sending START_RESEARCH message to content script');

        chrome.tabs.sendMessage(currentTab.id, {
          type: 'START_RESEARCH',
          myCompanyUrl: myCompanyUrl,
          targetCompanyUrl: targetCompanyUrl
        }, function(response) {
          // Re-enable button
          startResearchBtn.disabled = false;
          startResearchBtn.textContent = 'Start Research';

          if (chrome.runtime.lastError) {
            console.error('Chrome runtime error:', chrome.runtime.lastError);
            showStatus('Extension needs reload! Go to chrome://extensions/', 'error');
          } else if (response && response.success) {
            showStatus('Research started! Watch the overlay for insights', 'success');
          } else {
            console.error('Unexpected response:', response);
            showStatus('Failed to start research', 'error');
          }
        });
      } else {
        startResearchBtn.disabled = false;
        startResearchBtn.textContent = 'Start Research';
        showStatus('No active tab found', 'error');
      }
    });
  });

  function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';

    // Hide after 3 seconds
    setTimeout(() => {
      statusMessage.style.display = 'none';
    }, 3000);
  }

  function showBotStatus(message, type) {
    botStatusMessage.textContent = message;
    botStatusMessage.className = `status-message ${type}`;
    botStatusMessage.style.display = 'block';

    // Hide after 5 seconds
    setTimeout(() => {
      botStatusMessage.style.display = 'none';
    }, 5000);
  }

  // ============================================================================
  // Bot Creation Handler
  // ============================================================================

  startBotBtn.addEventListener('click', async function() {
    // Disable button to prevent double-clicks
    startBotBtn.disabled = true;
    startBotBtn.textContent = 'Starting Bot...';

    try {
      // Get the current active tab
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });

      if (!tabs[0]) {
        showBotStatus('No active tab found', 'error');
        return;
      }

      const currentTab = tabs[0];
      const meetingUrl = currentTab.url;

      // Check if we're on a Google Meet page
      if (!meetingUrl || !meetingUrl.includes('meet.google.com/')) {
        showBotStatus('Please open a Google Meet page first!', 'error');
        return;
      }

      // Extract the meeting code from the URL
      const meetingMatch = meetingUrl.match(/meet\.google\.com\/([a-z\-]+)/);
      if (!meetingMatch) {
        showBotStatus('Invalid Google Meet URL', 'error');
        return;
      }

      showBotStatus('Creating bot for meeting...', 'info');

      // Call the backend API to start the bot
      const backendUrl = 'http://localhost:8000';

      console.log('Creating bot for URL:', meetingUrl);

      const response = await fetch(`${backendUrl}/api/meetstream/start-bot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          meeting_url: meetingUrl,
          bot_name: 'Meetstream AI Transcriber',
          video_required: true
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('API Error:', errorData);
        throw new Error(errorData.detail || `HTTP ${response.status}: Failed to start bot`);
      }

      const result = await response.json();
      console.log('Bot started successfully:', result);

      showBotStatus(`Bot started! ID: ${result.bot_id.substring(0, 8)}...`, 'success');

      // Notify the content script
      chrome.tabs.sendMessage(currentTab.id, {
        type: 'BOT_STARTED',
        botId: result.bot_id,
        meetingUrl: meetingUrl
      });

    } catch (error) {
      console.error('Error starting bot:', error);
      showBotStatus(error.message || 'Failed to start bot. Check backend!', 'error');
    } finally {
      // Re-enable button
      startBotBtn.disabled = false;
      startBotBtn.textContent = 'Start Recording Bot';
    }
  });
});
