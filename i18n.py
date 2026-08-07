"""
i18n.py
Lightweight translation layer for Civic Sense AI.

Design:
- All *internal* identifiers (nav section ids, status values, category
  keys stored in the DB, session_state keys) stay in English — only the
  text a citizen actually reads on screen gets translated.
- `t(key)` looks up `key` in the dictionary for the currently selected
  language (`st.session_state.lang_code`), falling back to English if
  the key or language is missing, and finally to the key itself so a
  missing translation never crashes the page.
- `set_language_selector()` renders the picker and is safe to call from
  both the logged-out (login/register) view and the logged-in sidebar.
"""

import streamlit as st

LANGUAGES = {
    "en": "English",
    "hi": "हिंदी",
    "mr": "मराठी",
    "gu": "ગુજરાતી",
}

_TRANSLATIONS = {
    # ---------------- Nav ----------------
    "nav_home":      {"en": "🏠 Home", "hi": "🏠 होम", "mr": "🏠 मुख्यपृष्ठ", "gu": "🏠 હોમ"},
    "nav_report":    {"en": "📝 Report Incident", "hi": "📝 शिकायत दर्ज करें", "mr": "📝 तक्रार नोंदवा", "gu": "📝 ફરિયાદ નોંધાવો"},
    "nav_map":       {"en": "🗺️ Incident Map", "hi": "🗺️ घटना मानचित्र", "mr": "🗺️ घटना नकाशा", "gu": "🗺️ ઘટના નકશો"},
    "nav_my_reports":{"en": "📄 My Reports", "hi": "📄 मेरी शिकायतें", "mr": "📄 माझ्या तक्रारी", "gu": "📄 મારી ફરિયાદો"},
    "nav_assistant": {"en": "🤖 AI Assistant", "hi": "🤖 एआई सहायक", "mr": "🤖 एआय सहाय्यक", "gu": "🤖 એઆઈ સહાયક"},
    "nav_admin":     {"en": "📊 Admin Dashboard", "hi": "📊 एडमिन डैशबोर्ड", "mr": "📊 प्रशासक डॅशबोर्ड", "gu": "📊 એડમિન ડેશબોર્ડ"},
    "language_label": {"en": "🌐 Language", "hi": "🌐 भाषा", "mr": "🌐 भाषा", "gu": "🌐 ભાષા"},
    "logout": {"en": "🚪 Log out", "hi": "🚪 लॉग आउट", "mr": "🚪 लॉग आउट", "gu": "🚪 લૉગ આઉટ"},

    # ---------------- Home ----------------
    "home_welcome": {"en": "Welcome back, <b>{name}</b> — signed in as {role}.",
                      "hi": "वापसी पर स्वागत है, <b>{name}</b> — {role} के रूप में साइन इन।",
                      "mr": "पुन्हा स्वागत आहे, <b>{name}</b> — {role} म्हणून साइन इन.",
                      "gu": "ફરી સ્વાગત છે, <b>{name}</b> — {role} તરીકે સાઇન ઇન."},
    "role_admin": {"en": "Administrator", "hi": "प्रशासक", "mr": "प्रशासक", "gu": "એડમિનિસ્ટ્રેટર"},
    "role_citizen": {"en": "Citizen", "hi": "नागरिक", "mr": "नागरिक", "gu": "નાગરિક"},
    "home_what_todo": {"en": "#### What would you like to do?", "hi": "#### आप क्या करना चाहेंगे?",
                        "mr": "#### तुम्हाला काय करायचे आहे?", "gu": "#### તમે શું કરવા માંગો છો?"},
    "card_report_title": {"en": "Report Incident", "hi": "शिकायत दर्ज करें", "mr": "तक्रार नोंदवा", "gu": "ફરિયાદ નોંધાવો"},
    "card_report_desc": {"en": "File a new civic issue with AI-suggested category & priority.",
                          "hi": "एआई-सुझाई गई श्रेणी और प्राथमिकता के साथ नई नागरिक समस्या दर्ज करें।",
                          "mr": "एआय-सुचवलेल्या श्रेणी आणि प्राधान्यक्रमासह नवीन नागरी समस्या नोंदवा.",
                          "gu": "એઆઈ-સૂચિત શ્રેણી અને પ્રાથમિકતા સાથે નવો નાગરિક મુદ્દો નોંધાવો."},
    "card_map_title": {"en": "Incident Map", "hi": "घटना मानचित्र", "mr": "घटना नकाशा", "gu": "ઘટના નકશો"},
    "card_map_desc": {"en": "See every reported issue plotted live, color-coded by status.",
                       "hi": "स्थिति के अनुसार रंग-कोडित, हर दर्ज समस्या को लाइव मानचित्र पर देखें।",
                       "mr": "स्थितीनुसार रंग-कोडित, नोंदवलेली प्रत्येक समस्या थेट नकाशावर पहा.",
                       "gu": "સ્થિતિ પ્રમાણે રંગ-કોડેડ, દરેક નોંધાયેલ મુદ્દો લાઇવ નકશા પર જુઓ."},
    "card_my_reports_title": {"en": "My Reports", "hi": "मेरी शिकायतें", "mr": "माझ्या तक्रारी", "gu": "મારી ફરિયાદો"},
    "card_my_reports_desc": {"en": "Track the status of every issue you've personally reported.",
                              "hi": "आपके द्वारा दर्ज हर समस्या की स्थिति ट्रैक करें।",
                              "mr": "तुम्ही नोंदवलेल्या प्रत्येक समस्येची स्थिती ट्रॅक करा.",
                              "gu": "તમે નોંધાવેલા દરેક મુદ્દાની સ્થિતિ ટ્રૅક કરો."},
    "card_assistant_title": {"en": "AI Assistant", "hi": "एआई सहायक", "mr": "एआय सहाय्यक", "gu": "એઆઈ સહાયક"},
    "card_assistant_desc": {"en": "Ask how to report, track, or resolve a civic concern.",
                             "hi": "नागरिक समस्या को दर्ज, ट्रैक या हल करने का तरीका पूछें।",
                             "mr": "नागरी समस्या नोंदवण्याबद्दल, ट्रॅक करण्याबद्दल किंवा सोडवण्याबद्दल विचारा.",
                             "gu": "નાગરિક મુદ્દો કેવી રીતે નોંધાવવો, ટ્રૅક કરવો કે ઉકેલવો તે પૂછો."},
    "card_admin_title": {"en": "Admin Dashboard", "hi": "एडमिन डैशबोर्ड", "mr": "प्रशासक डॅशबोर्ड", "gu": "એડમિન ડેશબોર્ડ"},
    "card_admin_desc": {"en": "Review stats and manage every incident in the system.",
                         "hi": "आंकड़े देखें और सिस्टम की हर घटना प्रबंधित करें।",
                         "mr": "आकडेवारी पहा आणि प्रणालीतील प्रत्येक घटना व्यवस्थापित करा.",
                         "gu": "આંકડા જુઓ અને સિસ્ટમની દરેક ઘટના મેનેજ કરો."},
    "btn_open_report": {"en": "Open Report Incident", "hi": "शिकायत दर्ज करें खोलें", "mr": "तक्रार नोंदवा उघडा", "gu": "ફરિયાદ નોંધાવો ખોલો"},
    "btn_open_map": {"en": "Open Incident Map", "hi": "घटना मानचित्र खोलें", "mr": "घटना नकाशा उघडा", "gu": "ઘટના નકશો ખોલો"},
    "btn_open_my_reports": {"en": "Open My Reports", "hi": "मेरी शिकायतें खोलें", "mr": "माझ्या तक्रारी उघडा", "gu": "મારી ફરિયાદો ખોલો"},
    "btn_open_assistant": {"en": "Open AI Assistant", "hi": "एआई सहायक खोलें", "mr": "एआय सहाय्यक उघडा", "gu": "એઆઈ સહાયક ખોલો"},
    "btn_open_admin": {"en": "Open Admin Dashboard", "hi": "एडमिन डैशबोर्ड खोलें", "mr": "प्रशासक डॅशबोर्ड उघडा", "gu": "એડમિન ડેશબોર્ડ ખોલો"},

    # ---------------- Login / Register ----------------
    "hero_title": {"en": "🏙️ Civic Sense AI", "hi": "🏙️ सिविक सेंस एआई", "mr": "🏙️ सिव्हिक सेन्स एआय", "gu": "🏙️ સિવિક સેન્સ એઆઈ"},
    "hero_subtitle_logged_out": {
        "en": "Report civic issues, track them on a live map, and get instant AI-powered guidance.",
        "hi": "नागरिक समस्याओं की रिपोर्ट करें, उन्हें लाइव मानचित्र पर ट्रैक करें, और तुरंत एआई-संचालित मार्गदर्शन पाएं।",
        "mr": "नागरी समस्यांची तक्रार करा, त्या थेट नकाशावर ट्रॅक करा आणि त्वरित एआय-आधारित मार्गदर्शन मिळवा.",
        "gu": "નાગરિક મુદ્દાઓ નોંધાવો, તેમને લાઇવ નકશા પર ટ્રૅક કરો અને તરત જ એઆઈ-સંચાલિત માર્ગદર્શન મેળવો.",
    },
    "eyebrow_community": {"en": "Community Reporting Platform", "hi": "सामुदायिक रिपोर्टिंग प्लेटफ़ॉर्म",
                           "mr": "सामुदायिक तक्रार व्यासपीठ", "gu": "સામુદાયિક રિપોર્ટિંગ પ્લેટફોર્મ"},
    "feat_report_title": {"en": "Report", "hi": "रिपोर्ट करें", "mr": "तक्रार करा", "gu": "ફરિયાદ કરો"},
    "feat_report_desc": {"en": "Flag potholes, garbage, water logging & more in seconds.",
                          "hi": "गड्ढे, कचरा, जलभराव आदि को सेकंडों में फ़्लैग करें।",
                          "mr": "खड्डे, कचरा, पाणी साचणे इत्यादी काही सेकंदात नोंदवा.",
                          "gu": "ખાડા, કચરો, પાણી ભરાવો વગેરે સેકંડોમાં ફ્લેગ કરો."},
    "feat_track_title": {"en": "Track", "hi": "ट्रैक करें", "mr": "ट्रॅक करा", "gu": "ટ્રૅક કરો"},
    "feat_track_desc": {"en": "Watch issues move from Pending to Resolved on the map.",
                         "hi": "मानचित्र पर समस्याओं को लंबित से हल तक जाते देखें।",
                         "mr": "नकाशावर समस्या प्रलंबित ते निकाली अशा हलताना पहा.",
                         "gu": "નકશા પર મુદ્દાઓને પેન્ડિંગથી ઉકેલાયેલા થતા જુઓ."},
    "feat_help_title": {"en": "Get Help", "hi": "मदद पाएं", "mr": "मदत मिळवा", "gu": "મદદ મેળવો"},
    "feat_help_desc": {"en": "Ask the AI Assistant anything about civic reporting.",
                        "hi": "नागरिक रिपोर्टिंग के बारे में एआई सहायक से कुछ भी पूछें।",
                        "mr": "नागरी तक्रारींबद्दल एआय सहाय्यकाला काहीही विचारा.",
                        "gu": "નાગરિક રિપોર્ટિંગ વિશે એઆઈ સહાયકને કંઈપણ પૂછો."},
    "tab_login": {"en": "🔑  Login", "hi": "🔑  लॉगिन", "mr": "🔑  लॉगिन", "gu": "🔑  લૉગિન"},
    "tab_register": {"en": "🆕  Register", "hi": "🆕  पंजीकरण करें", "mr": "🆕  नोंदणी करा", "gu": "🆕  રજિસ્ટર કરો"},
    "username": {"en": "Username", "hi": "उपयोगकर्ता नाम", "mr": "वापरकर्तानाव", "gu": "વપરાશકર્તા નામ"},
    "password": {"en": "Password", "hi": "पासवर्ड", "mr": "पासवर्ड", "gu": "પાસવર્ડ"},
    "login_btn": {"en": "Log in", "hi": "लॉग इन करें", "mr": "लॉग इन करा", "gu": "લૉગ ઇન કરો"},
    "login_error": {"en": "Invalid username or password.", "hi": "अमान्य उपयोगकर्ता नाम या पासवर्ड।",
                     "mr": "अवैध वापरकर्तानाव किंवा पासवर्ड.", "gu": "અમાન્ય વપરાશકર્તા નામ અથવા પાસવર્ડ."},
    "demo_creds": {"en": "💡 Demo credentials", "hi": "💡 डेमो लॉगिन जानकारी", "mr": "💡 डेमो लॉगिन माहिती", "gu": "💡 ડેમો લૉગિન વિગતો"},
    "choose_username": {"en": "Choose a username", "hi": "उपयोगकर्ता नाम चुनें", "mr": "वापरकर्तानाव निवडा", "gu": "વપરાશકર્તા નામ પસંદ કરો"},
    "email": {"en": "Email", "hi": "ईमेल", "mr": "ईमेल", "gu": "ઈમેલ"},
    "choose_password": {"en": "Choose a password", "hi": "पासवर्ड चुनें", "mr": "पासवर्ड निवडा", "gu": "પાસવર્ડ પસંદ કરો"},
    "confirm_password": {"en": "Confirm password", "hi": "पासवर्ड की पुष्टि करें", "mr": "पासवर्डची पुष्टी करा", "gu": "પાસવર્ડની પુષ્ટિ કરો"},
    "create_account": {"en": "Create account", "hi": "खाता बनाएं", "mr": "खाते तयार करा", "gu": "ખાતું બનાવો"},
    "register_required": {"en": "Username and password are required.", "hi": "उपयोगकर्ता नाम और पासवर्ड आवश्यक हैं।",
                           "mr": "वापरकर्तानाव आणि पासवर्ड आवश्यक आहेत.", "gu": "વપરાશકર્તા નામ અને પાસવર્ડ જરૂરી છે."},
    "register_mismatch": {"en": "Passwords do not match.", "hi": "पासवर्ड मेल नहीं खाते।",
                           "mr": "पासवर्ड जुळत नाहीत.", "gu": "પાસવર્ડ મેળ ખાતા નથી."},
    "register_success_suffix": {"en": " You can now log in from the Login tab.",
                                 "hi": " अब आप लॉगिन टैब से लॉगिन कर सकते हैं।",
                                 "mr": " आता तुम्ही लॉगिन टॅबवरून लॉगिन करू शकता.",
                                 "gu": " હવે તમે લૉગિન ટૅબમાંથી લૉગિન કરી શકો છો."},

    # ---------------- Report Incident ----------------
    "report_hero_title": {"en": "📝 Report a Civic Incident", "hi": "📝 नागरिक शिकायत दर्ज करें",
                           "mr": "📝 नागरी तक्रार नोंदवा", "gu": "📝 નાગરિક ફરિયાદ નોંધાવો"},
    "report_hero_subtitle": {"en": "Describe the issue — our AI will suggest a category and priority automatically.",
                              "hi": "समस्या का वर्णन करें — हमारा एआई अपने आप श्रेणी और प्राथमिकता सुझाएगा।",
                              "mr": "समस्येचे वर्णन करा — आमचा एआय आपोआप श्रेणी आणि प्राधान्यक्रम सुचवेल.",
                              "gu": "મુદ્દાનું વર્ણન કરો — અમારું એઆઈ આપમેળે શ્રેણી અને પ્રાથમિકતા સૂચવશે."},
    "eyebrow_new_report": {"en": "New Report", "hi": "नई शिकायत", "mr": "नवीन तक्रार", "gu": "નવી ફરિયાદ"},
    "past_reports_pointer": {
        "en": "📄 Want to see your past reports and their status? Visit **My Reports** in the sidebar.",
        "hi": "📄 अपनी पिछली शिकायतें और उनकी स्थिति देखना चाहते हैं? साइडबार में **मेरी शिकायतें** पर जाएं।",
        "mr": "📄 तुमच्या मागील तक्रारी आणि त्यांची स्थिती पहायची आहे? साइडबारमध्ये **माझ्या तक्रारी** ला भेट द्या.",
        "gu": "📄 તમારી અગાઉની ફરિયાદો અને તેમની સ્થિતિ જોવી છે? સાઇડબારમાં **મારી ફરિયાદો** ની મુલાકાત લો.",
    },

    # ---------------- My Reports ----------------
    "my_reports_hero_title": {"en": "📄 My Reports", "hi": "📄 मेरी शिकायतें", "mr": "📄 माझ्या तक्रारी", "gu": "📄 મારી ફરિયાદો"},
    "my_reports_hero_subtitle": {
        "en": "Every civic issue you've reported, and where it stands right now.",
        "hi": "आपके द्वारा दर्ज हर नागरिक समस्या, और उसकी वर्तमान स्थिति।",
        "mr": "तुम्ही नोंदवलेली प्रत्येक नागरी समस्या, आणि सध्याची तिची स्थिती.",
        "gu": "તમે નોંધાવેલ દરેક નાગરિક મુદ્દો, અને તેની હાલની સ્થિતિ.",
    },
    "eyebrow_your_activity": {"en": "Your Activity", "hi": "आपकी गतिविधि", "mr": "तुमची क्रियाकलाप", "gu": "તમારી પ્રવૃત્તિ"},
    "no_reports_yet": {"en": "You haven't reported any incidents yet. Head to **Report Incident** to file your first one!",
                        "hi": "आपने अभी तक कोई शिकायत दर्ज नहीं की है। अपनी पहली शिकायत दर्ज करने के लिए **शिकायत दर्ज करें** पर जाएं!",
                        "mr": "तुम्ही अद्याप कोणतीही तक्रार नोंदवलेली नाही. तुमची पहिली तक्रार नोंदवण्यासाठी **तक्रार नोंदवा** वर जा!",
                        "gu": "તમે હજુ સુધી કોઈ ફરિયાદ નોંધાવી નથી. તમારી પહેલી ફરિયાદ નોંધાવવા **ફરિયાદ નોંધાવો** પર જાઓ!"},
    "filter_status": {"en": "Filter by status", "hi": "स्थिति के अनुसार फ़िल्टर करें", "mr": "स्थितीनुसार फिल्टर करा", "gu": "સ્થિતિ પ્રમાણે ફિલ્ટર કરો"},
    "filter_category": {"en": "Filter by category", "hi": "श्रेणी के अनुसार फ़िल्टर करें", "mr": "श्रेणीनुसार फिल्टर करा", "gu": "શ્રેણી પ્રમાણે ફિલ્ટર કરો"},
    "no_match_filters": {"en": "No reports match the selected filters.", "hi": "चयनित फ़िल्टर से कोई शिकायत मेल नहीं खाती।",
                          "mr": "निवडलेल्या फिल्टरशी कोणतीही तक्रार जुळत नाही.", "gu": "પસંદ કરેલા ફિલ્ટર સાથે કોઈ ફરિયાદ મેળ ખાતી નથી."},

    # ---------------- Incident Map ----------------
    "map_hero_title": {"en": "🗺️ Incident Map", "hi": "🗺️ घटना मानचित्र", "mr": "🗺️ घटना नकाशा", "gu": "🗺️ ઘટના નકશો"},
    "map_hero_subtitle": {"en": "All civic issues reported by citizens, plotted by location.",
                           "hi": "नागरिकों द्वारा दर्ज सभी नागरिक समस्याएं, स्थान के अनुसार अंकित।",
                           "mr": "नागरिकांनी नोंदवलेल्या सर्व नागरी समस्या, स्थानानुसार दर्शवलेल्या.",
                           "gu": "નાગરિકો દ્વારા નોંધાયેલા તમામ નાગરિક મુદ્દા, સ્થાન પ્રમાણે દર્શાવેલા."},
    "eyebrow_live_overview": {"en": "Live Overview", "hi": "लाइव अवलोकन", "mr": "थेट आढावा", "gu": "લાઇવ ઓવરવ્યૂ"},
    "map_view_toggle": {"en": "Map view", "hi": "मानचित्र दृश्य", "mr": "नकाशा दृश्य", "gu": "નકશા દૃશ્ય"},
    "map_view_street": {"en": "🗺️ Street", "hi": "🗺️ सड़क दृश्य", "mr": "🗺️ रस्ता दृश्य", "gu": "🗺️ સ્ટ્રીટ"},
    "map_view_satellite": {"en": "🛰️ Satellite", "hi": "🛰️ उपग्रह दृश्य", "mr": "🛰️ उपग्रह दृश्य", "gu": "🛰️ સેટેલાઇટ"},
    "no_incidents_filters": {"en": "No incidents match the selected filters.", "hi": "चयनित फ़िल्टर से कोई घटना मेल नहीं खाती।",
                              "mr": "निवडलेल्या फिल्टरशी कोणतीही घटना जुळत नाही.", "gu": "પસંદ કરેલા ફિલ્ટર સાથે કોઈ ઘટના મેળ ખાતી નથી."},
    "incident_list": {"en": "#### 📋 Incident List", "hi": "#### 📋 घटना सूची", "mr": "#### 📋 घटना यादी", "gu": "#### 📋 ઘટના યાદી"},

    # ---------------- Assistant ----------------
    "assistant_hero_title": {"en": "🤖 Civic Sense AI Assistant", "hi": "🤖 सिविक सेंस एआई सहायक",
                              "mr": "🤖 सिव्हिक सेन्स एआय सहाय्यक", "gu": "🤖 સિવિક સેન્સ એઆઈ સહાયક"},
    "assistant_hero_subtitle": {
        "en": "Ask about reporting issues, tracking complaints, or general civic responsibility.",
        "hi": "समस्याएं दर्ज करने, शिकायतें ट्रैक करने, या सामान्य नागरिक जिम्मेदारी के बारे में पूछें।",
        "mr": "समस्या नोंदवण्याबद्दल, तक्रारी ट्रॅक करण्याबद्दल किंवा सर्वसाधारण नागरी जबाबदारीबद्दल विचारा.",
        "gu": "મુદ્દા નોંધાવવા, ફરિયાદો ટ્રૅક કરવા અથવા સામાન્ય નાગરિક જવાબદારી વિશે પૂછો.",
    },
    "eyebrow_always_online": {"en": "Always Online", "hi": "हमेशा उपलब्ध", "mr": "नेहमी उपलब्ध", "gu": "હંમેશા ઓનલાઇન"},

    # ---------------- Admin ----------------
    "admin_hero_title": {"en": "📊 Admin Dashboard", "hi": "📊 एडमिन डैशबोर्ड", "mr": "📊 प्रशासक डॅशबोर्ड", "gu": "📊 એડમિન ડેશબોર્ડ"},
    "admin_hero_subtitle": {"en": "Overview and management of all reported civic incidents.",
                             "hi": "सभी दर्ज नागरिक घटनाओं का अवलोकन और प्रबंधन।",
                             "mr": "नोंदवलेल्या सर्व नागरी घटनांचा आढावा आणि व्यवस्थापन.",
                             "gu": "તમામ નોંધાયેલ નાગરિક ઘટનાઓની ઝાંખી અને સંચાલન."},
}


def t(key: str, **kwargs) -> str:
    """Translate `key` into the currently selected language, with `{placeholders}`
    filled in from kwargs. Falls back to English, then to the raw key."""
    lang = st.session_state.get("lang_code", "en")
    entry = _TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry.get("en") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def init_language():
    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "en"


def language_selector(key="lang_code_widget"):
    """Renders a selectbox that drives st.session_state.lang_code directly
    (the widget's own key IS the language state, so no manual sync needed)."""
    codes = list(LANGUAGES.keys())
    current = st.session_state.get("lang_code", "en")
    index = codes.index(current) if current in codes else 0
    choice = st.selectbox(
        t("language_label"),
        codes,
        index=index,
        format_func=lambda c: LANGUAGES[c],
        key=key,
    )
    st.session_state.lang_code = choice
