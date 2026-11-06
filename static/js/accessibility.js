/**
 * CivicCare - Multi-Lingual Citizen Accessibility Helper
 * Supports: English ('en'), Kannada ('kn'), Hindi ('hi')
 * Strict Isolation: No mixed languages inside any string.
 */

const CivicAccessibility = {
  recognition: null,
  isRecording: false,

  getCurrentLanguage: function() {
    const langInput = document.getElementById('inputLanguage');
    if (langInput && langInput.value) return langInput.value;
    if (window.currentLang) return window.currentLang;
    const htmlLang = document.documentElement.lang;
    if (htmlLang && (htmlLang === 'kn' || htmlLang === 'hi')) return htmlLang;
    return 'en';
  },

  // Initialize Speech-to-Text Voice Dictation
  initVoiceInput: function(options) {
    const btn = document.getElementById(options.buttonId);
    const target = document.getElementById(options.targetInputId);
    const status = document.getElementById(options.statusId);
    const langSelect = document.getElementById(options.langSelectId);

    if (!btn || !target) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      if (status) {
        status.innerHTML = '<span class="text-muted"><i class="bi bi-info-circle me-1"></i>Voice typing requires Chrome, Edge or Safari.</span>';
      }
      btn.addEventListener('click', function() {
        alert("Speech recognition is supported on Google Chrome, Microsoft Edge, and Safari. You can also type directly or tap the 1-click problem buttons.");
      });
      return;
    }

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;

    btn.addEventListener('click', () => {
      if (this.isRecording) {
        rec.stop();
        return;
      }

      const lang = (langSelect && langSelect.value) ? langSelect.value : this.getCurrentLanguage();
      if (lang === 'kn') {
        rec.lang = 'kn-IN';
      } else if (lang === 'hi') {
        rec.lang = 'hi-IN';
      } else {
        rec.lang = 'en-IN';
      }

      try {
        rec.start();
        this.isRecording = true;
        btn.classList.remove('btn-outline-success');
        btn.classList.add('btn-danger', 'animate-pulse');

        if (lang === 'kn') {
          btn.innerHTML = '<span class="recording-pulse me-1"></span> <strong>ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇವೆ...</strong>';
          if (status) {
            status.style.display = 'block';
            status.innerHTML = '<span class="text-danger fw-bold"><i class="bi bi-mic-fill me-1"></i>ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ</span>';
          }
        } else if (lang === 'hi') {
          btn.innerHTML = '<span class="recording-pulse me-1"></span> <strong>सुन रहे हैं... बोलें</strong>';
          if (status) {
            status.style.display = 'block';
            status.innerHTML = '<span class="text-danger fw-bold"><i class="bi bi-mic-fill me-1"></i>कृपया अपनी समस्या स्पष्ट रूप से बोलें</span>';
          }
        } else {
          btn.innerHTML = '<span class="recording-pulse me-1"></span> <strong>Listening... Speak now</strong>';
          if (status) {
            status.style.display = 'block';
            status.innerHTML = '<span class="text-danger fw-bold"><i class="bi bi-mic-fill me-1"></i>Please speak your problem clearly into the microphone</span>';
          }
        }
      } catch (err) {
        console.warn("[Voice] Start error:", err);
      }
    });

    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const lang = (langSelect && langSelect.value) ? langSelect.value : this.getCurrentLanguage();
      if (transcript) {
        const existing = target.value.trim();
        target.value = existing ? existing + " " + transcript : transcript;
        target.dispatchEvent(new Event('input', { bubbles: true }));

        if (status) {
          let msg = '<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i>Speech transcribed successfully!</span>';
          if (lang === 'kn') {
            msg = '<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i>ಮಾತು ಯಶಸ್ವಿಯಾಗಿ ದಾಖಲಾಗಿದೆ!</span>';
          } else if (lang === 'hi') {
            msg = '<span class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i>आवाज सफलतापूर्वक दर्ज हो गई!</span>';
          }
          status.innerHTML = msg;
          setTimeout(() => { status.style.display = 'none'; }, 4000);
        }
      }
    };

    rec.onerror = (event) => {
      console.warn("[Voice] Error:", event.error);
      const lang = (langSelect && langSelect.value) ? langSelect.value : this.getCurrentLanguage();
      if (status) {
        let msg = '<span class="text-warning"><i class="bi bi-exclamation-triangle me-1"></i>Could not hear audio. Please try again.</span>';
        if (lang === 'kn') {
          msg = '<span class="text-warning"><i class="bi bi-exclamation-triangle me-1"></i>ಧ್ವನಿ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.</span>';
        } else if (lang === 'hi') {
          msg = '<span class="text-warning"><i class="bi bi-exclamation-triangle me-1"></i>आवाज सुनाई नहीं दी। कृपया दोबारा प्रयास करें।</span>';
        }
        status.innerHTML = msg;
      }
      this.resetVoiceBtn(btn);
    };

    rec.onend = () => {
      this.resetVoiceBtn(btn);
    };
  },

  resetVoiceBtn: function(btn) {
    this.isRecording = false;
    btn.classList.remove('btn-danger', 'animate-pulse');
    btn.classList.add('btn-outline-success');
    const lang = this.getCurrentLanguage();
    if (lang === 'kn') {
      btn.innerHTML = '<i class="bi bi-mic-fill me-1 text-success"></i> <strong>ಮಾತನಾಡಿ</strong>';
    } else if (lang === 'hi') {
      btn.innerHTML = '<i class="bi bi-mic-fill me-1 text-success"></i> <strong>बोलकर बताएं</strong>';
    } else {
      btn.innerHTML = '<i class="bi bi-mic-fill me-1 text-success"></i> <strong>Speak Problem</strong>';
    }
  },

  // Text-to-Speech Spoken Audio Instructions
  speakText: function(text, lang) {
    if (!window.speechSynthesis) {
      alert("Text-to-speech is not supported on this device.");
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    const targetLang = lang || this.getCurrentLanguage();
    if (targetLang === 'kn') {
      utterance.lang = 'kn-IN';
    } else if (targetLang === 'hi') {
      utterance.lang = 'hi-IN';
    } else {
      utterance.lang = 'en-IN';
    }

    window.speechSynthesis.speak(utterance);
  },

  // 1-Tap Quick Problem Presets
  selectQuickProblem: function(type, langOverride) {
    const titleInput = document.getElementById('inputTitle');
    const descInput = document.getElementById('inputDescription');
    const catSelect = document.getElementById('selectCategory');

    if (!titleInput || !descInput) return;

    const lang = langOverride || this.getCurrentLanguage();

    const presets = {
      pothole: {
        en: {
          title: "Dangerous road pothole causing vehicle accidents",
          desc: "Deep asphalt crater pothole on the main road causing severe accident risk for vehicles and pedestrians. Requires urgent resurfacing."
        },
        kn: {
          title: "ರಸ್ತೆಯಲ್ಲಿ ಅಪಾಯಕಾರಿ ಗುಂಡಿ ಬಿದ್ದಿದೆ",
          desc: "ಮುಖ್ಯ ರಸ್ತೆಯಲ್ಲಿ ಆಳವಾದ ಗುಂಡಿ ಬಿದ್ದಿದ್ದು ದ್ವಿಚಕ್ರ ವಾಹನಗಳು ಮತ್ತು ಜನರು ಬೀಳುವ ಅಪಾಯವಿದೆ. ದಯವಿಟ್ಟು ತಕ್ಷಣ ಡಾಂಬರು ಹಾಕಿ ಸರಿಪಡಿಸಿ."
        },
        hi: {
          title: "सड़क पर खतरनाक गड्ढा है जिससे दुर्घटना का खतरा बना हुआ है",
          desc: "मुख्य सड़क पर गहरा गड्ढा बन गया है जिससे वाहन दुर्घटनाग्रस्त हो रहे हैं और पैदल यात्रियों को खतरा है। कृपया शीघ्र डामर डालकर सड़क की मरम्मत करें।"
        },
        category: "Road Damage"
      },
      water_leak: {
        en: {
          title: "Drinking water supply pipeline burst gushing water",
          desc: "Municipal potable water pipeline fractured and gushing clean drinking water onto street. Residents facing acute water shortage."
        },
        kn: {
          title: "ಕುಡಿಯುವ ನೀರಿನ ಪೈಪ್ ಒಡೆದು ನೀರು ಪೋಲಾಗುತ್ತಿದೆ",
          desc: "ಕುಡಿಯುವ ನೀರಿನ ಮುಖ್ಯ ಪೈಪ್ ಒಡೆದು ರಸ್ತೆಯಲ್ಲಿ ನೀರು ಹರಿಯುತ್ತಿದೆ. ಸಾರ್ವಜನಿಕರಿಗೆ ಕುಡಿಯುವ ನೀರಿನ ಕೊರತೆಯಾಗಿದೆ. ತಕ್ಷಣ ದುರಸ್ತಿ ಮಾಡಿ."
        },
        hi: {
          title: "पीने के पानी की पाइपलाइन टूटी और पानी बर्बाद हो रहा है",
          desc: "पीने के पानी की मुख्य पाइपलाइन टूट गई है जिससे भारी मात्रा में स्वच्छ जल सड़क पर बह रहा है और इलाके में पानी की किल्लत हो गई है। कृपया तुरंत मरम्मत करें।"
        },
        category: "Water Leakage"
      },
      garbage: {
        en: {
          title: "Uncollected garbage heap and overflowing bins",
          desc: "Massive pile of rotting uncollected solid garbage and overflowing community bins causing foul odor and health hazard."
        },
        kn: {
          title: "ಕಸದ ತೊಟ್ಟಿ ತುಂಬಿ ಗಬ್ಬು ನಾರುತ್ತಿದೆ",
          desc: "ಸಾರ್ವಜನಿಕ ರಸ್ತೆ ಬದಿಯಲ್ಲಿ ಕಸದ ರಾಶಿ ಬಿದ್ದಿದ್ದು, ತೀವ್ರ ದುರ್ವಾಸನೆ ಬರುತ್ತಿದೆ ಮತ್ತು ನಾಯಿಗಳು, ಹಂದಿಗಳು ಕಸವನ್ನು ಹರಡುತ್ತಿವೆ."
        },
        hi: {
          title: "कचरे का बड़ा ढेर और ओवरफ्लो डस्टबिन",
          desc: "सड़क किनारे कचरे का बड़ा ढेर लगा हुआ है जिससे तेज दुर्गंध आ रही है और मक्खी-मच्छरों से बीमारियां फैलने का गंभीर खतरा है। कृपया कचरा तुरंत उठवाएं।"
        },
        category: "Garbage Collection"
      },
      streetlight: {
        en: {
          title: "Streetlights completely dark and not functioning",
          desc: "All streetlights in this corridor are dark and non-operational at night, creating severe accident and safety hazard for residents."
        },
        kn: {
          title: "ಬೀದಿ ದೀಪಗಳು ಉರಿಯುತ್ತಿಲ್ಲ, ಕತ್ತಲೆಯಾಗಿದೆ",
          desc: "ಈ ರಸ್ತೆಯಲ್ಲಿ ಎಲ್ಲಾ ಬೀದಿ ದೀಪಗಳು ಕೆಟ್ಟಿದ್ದು ರಾತ್ರಿ ವೇಳೆ ಕತ್ತಲೆಯಾಗಿದೆ. ಮಹಿಳೆಯರು ಮತ್ತು ಮಕ್ಕಳಿಗೆ ಸಂಚರಿಸಲು ತುಂಬಾ ತೊಂದರೆಯಾಗಿದೆ."
        },
        hi: {
          title: "स्ट्रीट लाइट बंद है और पूरी सड़क पर अंधेरा है",
          desc: "इस मुख्य मार्ग की सभी स्ट्रीट लाइटें बंद हैं जिससे रात में गहरा अंधेरा छाया रहता है और सुरक्षा का खतरा बना हुआ है। कृपया नई लाइटें लगाकर इसे चालू करें।"
        },
        category: "Streetlight Failure"
      },
      drainage: {
        en: {
          title: "Stormwater drain blocked and open manhole hazard",
          desc: "Stormwater drain clogged with sediment and plastic waste causing black sewage backflow and open manhole falling hazard."
        },
        kn: {
          title: "ಚರಂಡಿ ಬಂದ್ ಆಗಿ ಕೊಳಚೆ ನೀರು ರಸ್ತೆಯಲ್ಲಿ ಹರಿಯುತ್ತಿದೆ",
          desc: "ಚರಂಡಿಯಲ್ಲಿ ಹೂಳು ತುಂಬಿ ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯುತ್ತಿಲ್ಲ. ಕೊಳಚೆ ನೀರು ರಸ್ತೆಗೆ ನುಗ್ಗಿದೆ ಮತ್ತು ಮ್ಯಾನ್‌ಹೋಲ್ ಮುಚ್ಚಳ ತೆರೆದಿದೆ."
        },
        hi: {
          title: "नाली जाम और खुला मैनहोल खतरा",
          desc: "नाली में कचरा और गाद भर जाने से गंदा सीवेज का पानी सड़क पर बह रहा है तथा मैनहोल का ढक्कन खुला है जिससे जानलेवा खतरा है। कृपया तत्काल सफाई करवाएं।"
        },
        category: "Drainage Problems"
      },
      infra: {
        en: {
          title: "Broken public footpath slab and park amenity damaged",
          desc: "Pedestrian footpath concrete slabs damaged and public seating vandalized creating walking hazard for senior citizens."
        },
        kn: {
          title: "ಸಾರ್ವಜನಿಕ ಫುಟ್‌ಪಾತ್ / ಪಾರ್ಕ್ ಆಸ್ತಿ ಹಾನಿಯಾಗಿದೆ",
          desc: "ಪಾದಚಾರಿ ರಸ್ತೆಯ ಕಾಂಕ್ರೀಟ್ ಸ್ಲ್ಯಾಬ್ ಒಡೆದು ಅಪಾಯಕಾರಿಯಾಗಿದೆ. ಸಾರ್ವಜನಿಕರ ಹಿತದೃಷ್ಟಿಯಿಂದ ದುರಸ್ತಿ ಮಾಡಿ."
        },
        hi: {
          title: "सार्वजनिक फुटपाथ और पार्क संपत्ति क्षतिग्रस्त",
          desc: "पैदल चलने वाले फुटपाथ की टाइलें और स्लैब टूट गए हैं जिससे वरिष्ठ नागरिकों और पैदल यात्रियों के गिरने का खतरा है। कृपया शीघ्र मरम्मत कराएं।"
        },
        category: "Public Infrastructure Damage"
      }
    };

    const item = presets[type];
    if (item) {
      const data = item[lang] || item['en'];
      titleInput.value = data.title;
      descInput.value = data.desc;
      if (catSelect) {
        catSelect.value = item.category;
      }

      document.querySelectorAll('.quick-problem-card').forEach(c => c.classList.remove('active-problem-card'));
      const activeCard = document.getElementById('quickCard_' + type);
      if (activeCard) activeCard.classList.add('active-problem-card');

      titleInput.dispatchEvent(new Event('input', { bubbles: true }));
      descInput.dispatchEvent(new Event('input', { bubbles: true }));

      titleInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
};

window.CivicAccessibility = CivicAccessibility;
