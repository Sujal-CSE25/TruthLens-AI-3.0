export type Language = 'en' | 'hi';

export const translations: Record<Language, Record<string, string>> = {
  en: {
    // Top utility bar
    'gov.title': 'Government of India',
    'gov.hindiTitle': 'भारत सरकार',
    'gov.skip': 'Skip to main content',
    'gov.lang': 'English',
    'gov.selectLang': 'Select language',

    // Header
    'header.ministry': 'Ministry of Home Affairs\nSashastra Seema Bal (SSB)',
    'header.gov': 'Government of India',
    'header.tagline': 'AI-Based Fake Identity & Document Screening System',
    'header.admin': 'TruthLens Admin',
    'header.role': 'Administrator',

    // Navigation
    'nav.home': 'Home',
    'nav.screening': 'Screening',
    'nav.investigations': 'Investigations',
    'nav.forensics': 'Forensics',
    'nav.identity': 'Identity Intelligence',
    'nav.analytics': 'Analytics',
    'nav.audit': 'Audit Trail',
    'nav.about': 'About',

    // System strip
    'strip.dataUpdated': 'DATA UPDATED',
    'strip.nextCycle': 'NEXT AUTO SYNC (DEMO)',
    'strip.dataSources': 'DATA SOURCES',
    'strip.allSynced': 'All Systems Online',
    'strip.region': 'SYSTEM REGION',
    'strip.india': 'India (SSB)',
    'strip.viewFreshness': 'View System Status',
    'strip.syncNotice': 'All screening modules, watchlist databases, and biometric verification services are actively synced as of',
    'strip.operational': '● Fully Operational',

    // Home Page
    'home.heroLabel': 'TRUTHLENS AI 3.0 — SIH 2026',
    'home.heroH1': 'Screen Every Identity.',
    'home.heroH1Highlight': 'Verify Every Signal.',
    'home.heroDesc': 'AI-assisted document verification, tamper detection and biometric analysis for stronger, safer borders.',
    'home.startAnalyzing': 'New Screening',
    'home.watchDemo': 'Watch Demo',
    'home.systemStatus': 'System Status',
    'home.activePipeline': 'All Systems Operational',
    'home.capabilitiesTitle': 'Institutional Capabilities',
    'home.capAgents': 'AI Agents',
    'home.capAgentsSub': 'Specialized Reasoning',
    'home.capSignals': 'Forensic Signals',
    'home.capSignalsSub': 'Multi-Modal Vision & NLP',
    'home.capRAG': 'Evidence Retrieval',
    'home.capRAGSub': 'RAG & Verified Sources',
    'home.capModes': 'Detection Modes',
    'home.capModesSub': 'Text, Images & Documents',

    // Footer
    'footer.tagline': 'AI-Based Fake Identity & Document Screening System',
    'footer.prototype': 'SIH 2026 · PS 26188 · Prototype',

    'footer.aboutCol': 'About',
    'footer.resourcesCol': 'Resources',
    'footer.policiesCol': 'Policies',
    'footer.stayConnected': 'Stay Connected',
    'footer.stayConnectedSub': 'For updates and announcements',
    'footer.copyright': '© 2026 Government of India. All rights reserved.',
    'footer.notice': 'This is a SIH 2026 Prototype. Not for Operational Use.',

    // Detection Page
    'detection.title': 'Content Verification & Forensic Analysis',
    'detection.sub': 'Automated 6-agent verification grounded in forensic signals and verified evidence',
    'detection.tabText': 'Text & News Detection',
    'detection.tabImage': 'Image & Deepfake Detection',

    'detection.presetLabel': 'Quick Test Sample Presets:',
    'detection.presetSelect': 'Select a pre-configured verification sample…',
    'detection.preset1': 'NASA Artemis Mission (Credible Science)',
    'detection.preset2': '5G & Flu False Health Claim (Misinformation)',
    'detection.preset3': 'Manipulated Election Statistics (Political)',
    'detection.preset4': 'Miracle Cancer Cure (Health Misinformation)',
    'detection.textPlaceholder': 'Paste news article, social media post, transcript, or claim here for analysis…',
    'detection.analyzeBtn': 'Verify Content with 6 Agents',
    'detection.analyzeForensicsBtn': 'Run Image & Deepfake Forensics',
    'detection.analyzing': 'Running 6-Agent Verification Pipeline…',
    'detection.analyzingForensics': 'Executing Forensic Signal Decomposition…',

    'detection.dragFile': 'Drag and drop file here, or browse',
    'detection.fileHint': 'Supports images (JPEG, PNG), documents (PDF), or credentials up to 25MB',
    'detection.traceVerified': 'Six-Agent Pipeline Trace Verified',
    'detection.forensicTraceVerified': 'Forensic Signal Pipeline Trace Verified',
    'detection.forensicProgress': 'Forensic Inspection in Progress',
    'detection.forensicSubtitle': 'Executing deep pixel-level ELA, EXIF audit, and noise anomaly decomposition…',
    'detection.verdictFinal': 'Final Verdict',

    'detection.trustScore': 'Trust Score',
    'detection.confidence': 'Confidence',
    'detection.riskLevel': 'Risk Level',
    'detection.trustCredibility': 'Trust Credibility',
    'detection.fakeProbability': 'Fake Probability',
    'detection.signalRadar': 'Risk & Trust Signal Radar',
    'detection.whyVerdict': 'Why did TruthLens reach this verdict?',
    'detection.claimGrounding': 'Claim-Level Verification & Evidence Grounding',
    'detection.linguisticTitle': 'Linguistic & Stylistic Analysis (Text Forensics)',
    'detection.redFlagsTitle': 'Forensic Red Flags & Inconsistencies',
    'detection.newVerification': 'New Verification',

    // Forensics Page
    'forensics.title': 'Document Forensics Inspection Lab',
    'forensics.sub': 'Deep OCR text extraction, layout template completeness, and computational document-forgery forensics',
    'forensics.tabDocument': 'Document Forgery Inspection',
    'forensics.uploadDocument': 'Upload Document for Live Forensic Verification',
    'forensics.runDocBtn': 'Run Document Forensics',
    'forensics.elaTitle': 'Error Level Analysis (ELA)',
    'forensics.exifTitle': 'EXIF Metadata Analysis',
    'forensics.noiseTitle': 'Sensor Noise Pattern Consistency',
    'forensics.nlpTitle': 'Linguistic Signal Decomposition',


    // Dashboard Page
    'dashboard.title': 'Operational Dashboard',
    'dashboard.sub': 'Real-time overview of verification pipeline, continuous learning readiness, and system health',
    'dashboard.total': 'Total Analyses',
    'dashboard.real': 'Real Content',
    'dashboard.fake': 'Fake / Misleading',
    'dashboard.unverified': 'Unverified',
    'dashboard.highRisk': 'High Risk',
    'dashboard.continuousLearning': 'Continuous Learning & Retraining Readiness',
    'dashboard.modalityDist': 'Content Modality Distribution',
    'dashboard.trend30': 'Analysis Volume Trend (30 Days)',
    'dashboard.systemHealth': 'System & Service Health',

    // Analytics Page
    'analytics.title': 'System Analytics',
    'analytics.sub': 'Verification outcomes, risk distribution, evidence retrieval, and agent performance',
    'analytics.verifiedReal': 'Verified Real',
    'analytics.flaggedFake': 'Flagged Fake',
    'analytics.accuracy': 'Feedback Accuracy',
    'analytics.outcomes': 'Verification Outcomes',
    'analytics.riskDist': 'Risk Distribution',
    'analytics.ragCorpus': 'Evidence Retrieval RAG Corpus',
    'analytics.agentPerf': 'Agent Execution Performance',

    // About Page
    'about.title': 'About TruthLens AI 3.0',
    'about.sub': 'SIH 2026 · PS 26188 · Prototype — AI-Based Fake Identity & Document Screening System',
    'about.whatIs': 'What is TruthLens AI 3.0?',

    'about.sixAgentsTitle': 'The Six-Agent Architecture',
    'about.forensicsTitle': 'Dedicated Forensic Tracks',
  },
  hi: {
    // Top utility bar
    'gov.title': 'भारत सरकार',
    'gov.hindiTitle': 'Government of India',
    'gov.skip': 'मुख्य सामग्री पर जाएं',
    'gov.lang': 'हिन्दी',
    'gov.selectLang': 'भाषा चुनें',

    // Header
    'header.ministry': 'गृह मंत्रालय\nसशस्त्र सीमा बल (SSB)',
    'header.gov': 'भारत सरकार',
    'header.tagline': 'एआई-आधारित जाली पहचान एवं दस्तावेज जांच प्रणाली',
    'header.admin': 'ट्रूथ लेंस प्रशासक',
    'header.role': 'प्रशासक',

    // Navigation
    'nav.home': 'मुखपृष्ठ',
    'nav.screening': 'दस्तावेज़ जांच',
    'nav.investigations': 'जांच मामले',
    'nav.forensics': 'फोरेंसिक लैब',
    'nav.identity': 'पहचान आसूचना',
    'nav.analytics': 'विश्लेषण',
    'nav.audit': 'ऑडिट ट्रेल',
    'nav.about': 'परिचय',

    // System strip
    'strip.dataUpdated': 'डेटा अद्यतन (Updated)',
    'strip.nextCycle': 'अगला विश्लेषण चक्र',
    'strip.dataSources': 'डेटा स्रोत',
    'strip.allSynced': 'सभी समन्वित (Synced)',
    'strip.region': 'सिस्टम क्षेत्र',
    'strip.india': 'भारत (India)',
    'strip.viewFreshness': 'डेटा ताज़गी देखें',
    'strip.syncNotice': 'सभी ज्ञान भंडार, भाषाई नियम और निरंतर शिक्षण फ़ीडबैक मॉडल इस समय पूरी तरह समन्वित हैं:',
    'strip.operational': '● पूर्णतः क्रियाशील',

    // Home Page
    'home.heroLabel': 'ट्रूथ लेंस एआई 3.0 — SIH 2026',
    'home.heroH1': 'प्रत्येक पहचान की जांच करें।',
    'home.heroH1Highlight': 'प्रत्येक सिग्नल का सत्यापन करें।',
    'home.heroDesc': 'मजबूत और सुरक्षित सीमाओं के लिए एआई-सहायता प्राप्त दस्तावेज सत्यापन, छेड़छाड़ का पता लगाना और बायोमेट्रिक विश्लेषण।',
    'home.startAnalyzing': 'नया दस्तावेज़ सत्यापन',
    'home.watchDemo': 'डेमो देखें',
    'home.systemStatus': 'सिस्टम स्थिति',
    'home.activePipeline': 'सभी प्रणालियां सक्रिय',
    'home.capabilitiesTitle': 'संस्थागत क्षमताएं',
    'home.capAgents': 'एआई एजेंट्स',
    'home.capAgentsSub': 'विशिष्ट तार्किक विश्लेषण',
    'home.capSignals': 'फोरेंसिक संकेत',
    'home.capSignalsSub': 'मल्टी-मॉडल विज़न और एनएलपी',
    'home.capRAG': 'साक्ष्य पुनर्प्राप्ति',
    'home.capRAGSub': 'सत्यापित स्रोतों से RAG',
    'home.capModes': 'जांच श्रेणियां',
    'home.capModesSub': 'पासपोर्ट, वीजा एवं पहचान पत्र',

    // Footer
    'footer.tagline': 'एआई-आधारित जाली पहचान एवं दस्तावेज जांच प्रणाली',
    'footer.prototype': 'स्मार्ट इंडिया हैकाथॉन 2026 · PS 26188 · प्रोटोटाइप',
    'footer.aboutCol': 'परिचय',

    'footer.resourcesCol': 'संसाधन',
    'footer.policiesCol': 'नीतियां',
    'footer.stayConnected': 'जुड़े रहें',
    'footer.stayConnectedSub': 'अपडेट और घोषणाओं के लिए',
    'footer.copyright': '© 2026 भारत सरकार। सर्वाधिकार सुरक्षित।',
    'footer.notice': 'यह स्मार्ट इंडिया हैकाथॉन 2026 प्रोटोटाइप है। केवल परीक्षण हेतु।',

    // Detection Page
    'detection.title': 'सामग्री सत्यापन एवं फोरेंसिक विश्लेषण',
    'detection.sub': 'फोरेंसिक संकेतों और सत्यापित साक्ष्यों पर आधारित 6-एजेंट स्वचालित सत्यापन प्रणाली',
    'detection.tabText': 'टेक्स्ट एवं समाचार पहचान (Text & News)',
    'detection.tabImage': 'इमेज एवं डीपफेक पहचान (Image & Deepfake)',

    'detection.presetLabel': 'त्वरित परीक्षण नमूने (Presets):',
    'detection.presetSelect': 'एक पूर्व-निर्धारित परीक्षण नमूना चुनें…',
    'detection.preset1': 'नासा आर्टेमिस मिशन (प्रमाणिक वैज्ञानिक तथ्य)',
    'detection.preset2': '5G और फ्लू भ्रामक दावा (स्वास्थ्य संबंधी अफ़वाह)',
    'detection.preset3': 'हेरफेर किए गए चुनावी आंकड़े (राजनीतिक दुष्प्रचार)',
    'detection.preset4': 'चमत्कारी कैंसर उपचार दावा (चिकित्सा भ्रांति)',
    'detection.textPlaceholder': 'विश्लेषण के लिए समाचार, सोशल मीडिया पोस्ट या दावा यहां पेस्ट करें…',
    'detection.analyzeBtn': '6 एजेंटों द्वारा सामग्री सत्यापित करें',
    'detection.analyzeForensicsBtn': 'इमेज एवं डीपफेक फोरेंसिक चलाएं',
    'detection.analyzing': '6-एजेंट सत्यापन पाइपलाइन प्रगति पर है…',
    'detection.analyzingForensics': 'फोरेंसिक सिग्नल विश्लेषण निष्पादित हो रहा है…',

    'detection.dragFile': 'फ़ाइल यहाँ खींचें और छोड़ें, या ब्राउज़ करें',
    'detection.fileHint': 'इमेज (JPEG, PNG), दस्तावेज़ (PDF) या प्रमाण पत्र (25MB तक समर्थित)',
    'detection.traceVerified': 'छह-एजेंट पाइपलाइन निष्पादन सत्यापित',
    'detection.forensicTraceVerified': 'फोरेंसिक संकेत पाइपलाइन निष्पादन सत्यापित',
    'detection.forensicProgress': 'फोरेंसिक निरीक्षण प्रगति पर है',
    'detection.forensicSubtitle': 'गहन पिक्सेल-स्तरीय ELA, EXIF और सेंसर नॉइज़ विश्लेषण जारी है…',
    'detection.verdictFinal': 'अंतिम निर्णय (Final Verdict)',

    'detection.trustScore': 'विश्वास स्कोर',
    'detection.confidence': 'विश्वास स्तर',
    'detection.riskLevel': 'जोखिम स्तर',
    'detection.trustCredibility': 'विश्वसनीयता प्रतिशत',
    'detection.fakeProbability': 'फर्जी होने की संभावना',
    'detection.signalRadar': 'जोखिम एवं विश्वास संकेत रडार',
    'detection.whyVerdict': 'ट्रूथ लेंस इस निर्णय पर क्यों पहुँचा?',
    'detection.claimGrounding': 'दावा-स्तरीय सत्यापन एवं साक्ष्य मिलान',
    'detection.linguisticTitle': 'भाषाई एवं शैलीगत विश्लेषण (टेक्स्ट फोरेंसिक)',
    'detection.redFlagsTitle': 'फोरेंसिक विसंगतियां एवं चेतावनी संकेत',
    'detection.newVerification': 'नया सत्यापन करें',

    // Forensics Page
    'forensics.title': 'दस्तावेज़ फोरेंसिक निरीक्षण प्रयोगशाला',
    'forensics.sub': 'गहन ओसीआर टेक्स्ट निष्कर्षण, टेम्पलेट पूर्णता और दस्तावेज़ जालसाजी फोरेंसिक',
    'forensics.tabDocument': 'दस्तावेज़ जालसाजी निरीक्षण (Document Forgery)',
    'forensics.uploadDocument': 'लाइव फोरेंसिक सत्यापन हेतु दस्तावेज़ अपलोड करें',
    'forensics.runDocBtn': 'दस्तावेज़ फोरेंसिक चलाएं',
    'forensics.elaTitle': 'एरर लेवल एनालिसिस (ELA)',
    'forensics.exifTitle': 'EXIF मेटाडेटा विश्लेषण',

    'forensics.noiseTitle': 'सेंसर नॉइज़ पैटर्न संगति',
    'forensics.nlpTitle': 'भाषाई संकेत विश्लेषण',

    // Dashboard Page
    'dashboard.title': 'परिचालन डैशबोर्ड',
    'dashboard.sub': 'सत्यापन पाइपलाइन, निरंतर शिक्षण तैयारी और सिस्टम स्वास्थ्य का लाइव अवलोकन',
    'dashboard.total': 'कुल विश्लेषण',
    'dashboard.real': 'वास्तविक सामग्री',
    'dashboard.fake': 'फर्जी / भ्रामक',
    'dashboard.unverified': 'असत्यापित',
    'dashboard.highRisk': 'उच्च जोखिम',
    'dashboard.continuousLearning': 'निरंतर शिक्षण एवं पुनः-प्रशिक्षण तैयारी',
    'dashboard.modalityDist': 'सामग्री माध्यम वितरण (Text/Image/Doc)',
    'dashboard.trend30': 'विश्लेषण मात्रा का रुझान (30 दिन)',
    'dashboard.systemHealth': 'सिस्टम एवं सेवा स्वास्थ्य स्थिति',

    // Analytics Page
    'analytics.title': 'सिस्टम विश्लेषण एवं सांख्यिकी',
    'analytics.sub': 'सत्यापन परिणाम, जोखिम वितरण, साक्ष्य पुनर्प्राप्ति और एजेंट प्रदर्शन',
    'analytics.verifiedReal': 'सत्यापित वास्तविक',
    'analytics.flaggedFake': 'चिह्नित फर्जी',
    'analytics.accuracy': 'फ़ीडबैक सटीकता दर',
    'analytics.outcomes': 'सत्यापन परिणाम अनुपात',
    'analytics.riskDist': 'जोखिम वितरण',
    'analytics.ragCorpus': 'साक्ष्य पुनर्प्राप्ति RAG भंडार',
    'analytics.agentPerf': 'एजेंट निष्पादन गति एवं समय',

    // About Page
    'about.title': 'ट्रूथ लेंस एआई 3.0 परिचय',
    'about.sub': 'स्मार्ट इंडिया हैकाथॉन 2026 · PS 26188 · प्रोटोटाइप — एआई-आधारित जाली पहचान एवं दस्तावेज जांच प्रणाली',
    'about.whatIs': 'ट्रूथ लेंस एआई 3.0 क्या है?',

    'about.sixAgentsTitle': 'सिक्स-एजेंट आर्किटेक्चर',
    'about.forensicsTitle': 'समर्पित फोरेंसिक प्रणालियां',
  },
};
