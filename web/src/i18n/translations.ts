export type LanguageCode = "en" | "hi" | "or" | "pa";

export interface TranslationDictionary {
  appName: string;
  tagline: string;
  navHome: string;
  navChat: string;
  navDiseases: string;
  navVaccination: string;
  navAlerts: string;
  navFacilities: string;
  navAbout: string;
  navAdmin: string;
  chatPlaceholder: string;
  send: string;
  clear: string;
  listening: string;
  speakTooltip: string;
  readAloudTooltip: string;
  stopAudioTooltip: string;
  quickQuestionsTitle: string;
  sourcesTitle: string;
  verifiedOfficialSources: string;
  disclaimer: string;
  emergencyAlert: string;
  emergencyCallNow: string;
  depthBasic: string;
  depthGood: string;
  depthDeep: string;
  depthBasicDesc: string;
  depthGoodDesc: string;
  depthDeepDesc: string;
  demoDataBanner: string;
  sampleFacilitiesBanner: string;
  searchDiseasesPlaceholder: string;
  allCategories: string;
  infectious: string;
  maternalChild: string;
  nonCommunicable: string;
  environmental: string;
  vaccinesDueTitle: string;
  supplementsTitle: string;
  agePickerLabel: string;
  showAllAges: string;
  feedbackHelpful: string;
  feedbackNotHelpful: string;
  feedbackSubmitted: string;
  adminTitle: string;
  adminEnterToken: string;
  adminVerify: string;
  adminNoFeedback: string;
  errorGeneric: string;
  errorRateLimit: string;
  errorOffline: string;
}

export const translations: Record<LanguageCode, TranslationDictionary> = {
  en: {
    appName: "Swasthya Setu",
    tagline: "Verified public-health awareness assistant for rural & semi-urban India",
    navHome: "Home",
    navChat: "Chat",
    navDiseases: "Diseases",
    navVaccination: "Vaccines",
    navAlerts: "Outbreak Alerts",
    navFacilities: "Find Facilities",
    navAbout: "About & Sources",
    navAdmin: "Admin",
    chatPlaceholder: "Ask about symptoms, prevention, or vaccine schedules...",
    send: "Send",
    clear: "Clear Chat",
    listening: "Listening... speak now",
    speakTooltip: "Voice input (Speak in Hindi or English)",
    readAloudTooltip: "Read answer aloud",
    stopAudioTooltip: "Stop audio",
    quickQuestionsTitle: "Quick awareness questions:",
    sourcesTitle: "Verified Official Sources",
    verifiedOfficialSources: "Source documents and citations for this response",
    disclaimer: "Health awareness only, not medical advice. We never prescribe doses or medicines. In an emergency, call 108.",
    emergencyAlert: "Possible Medical Emergency. Do not wait for an online answer.",
    emergencyCallNow: "Call 108 Emergency Helpline",
    depthBasic: "Basic",
    depthGood: "Good",
    depthDeep: "Deep",
    depthBasicDesc: "Backed by official WHO fact sheet (<30 chunks).",
    depthGoodDesc: "Backed by national guidelines and fact sheets (30–150 chunks).",
    depthDeepDesc: "Backed by comprehensive multi-document national manuals (>150 chunks).",
    demoDataBanner: "DEMO DATA ONLY - Not a live alert. For active official disease surveillance in India, consult IDSP at idsp.nic.in.",
    sampleFacilitiesBanner: "SAMPLE DATA ONLY - For demonstration. In a medical emergency, call 108 or go to your nearest government hospital.",
    searchDiseasesPlaceholder: "Search 30 covered diseases or topics...",
    allCategories: "All Categories",
    infectious: "Infectious Diseases",
    maternalChild: "Maternal & Child Health",
    nonCommunicable: "Non-Communicable Conditions",
    environmental: "Environmental & First Aid",
    vaccinesDueTitle: "Vaccines Due",
    supplementsTitle: "Nutritional Supplements (Not Vaccines)",
    agePickerLabel: "Filter by age:",
    showAllAges: "All milestones (Birth to 16 Years)",
    feedbackHelpful: "Helpful",
    feedbackNotHelpful: "Not helpful",
    feedbackSubmitted: "Thank you for your feedback!",
    adminTitle: "Admin Feedback Dashboard",
    adminEnterToken: "Enter Admin Secret Token:",
    adminVerify: "Access Feedback",
    adminNoFeedback: "No feedback records found yet.",
    errorGeneric: "Something went wrong. Please check your connection and try again.",
    errorRateLimit: "Rate limit reached. Please wait a moment before sending another query.",
    errorOffline: "Health assistant server is offline or unreachable. Please verify server connection.",
  },
  hi: {
    appName: "स्वास्थ्य सेतु",
    tagline: "ग्रामीण और अर्ध-शहरी भारत के लिए सत्यापित स्वास्थ्य जागरूकता सहायक",
    navHome: "होम",
    navChat: "चैट",
    navDiseases: "बीमारियां",
    navVaccination: "टीकाकरण",
    navAlerts: "प्रकोप अलर्ट",
    navFacilities: "स्वास्थ्य केंद्र खोजें",
    navAbout: "बारे में व स्रोत",
    navAdmin: "प्रशासन",
    chatPlaceholder: "लक्षण, रोकथाम या टीकाकरण के बारे में सवाल पूछें...",
    send: "भेजें",
    clear: "चैट साफ करें",
    listening: "सुन रहे हैं... बोलिए",
    speakTooltip: "माइक से बोलकर पूछें",
    readAloudTooltip: "उत्तर सुनकर समझें",
    stopAudioTooltip: "आवाज बंद करें",
    quickQuestionsTitle: "त्वरित जागरूकता प्रश्न:",
    sourcesTitle: "सत्यापित आधिकारिक स्रोत",
    verifiedOfficialSources: "इस उत्तर के लिए आधिकारिक संदर्भ व पृष्ठ",
    disclaimer: "यह स्वास्थ्य जागरूकता की जानकारी है, चिकित्सा सलाह नहीं। आपातकाल में नजदीकी अस्पताल जाएँ या 108 पर कॉल करें।",
    emergencyAlert: "यह आपातकाल हो सकता है। ऑनलाइन जवाब का इंतजार न करें।",
    emergencyCallNow: "तुरंत 108 हेल्पलाइन पर कॉल करें",
    depthBasic: "प्राथमिक",
    depthGood: "अच्छा",
    depthDeep: "विस्तृत",
    depthBasicDesc: "WHO तथ्य-पत्रक आधारित जानकारी (<30 अंश)।",
    depthGoodDesc: "राष्ट्रीय दिशानिर्देशों व तथ्य-पत्रकों पर आधारित (30–150 अंश)।",
    depthDeepDesc: "विस्तृत राष्ट्रीय उपचार पुस्तिकाओं पर आधारित (>150 अंश)।",
    demoDataBanner: "केवल डेमो डेटा - यह लाइव अलर्ट नहीं है। आधिकारिक निगरानी के लिए IDSP (idsp.nic.in) देखें।",
    sampleFacilitiesBanner: "नमूना सुविधा डेटा - आपातकाल में तुरंत नजदीकी अस्पताल जाएँ या 108 पर कॉल करें।",
    searchDiseasesPlaceholder: "30 बीमारियों या स्वास्थ्य विषयों में खोजें...",
    allCategories: "सभी श्रेणियां",
    infectious: "संक्रामक रोग",
    maternalChild: "मातृ एवं शिशु स्वास्थ्य",
    nonCommunicable: "गैर-संचारी रोग",
    environmental: "पर्यावरण व प्राथमिक उपचार",
    vaccinesDueTitle: "देय टीके",
    supplementsTitle: "पूरक आहार / सप्लीमेंट (यह टीका नहीं है)",
    agePickerLabel: "उम्र अनुसार चुनें:",
    showAllAges: "सभी आयु वर्ग (जन्म से 16 वर्ष)",
    feedbackHelpful: "मददगार",
    feedbackNotHelpful: "मददगार नहीं",
    feedbackSubmitted: "आपकी प्रतिक्रिया के लिए धन्यवाद!",
    adminTitle: "प्रशासनिक प्रतिक्रिया डैशबोर्ड",
    adminEnterToken: "एडमिन सीक्रेट टोकन दर्ज करें:",
    adminVerify: "प्रतिक्रिया देखें",
    adminNoFeedback: "अभी तक कोई प्रतिक्रिया दर्ज नहीं हुई है।",
    errorGeneric: "कुछ गड़बड़ हुई। कृपया इंटरनेट कनेक्शन जांचें और पुनः प्रयास करें।",
    errorRateLimit: "अनुरोध सीमा पूरी हो गई। कृपया थोड़ा इंतजार करें।",
    errorOffline: "स्वास्थ्य सहायक सर्वर अनुपलब्ध है। कृपया कनेक्शन जांचें।",
  },
  or: {
    appName: "ସ୍ୱାସ୍ଥ୍ୟ ସେତୁ",
    tagline: "ଗ୍ରାମୀଣ ଏବଂ ଅର୍ଦ୍ଧ-ସହରୀ ଭାରତ ପାଇଁ ସ୍ୱାସ୍ଥ୍ୟ ସଚେତନତା ସହାୟକ",
    navHome: "ମୁଖ୍ୟ ପୃଷ୍ଠା",
    navChat: "ଚାଟ୍",
    navDiseases: "ରୋଗ",
    navVaccination: "ଟୀକାକରଣ",
    navAlerts: "ରୋଗ ସତର୍କତା",
    navFacilities: "ଡାକ୍ତରଖାନା ଖୋଜନ୍ତୁ",
    navAbout: "ବିଷୟରେ ଓ ସୂତ୍ର",
    navAdmin: "ପ୍ରଶାସନ",
    chatPlaceholder: "ଲକ୍ଷଣ, ନିରାକରଣ କିମ୍ବା ଟୀକା ସୂଚୀ ବିଷୟରେ ପଚାରନ୍ତୁ...",
    send: "ପଠାନ୍ତୁ",
    clear: "ସଫା କରନ୍ତୁ",
    listening: "ଶୁଣୁଛି... କୁହନ୍ତୁ",
    speakTooltip: "ଭଏସ୍ ଇନପୁଟ୍",
    readAloudTooltip: "ଉତ୍ତର ଶୁଣନ୍ତୁ",
    stopAudioTooltip: "ବନ୍ଦ କରନ୍ତୁ",
    quickQuestionsTitle: "ପଚାରିବା ପ୍ରଶ୍ନ:",
    sourcesTitle: "ସତ୍ୟାପିତ ସରକାରୀ ସୂତ୍ର",
    verifiedOfficialSources: "ଅଧିକାରିକ ସୂତ୍ର ଏବଂ ପୃଷ୍ଠା",
    disclaimer: "ଏହା କେବଳ ସଚେତନତା ପାଇଁ, ଚିକିତ୍ସା ପରାମର୍ଶ ନୁହେଁ। ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତିରେ ୧୦୮ କଲ୍ କରନ୍ତୁ।",
    emergencyAlert: "ଏହା ଜରୁରୀକାଳୀନ ହୋଇପାରେ। ତୁରନ୍ତ ଡାକ୍ତରଖାନା ଯାଆନ୍ତୁ।",
    emergencyCallNow: "୧୦୮ ରେ କଲ୍ କରନ୍ତୁ",
    depthBasic: "ପ୍ରାଥମିକ",
    depthGood: "ଭଲ",
    depthDeep: "ଗଭୀର",
    depthBasicDesc: "WHO ତଥ୍ୟ ଆଧାରିତ।",
    depthGoodDesc: "ଜାତୀୟ ନିର୍ଦ୍ଦେଶାବଳୀ ଆଧାରିତ।",
    depthDeepDesc: "ବିସ୍ତୃତ ପୁସ୍ତିକା ଆଧାରିତ।",
    demoDataBanner: "କେବଳ ଡେମୋ ଡାଟା - ଲାଇଭ୍ ଆଲର୍ଟ ନୁହେଁ। idsp.nic.in ଦେଖନ୍ତୁ।",
    sampleFacilitiesBanner: "ନମୁନା ଡାଟା - ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତିରେ ୧୦୮ ଡାକନ୍ତୁ।",
    searchDiseasesPlaceholder: "ରୋଗ ଖୋଜନ୍ତୁ...",
    allCategories: "ସମସ୍ତ ଶ୍ରେଣୀ",
    infectious: "ସଂକ୍ରାମକ ରୋଗ",
    maternalChild: "ମାତୃ ଓ ଶିଶୁ ସ୍ୱାସ୍ଥ୍ୟ",
    nonCommunicable: "ଅସଂକ୍ରାମକ ରୋଗ",
    environmental: "ପରିବେଶ ଓ ପ୍ରାଥମିକ ଚିକିତ୍ସା",
    vaccinesDueTitle: "ଦିଆଯିବାକୁ ଥିବା ଟୀକା",
    supplementsTitle: "ପୋଷକ ତତ୍ତ୍ୱ (ଟୀକା ନୁହେଁ)",
    agePickerLabel: "ବୟସ ଅନୁସାରେ:",
    showAllAges: "ସମସ୍ତ ବୟସ",
    feedbackHelpful: "ଉପଯୋଗୀ",
    feedbackNotHelpful: "ଉପଯୋଗୀ ନୁହେଁ",
    feedbackSubmitted: "ଧନ୍ୟବାଦ!",
    adminTitle: "ପ୍ରଶାସନ ଡ୍ୟାସବୋର୍ଡ",
    adminEnterToken: "ଟୋକେନ୍ ଦିଅନ୍ତୁ:",
    adminVerify: "ଯାଞ୍ଚ କରନ୍ତୁ",
    adminNoFeedback: "କୌଣସି ରେକର୍ଡ ନାହିଁ।",
    errorGeneric: "ତ୍ରୁଟି ଘଟିଲା। ପୁନଃ ଚେଷ୍ଟା କରନ୍ତୁ।",
    errorRateLimit: "ଦୟାକରି କିଛି ସମୟ ଅପେକ୍ଷା କରନ୍ତୁ।",
    errorOffline: "ସର୍ଭର ସଂଯୋଗ ବିଫଳ।",
  },
  pa: {
    appName: "ਸਵਸਥਿਆ ਸੇਤੂ",
    tagline: "ਪੇਂਡੂ ਅਤੇ ਅਰਧ-ਸ਼ਹਿਰੀ ਭਾਰਤ ਲਈ ਪ੍ਰਮਾਣਿਤ ਸਿਹਤ ਜਾਗਰੂਕਤਾ ਸਹਾਇਕ",
    navHome: "ਮੁੱਖ ਪੰਨਾ",
    navChat: "ਗੱਲਬਾਤ",
    navDiseases: "ਬਿਮਾਰੀਆਂ",
    navVaccination: "ਟੀਕਾਕਰਨ",
    navAlerts: "ਚੇਤਾਵਨੀਆਂ",
    navFacilities: "ਸਿਹਤ ਕੇਂਦਰ",
    navAbout: "ਬਾਰੇ ਅਤੇ ਸਰੋਤ",
    navAdmin: "ਪ੍ਰਸ਼ਾਸਨ",
    chatPlaceholder: "ਲੱਛਣ, ਬਚਾਅ ਜਾਂ ਟੀਕਾਕਰਨ ਬਾਰੇ ਸਵਾਲ ਪੁੱਛੋ...",
    send: "ਭੇਜੋ",
    clear: "ਚੈਟ ਸਾਫ਼ ਕਰੋ",
    listening: "ਸੁਣ ਰਿਹਾ ਹਾਂ... ਬੋਲੋ",
    speakTooltip: "ਆਵਾਜ਼ ਨਾਲ ਪੁੱਛੋ",
    readAloudTooltip: "ਉੱਤਰ ਸੁਣੋ",
    stopAudioTooltip: "ਆਵਾਜ਼ ਬੰਦ ਕਰੋ",
    quickQuestionsTitle: "ਤੁਰੰਤ ਸਵਾਲ:",
    sourcesTitle: "ਪ੍ਰਮਾਣਿਤ ਸਰਕਾਰੀ ਸਰੋਤ",
    verifiedOfficialSources: "ਅਧਿਕਾਰਤ ਦਸਤਾਵੇਜ਼ ਅਤੇ ਸਰੋਤ",
    disclaimer: "ਇਹ ਕੇਵਲ ਸਿਹਤ ਜਾਗਰੂਕਤਾ ਲਈ ਹੈ, ਡਾਕਟਰੀ ਸਲਾਹ ਨਹੀਂ। ਐਮਰਜੈਂਸੀ ਵਿੱਚ 108 ਤੇ ਕਾਲ ਕਰੋ।",
    emergencyAlert: "ਇਹ ਐਮਰਜੈਂਸੀ ਹੋ ਸਕਦੀ ਹੈ। ਤੁਰੰਤ ਹਸਪਤਾਲ ਜਾਓ।",
    emergencyCallNow: "108 ਹੈਲਪਲਾਈਨ ਤੇ ਕਾਲ ਕਰੋ",
    depthBasic: "ਬੁਨਿਆਦੀ",
    depthGood: "ਚੰਗਾ",
    depthDeep: "ਵਿਸਥਾਰਪੂਰਵਕ",
    depthBasicDesc: "WHO ਤੱਥ-ਪੱਤਰ ਆਧਾਰਿਤ (<30 ਅੰਸ਼)।",
    depthGoodDesc: "ਰਾਸ਼ਟਰੀ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼ਾਂ ਆਧਾਰਿਤ (30–150 ਅੰਸ਼)।",
    depthDeepDesc: "ਵਿਸਥਾਰਪੂਰਵਕ ਮੈਨੂਅਲ ਆਧਾਰਿਤ (>150 ਅੰਸ਼)।",
    demoDataBanner: "ਕੇਵਲ ਡੈਮੋ ਡਾਟਾ - ਲਾਈਵ ਚੇਤਾਵਨੀ ਨਹੀਂ ਹੈ। idsp.nic.in ਦੇਖੋ।",
    sampleFacilitiesBanner: "ਨਮੂਨਾ ਡਾਟਾ - ਐਮਰਜੈਂਸੀ ਵਿੱਚ 108 ਤੇ ਕਾਲ ਕਰੋ।",
    searchDiseasesPlaceholder: "ਬਿਮਾਰੀਆਂ ਖੋਜੋ...",
    allCategories: "ਸਭ ਸ਼੍ਰੇਣੀਆਂ",
    infectious: "ਛੂਤ ਦੀਆਂ ਬਿਮਾਰੀਆਂ",
    maternalChild: "ਮਾਂ ਅਤੇ ਬੱਚੇ ਦੀ ਸਿਹਤ",
    nonCommunicable: "ਗ਼ੈਰ-ਸੰਚਾਰੀ ਬਿਮਾਰੀਆਂ",
    environmental: "ਵਾਤਾਵਰਣ ਅਤੇ ਮੁੱਢਲੀ ਸਹਾਇਤਾ",
    vaccinesDueTitle: "ਜ਼ਰੂਰੀ ਟੀਕੇ",
    supplementsTitle: "ਸਪਲੀਮੈਂਟ (ਟੀਕਾ ਨਹੀਂ ਹੈ)",
    agePickerLabel: "ਉਮਰ ਚੁਣੋ:",
    showAllAges: "ਸਾਰੀਆਂ ਉਮਰਾਂ",
    feedbackHelpful: "ਮਦਦਗਾਰ",
    feedbackNotHelpful: "ਮਦਦਗਾਰ ਨਹੀਂ",
    feedbackSubmitted: "ਧੰਨਵਾਦ!",
    adminTitle: "ਪ੍ਰਸ਼ਾਸਨ ਡੈਸ਼ਬੋਰਡ",
    adminEnterToken: "ਟੋਕਨ ਦਾਖਲ ਕਰੋ:",
    adminVerify: "ਜਾਂਚ ਕਰੋ",
    adminNoFeedback: "ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ।",
    errorGeneric: "ਕੁਝ ਗੜਬੜ ਹੋ ਗਈ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
    errorRateLimit: "ਕਿਰਪਾ ਕਰਕੇ ਥੋੜ੍ਹਾ ਇੰਤਜ਼ਾਰ ਕਰੋ।",
    errorOffline: "ਸਰਵਰ ਨਾਲ ਸੰਪਰਕ ਨਹੀਂ ਹੋ ਰਿਹਾ।",
  },
};

