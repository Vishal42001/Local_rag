
function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Stop any previous speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        // Try to pick a decent voice
        const voices = window.speechSynthesis.getVoices();
        const preferred = voices.find(v => v.name.includes('Google US English')) || voices[0];
        if (preferred) utterance.voice = preferred;

        window.speechSynthesis.speak(utterance);
    } else {
        alert("Text-to-Speech not supported in this browser.");
    }
}

// Global listener for Streamlit events is tricky, so we attach to window for manual triggering
window.speakLastResponse = function () {
    // Find the last assistant message in the DOM (hacky but works for Streamlit)
    const elements = document.querySelectorAll('.chat-message-bot');
    if (elements.length > 0) {
        const lastText = elements[elements.length - 1].innerText;
        speakText(lastText);
    } else {
        console.log("No text found to read.");
    }
}
