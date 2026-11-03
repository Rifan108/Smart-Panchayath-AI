/**
 * Smart AI Panchayat – Multilingual Voice Assistant Clientside Controller
 * Integrates Web Speech Recognition (STT), SpeechSynthesis (TTS), and Audio playback.
 * Supports: English (en-IN), Kannada (kn-IN), Hindi (hi-IN), Marathi (mr-IN), Malayalam (ml-IN).
 */

(function () {
    let recognition = null;
    let isListening = false;

    const LANG_CODES = {
        'en': 'en-IN',
        'kn': 'kn-IN',
        'hi': 'hi-IN',
        'mr': 'mr-IN',
        'ml': 'ml-IN',
        'ta': 'ta-IN',
        'te': 'te-IN'
    };

    function setNativeValue(element, value) {
        const valueSetter = Object.getOwnPropertyDescriptor(element, 'value')?.set;
        const prototype = Object.getPrototypeOf(element);
        const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
        if (prototypeValueSetter && valueSetter !== prototypeValueSetter) {
            prototypeValueSetter.call(element, value);
        } else if (valueSetter) {
            valueSetter.call(element, value);
        } else {
            element.value = value;
        }
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Web Speech API not supported in this browser. Falling back to text input.");
            return null;
        }

        const rec = new SpeechRecognition();
        rec.continuous = false;
        rec.interimResults = true;
        rec.maxAlternatives = 1;

        rec.onstart = function () {
            isListening = true;
            const micBtn = document.getElementById("assistant-mic-btn");
            const indicator = document.getElementById("assistant-stt-indicator");
            if (micBtn) {
                micBtn.classList.add("btn-danger", "pulse-mic");
                micBtn.classList.remove("btn-outline-primary");
            }
            if (indicator) {
                indicator.classList.remove("d-none");
            }
        };

        rec.onresult = function (event) {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                transcript += event.results[i][0].transcript;
            }
            const inputField = document.getElementById("assistant-text-input");
            if (inputField) {
                setNativeValue(inputField, transcript);
            }
        };

        rec.onerror = function (event) {
            console.warn("Speech recognition error:", event.error);
            stopListening();
        };

        rec.onend = function () {
            stopListening();
            // Automatically trigger send if transcription is present
            const inputField = document.getElementById("assistant-text-input");
            const sendBtn = document.getElementById("assistant-send-btn");
            if (inputField && inputField.value.trim().length > 0 && sendBtn) {
                setTimeout(() => {
                    sendBtn.click();
                }, 300);
            }
        };

        return rec;
    }

    function stopListening() {
        isListening = false;
        const micBtn = document.getElementById("assistant-mic-btn");
        const indicator = document.getElementById("assistant-stt-indicator");
        if (micBtn) {
            micBtn.classList.remove("btn-danger", "pulse-mic");
            micBtn.classList.add("btn-outline-primary");
        }
        if (indicator) {
            indicator.classList.add("d-none");
        }
    }

    // Attach click listeners on DOM load
    document.addEventListener("DOMContentLoaded", function () {
        document.addEventListener("click", function (e) {
            // Mic button toggle
            if (e.target && (e.target.id === "assistant-mic-btn" || e.target.closest("#assistant-mic-btn"))) {
                if (!recognition) {
                    recognition = initSpeechRecognition();
                }
                if (!recognition) {
                    alert("Speech recognition is not supported in this browser. Please use Google Chrome or Edge.");
                    return;
                }

                if (isListening) {
                    recognition.stop();
                } else {
                    const langSelector = document.getElementById("assistant-lang-selector");
                    const langCode = langSelector ? (langSelector.value || "en") : "en";
                    recognition.lang = LANG_CODES[langCode] || "en-IN";
                    try {
                        recognition.start();
                    } catch (err) {
                        console.warn("Recognition start error:", err);
                    }
                }
            }
        });
    });
})();

