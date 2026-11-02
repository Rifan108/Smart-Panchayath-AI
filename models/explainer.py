"""
OpenAI-Powered Explainer Module
Generates intelligent, contextual, bilingual (English + Malayalam) explanations
for sector prioritization using GPT-3.5-turbo (cheapest OpenAI model).

Falls back to a template-based explanation if the API is unavailable.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, OPENAI_MODEL, SECTOR_INDICATORS, ENABLE_OPENAI_EXPLANATIONS

# ─── Lazy import OpenAI ────────────────────────────────────────────────────────
def _get_openai_client():
    try:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        return None


# ─── Readable label mapping with full multi-language support ──────────────────
FEATURE_LABELS_I18N = {
    "disease_incidence_rate": {
        "en": "Disease Incidence Rate",
        "ml": "രോഗ ബാധിത നിരക്ക്",
        "kn": "ರೋಗ ಪ್ರಮಾಣ",
        "ta": "நோய் பாதிப்பு விகிதம்",
        "te": "వ్యాధి సంభావ్యత రేటు",
        "mr": "रोग प्रादुर्भाव दर",
    },
    "hospital_beds_per_1000": {
        "en": "Hospital Beds per 1,000 Residents",
        "ml": "ആശുപത്രി കിടക്കകൾ (1,000 പേർക്ക്)",
        "kn": "ಆಸ್ಪತ್ರೆ ಹಾಸಿಗೆಗಳು (1,000 ಜನರಿಗೆ)",
        "ta": "மருத்துவமனை படுக்கைகள் (1,000 பேருக்கு)",
        "te": "ఆసుపత్రి పడకలు (1,000 మందికి)",
        "mr": "रुग्णालय खाटा (दर 1,000 लोकांमागे)",
    },
    "doctor_patient_ratio": {
        "en": "Doctor-Patient Ratio",
        "ml": "ഡോക്ടർ-രോഗി അനുപാതം",
        "kn": "ವೈದ್ಯ-ರೋಗಿ ಅನುಪಾತ",
        "ta": "மருத்துவர்-நோயாளி விகிதம்",
        "te": "వైద్యుల-రోగుల నిష్పత్తి",
        "mr": "डॉक्टर-रुग्ण प्रमाण",
    },
    "infant_mortality_rate": {
        "en": "Infant Mortality Rate",
        "ml": "ശിശുമരണ നിരക്ക്",
        "kn": "ಶಿಶು ಮರಣ ಪ್ರಮಾಣ",
        "ta": "சிசு இறப்பு விகிதம்",
        "te": "శిశు మరణాల రేటు",
        "mr": "बालमृत्यू दर",
    },
    "vaccination_coverage_pct": {
        "en": "Vaccination Coverage %",
        "ml": "വാക്സിനേഷൻ കവറേജ് %",
        "kn": "ಲಸಿಕೆ ವ್ಯಾಪ್ತಿ %",
        "ta": "தடுப்பூசி பாதுகாப்பு %",
        "te": "టీకా రక్షణ %",
        "mr": "लसीकरण व्याप्ती %",
    },
    "literacy_rate": {
        "en": "Literacy Rate",
        "ml": "സാക്ഷരതാ നിരക്ക്",
        "kn": "ಸಾಕ್ಷರತಾ ಪ್ರಮಾಣ",
        "ta": "கல்வியறிவு விகிதம்",
        "te": "అక్షరాస్యత రేటు",
        "mr": "साक्षरता प्रमाण",
    },
    "school_enrollment_ratio": {
        "en": "School Enrollment Ratio",
        "ml": "സ്കൂൾ പ്രവേശന അനുപാതം",
        "kn": "ಶಾಲೆ ದಾಖಲಾತಿ ಅನುಪಾತ",
        "ta": "பள்ளி சேர்க்கை விகிதம்",
        "te": "పాఠశాల నమోదు నిష్పత్తి",
        "mr": "शाळा नोंदणी प्रमाण",
    },
    "dropout_rate": {
        "en": "School Dropout Rate",
        "ml": "സ്കൂൾ കൊഴിഞ്ഞുപോക്ക് നിരക്ക്",
        "kn": "ಶಾಲೆ ಬಿಡುವವರ ಪ್ರಮಾಣ",
        "ta": "பள்ளி இடைநிற்றல் விகிதம்",
        "te": "పాఠశాల డ్రాపౌట్ రేటు",
        "mr": "शाळा सोडण्याचे प्रमाण",
    },
    "student_teacher_ratio": {
        "en": "Student-Teacher Ratio",
        "ml": "വിദ്യാർത്ഥി-അധ്യാപക അനുപാതം",
        "kn": "ವಿದ್ಯಾರ್ಥಿ-ಶಿಕ್ಷಕ ಅನುಪಾತ",
        "ta": "மாணவர்-ஆசிரியர் விகிதம்",
        "te": "విద్యార్థి-ఉపాధ్యాయుల నిష్పత్తి",
        "mr": "विद्यार्थी-शिक्षक प्रमाण",
    },
    "digital_classroom_pct": {
        "en": "Digital Classroom %",
        "ml": "ഡിജിറ്റൽ ക്ലാസ്റൂം %",
        "kn": "ಡಿಜಿಟಲ್ ತರಗತಿ ಕೊಠಡಿ %",
        "ta": "டிஜிட்டல் வகுப்பறை %",
        "te": "డిజిటల్ తరగతి గది %",
        "mr": "डिजिटल वर्गखोल्या %",
    },
    "road_connectivity_index": {
        "en": "Road Connectivity Index",
        "ml": "റോഡ് കണക്റ്റിവിറ്റി സൂചിക",
        "kn": "ರಸ್ತೆ ಸಂಪರ್ಕ ಸೂಚ್ಯಂಕ",
        "ta": "சாலை இணைப்பு குறியீடு",
        "te": "రహదారి కనెక్టివిటీ సూచిక",
        "mr": "रस्ता कनेक्टिव्हिटी निर्देशांक",
    },
    "safe_drinking_water_pct": {
        "en": "Safe Drinking Water Access %",
        "ml": "ശുദ്ധജല ലഭ്യത %",
        "kn": "ಸುರಕ್ಷಿತ ಕುಡಿಯುವ ನೀರು %",
        "ta": "பாதுகாப்பான குடிநீர் %",
        "te": "సురక్షిత తాగునీరు %",
        "mr": "सुरक्षित पिण्याचे पाणी %",
    },
    "electrification_pct": {
        "en": "Electrification %",
        "ml": "വൈദ്യുതീകരണം %",
        "kn": "ವಿದ್ಯುದೀಕರಣ %",
        "ta": "மின்மயமாக்கல் %",
        "te": "విద్యుద్దీకరణ %",
        "mr": "विद्युतीकरण %",
    },
    "housing_adequacy_pct": {
        "en": "Housing Adequacy %",
        "ml": "ഭവന സുരക്ഷിതത്വം %",
        "kn": "ವಸತಿ ಸಮರ್ಪಕತೆ %",
        "ta": "வீட்டு வசதி போதுமான அளவு %",
        "te": "గృహ వసతి సమృద్ధి %",
        "mr": "गृहनिर्माण पर्याप्तता %",
    },
    "public_transport_access": {
        "en": "Public Transport Access",
        "ml": "പൊതുഗതാഗത ലഭ്യത",
        "kn": "ಸಾರ್ವಜನಿಕ ಸಾರಿಗೆ ಲಭ್ಯತೆ",
        "ta": "பொதுப் போக்குவரத்து வசதி",
        "te": "ప్రజా రవాణా సదుపాయం",
        "mr": "सार्वजनिक वाहतूक सुविधा",
    },
    "cultivable_land_pct": {
        "en": "Cultivable Land %",
        "ml": "കൃഷിഭൂമി %",
        "kn": "ಕೃಷಿಯೋಗ್ಯ ಭೂಮಿ %",
        "ta": "சாகுபடி நிலம் %",
        "te": "వ్యవసాయ యోగ్యమైన భూమి %",
        "mr": "लागवडीयोग्य जमीन %",
    },
    "irrigation_coverage_pct": {
        "en": "Irrigation Coverage %",
        "ml": "ജലസേചന ലഭ്യത %",
        "kn": "ನೀರಾವರಿ ವ್ಯಾಪ್ತಿ %",
        "ta": "பாசன வசதி %",
        "te": "నీటిపారుదల రక్షణ %",
        "mr": "जलसिंचन व्याप्ती %",
    },
    "crop_yield_index": {
        "en": "Crop Yield Index",
        "ml": "വിളവ് സൂചിക",
        "kn": "ಬೆಳೆ ಇಳುವರಿ ಸೂಚ್ಯಂಕ",
        "ta": "பயிர் விளைச்சல் குறியீடு",
        "te": "పంట దిగుబడి సూచిక",
        "mr": "पीक उत्पादन निर्देशांक",
    },
    "farmer_income_level": {
        "en": "Farmer Income Level",
        "ml": "കർഷക വരുമാന നിലവാരം",
        "kn": "ರೈತರ ಆದಾಯ ಮಟ್ಟ",
        "ta": "விவசாயிகள் வருமான நிலை",
        "te": "రైతుల ఆదాయ స్థాయి",
        "mr": "शेतकरी उत्पन्न पातळी",
    },
    "food_security_score": {
        "en": "Food Security Score",
        "ml": "ഭക്ഷ്യസുരക്ഷാ സ്കോർ",
        "kn": "ಆಹಾರ ಭದ್ರತೆ ಸ್ಕೋರ್",
        "ta": "உணவு பாதுகாப்பு மதிப்பெண்",
        "te": "ఆహార భద్రత స్కోరు",
        "mr": "अन्न सुरक्षा स्कोअर",
    },
    "poverty_rate_bpl_pct": {
        "en": "BPL Population %",
        "ml": "ദാരിദ്ര്യരേഖയ്ക്ക് താഴെയുള്ളവർ %",
        "kn": "ಬಿಪಿಎಲ್ ಜನಸಂಖ್ಯೆ %",
        "ta": "வறுமைக் கோட்டிற்கு கீழ் உள்ளோர் %",
        "te": "దారిద్య్ర రేఖ దిగువన ఉన్నవారు %",
        "mr": "दारिद्र्यरेषेखालील लोकसंख्या %",
    },
    "sc_st_population_pct": {
        "en": "SC/ST Population %",
        "ml": "SC/ST ജനസംഖ്യ %",
        "kn": "ಎಸ್ಸಿ/ಎಸ್ಟಿ ಜನಸಂಖ್ಯೆ %",
        "ta": "SC/ST மக்கள் தொகை %",
        "te": "ఎస్సీ/ఎస్టీ జనాభా %",
        "mr": "अनुसूचित जाती/जमाती लोकसंख्या %",
    },
    "women_empowerment_index": {
        "en": "Women Empowerment Index",
        "ml": "സ്ത്രീ ശാക്തീകരണ സൂചിക",
        "kn": "ಮಹಿಳಾ ಸಬಲೀಕರಣ ಸೂಚ್ಯಂಕ",
        "ta": "பெண்கள் அதிகாரமளித்தல் குறியீடு",
        "te": "మహిళా సాధికారత సూచిక",
        "mr": "महिला सक्षमीकरण निर्देशांक",
    },
    "disability_support_coverage": {
        "en": "Disability Support Coverage",
        "ml": "ഭിന്നശേഷി പിന്തുണ ലഭ്യത",
        "kn": "ವಿಕಲಾಂಗರ ಬೆಂಬಲ ವ್ಯಾಪ್ತಿ",
        "ta": "மாற்றுத்திறனாளிகள் ஆதரவு",
        "te": "దివ్యాంగుల సహాయ పరిధి",
        "mr": "दिव्यांग सहाय्य व्याप्ती",
    },
    "pension_coverage_pct": {
        "en": "Pension Coverage %",
        "ml": "പെൻഷൻ ലഭ്യത %",
        "kn": "ಪಿಂಚಣಿ ವ್ಯಾಪ್ತಿ %",
        "ta": "ஓய்வூதிய பாதுகாப்பு %",
        "te": "పింఛను పరిధి %",
        "mr": "पेन्शन व्याप्ती %",
    },
    "employment_rate": {
        "en": "Employment Rate",
        "ml": "തൊഴിൽ നിരക്ക്",
        "kn": "ಉದ್ಯೋಗ ದರ",
        "ta": "வேலைவாய்ப்பு விகிதம்",
        "te": "ఉపాధి రేటు",
        "mr": "रोजगार दर",
    },
    "msme_density": {
        "en": "MSME Density",
        "ml": "ചെറുകിട വ്യവസായ സാന്ദ്രത",
        "kn": "ಎಂಎಸ್ಎಂಇ ಸಾಂದ್ರತೆ",
        "ta": "சிறு குறு தொழில்கள் அடர்த்தி",
        "te": "సూక్ష్మ చిన్న పరిశ్రమల సాంద్రత",
        "mr": "लघु व मध्यम उद्योग घनता",
    },
    "per_capita_income": {
        "en": "Per Capita Income",
        "ml": "പ്രതിശീർഷ വരുമാനം",
        "kn": "ತಲಾ ಆದಾಯ",
        "ta": "தனிநபர் வருமானம்",
        "te": "తలసరి ఆదాయం",
        "mr": "दरडोई उत्पन्न",
    },
    "skill_training_coverage_pct": {
        "en": "Skill Training Coverage %",
        "ml": "നൈപുണ്യ പരിശീലനം %",
        "kn": "ಕೌಶಲ್ಯ ತರಬೇತಿ %",
        "ta": "திறன் பயிற்சி பாதுகாப்பு %",
        "te": "నైపుణ్య శిక్షణ %",
        "mr": "कौशल्य प्रशिक्षण %",
    },
    "tourism_potential_index": {
        "en": "Tourism Potential Index",
        "ml": "ടൂറിസം സാധ്യത സൂചിക",
        "kn": "ಪ್ರವಾಸೋದ್ಯಮ ಸಾಮರ್ಥ್ಯ ಸೂಚ್ಯಂಕ",
        "ta": "சுற்றுலா சாத்தியக்கூறு குறியீடு",
        "te": "పర్యాటక సామర్థ్య సూచిక",
        "mr": "पर्यटन क्षमता निर्देशांक",
    },
    "flood_risk_score": {
        "en": "Flood Risk Score",
        "ml": "വെള്ളപ്പൊക്ക സാധ്യത സ്കോർ",
        "kn": "ಪ್ರವಾಹ ಅಪಾಯ ಸ್ಕೋರ್",
        "ta": "வெள்ள அபாய மதிப்பெண்",
        "te": "వరద ప్రమాద స్కోరు",
        "mr": "पूर जोखीम स्कोअर",
    },
    "waste_management_coverage_pct": {
        "en": "Waste Management Coverage %",
        "ml": "മാലിന്യ സംസ്കരണ ലഭ്യത %",
        "kn": "ತ್ಯಾಜ್ಯ ನಿರ್ವಹಣೆ ವ್ಯಾಪ್ತಿ %",
        "ta": "கழிவு மேலாண்மை %",
        "te": "వ్యర్థాల నిర్వహణ %",
        "mr": "कचरा व्यवस्थापन व्याप्ती %",
    },
    "green_cover_pct": {
        "en": "Green Cover %",
        "ml": "ഹരിത ഭൂമി %",
        "kn": "ಹಸಿರು ಹೊದಿಕೆ %",
        "ta": "பசுமை பரப்பு %",
        "te": "హరిత విస్తీర్ణం %",
        "mr": "हरित आच्छादन %",
    },
    "water_body_health_index": {
        "en": "Water Body Health Index",
        "ml": "ജലാശയ ആരോഗ്യ സൂചിക",
        "kn": "ಜಲಮೂಲಗಳ ಆರೋಗ್ಯ ಸೂಚ್ಯಂಕ",
        "ta": "நீர்நிலைகள் பாதுகாப்பு குறியீடு",
        "te": "జలాశయాల ఆరోగ్య సూచిక",
        "mr": "जलस्रोत आरोग्य निर्देशांक",
    },
    "disaster_preparedness_score": {
        "en": "Disaster Preparedness Score",
        "ml": "ദുരന്ത നിവാരണ സന്നദ്ധത",
        "kn": "ವಿಪತ್ತು ಸನ್ನದ್ಧತೆ ಸ್ಕೋರ್",
        "ta": "பேரிடர் தயார்நிலை மதிப்பெண்",
        "te": "విపత్తు సంసిద్ధత స్కోరు",
        "mr": "आपत्ती सज्जता स्कोअर",
    },
    "internet_penetration_pct": {
        "en": "Internet Penetration %",
        "ml": "ഇന്റർനെറ്റ് ലഭ്യത %",
        "kn": "ಇಂಟರ್ನೆಟ್ ಸಂಪರ್ಕ %",
        "ta": "இணைய வசதி %",
        "te": "ఇంటర్నెట్ వ్యాప్తి %",
        "mr": "इंटरनेट सुविधा %",
    },
    "digital_literacy_pct": {
        "en": "Digital Literacy %",
        "ml": "ഡിജിറ്റൽ സാക്ഷരത %",
        "kn": "ಡಿಜಿಟಲ್ ಸಾಕ್ಷರತೆ %",
        "ta": "டிஜிட்டல் கல்வியறிவு %",
        "te": "డిజిటల్ అక్షరాస్యత %",
        "mr": "डिजिटल साक्षरता %",
    },
    "e_service_adoption_rate": {
        "en": "E-Service Adoption Rate",
        "ml": "ഇ-സർവീസ് ഉപയോഗ നിരക്ക്",
        "kn": "ಇ-ಸೇವೆ ಬಳಕೆ ದರ",
        "ta": "மின்-சேவை பயன்பாட்டு விகிதம்",
        "te": "ఈ-సేవల వినియోగ రేటు",
        "mr": "ई-सेवा वापर दर",
    },
    "aadhaar_enrollment_pct": {
        "en": "Aadhaar Enrollment %",
        "ml": "ആധാർ എൻറോൾമെന്റ് %",
        "kn": "ಆಧಾರ್ ನೋಂದಣಿ %",
        "ta": "ஆதார் பதிவு %",
        "te": "ఆధార్ నమోదు %",
        "mr": "आधार नोंदणी %",
    },
    "mobile_connectivity_index": {
        "en": "Mobile Connectivity Index",
        "ml": "മൊബൈൽ കണക്റ്റിവിറ്റി സൂചിക",
        "kn": "ಮೊಬೈಲ್ ಸಂಪರ್ಕ ಸೂಚ್ಯಂಕ",
        "ta": "கைபேசி இணைப்பு குறியீடு",
        "te": "మొబైల్ కనెక్టివిటీ సూచిక",
        "mr": "मोबाइल कनेक्टिव्हिटी निर्देशांक",
    },
}

# English label fallback mapping
FEATURE_LABELS = {k: v["en"] for k, v in FEATURE_LABELS_I18N.items()}

def get_indicator_label(indicator_name, lang="en"):
    """Get localized label for an indicator key."""
    lang = lang or "en"
    if indicator_name in FEATURE_LABELS_I18N:
        entry = FEATURE_LABELS_I18N[indicator_name]
        return entry.get(lang, entry.get("en", indicator_name))
    return indicator_name.replace("_", " ").title()


SECTOR_NAMES_I18N = {
    "Health & Sanitation": {
        "en": "Health & Sanitation",
        "ml": "ആരോഗ്യവും ശുചിത്വവും",
        "kn": "ಆರೋಗ್ಯ ಮತ್ತು ನೈರ್ಮಲ್ಯ",
        "ta": "சுகாதாரம் மற்றும் துப்புரவு",
        "te": "ఆరోగ్యం మరియు పారిశుధ్యం",
        "mr": "आरोग्य आणि स्वच्छता",
    },
    "Education": {
        "en": "Education",
        "ml": "വിദ്യാഭ്യാസം",
        "kn": "ಶಿಕ್ಷಣ",
        "ta": "கல்வி",
        "te": "విద్య",
        "mr": "शिक्षण",
    },
    "Infrastructure": {
        "en": "Infrastructure",
        "ml": "അടിസ്ഥാന സൗകര്യങ്ങൾ",
        "kn": "ಮೂಲಸೌಕರ್ಯ",
        "ta": "உள்கட்டமைப்பு",
        "te": "మౌలిక సదుపాయాలు",
        "mr": "पायाभूत सुविधा",
    },
    "Agriculture & Food Security": {
        "en": "Agriculture & Food Security",
        "ml": "കൃഷിയും ഭക്ഷ്യസുരക്ഷയും",
        "kn": "ಕೃಷಿ ಮತ್ತು ಆಹಾರ ಭದ್ರತೆ",
        "ta": "விவசாயம் மற்றும் உணவுப் பாதுகாப்பு",
        "te": "వ్యవసాయం మరియు ఆహార భద్రత",
        "mr": "शेती आणि अन्न सुरक्षा",
    },
    "Social Welfare": {
        "en": "Social Welfare",
        "ml": "സാമൂഹ്യക്ഷേമം",
        "kn": "ಸಮಾಜ ಕಲ್ಯಾಣ",
        "ta": "சமூக நலன்",
        "te": "సాంఘిక సంక్షేమం",
        "mr": "समाज कल्याण",
    },
    "Economic Development": {
        "en": "Economic Development",
        "ml": "സാമ്പത്തിക വികസനം",
        "kn": "ಆರ್ಥಿಕ ಅಭಿವೃದ್ಧಿ",
        "ta": "பொருளாதார வளர்ச்சி",
        "te": "ఆర్థిక అభివృద్ధి",
        "mr": "आर्थिक विकास",
    },
    "Environment & Disaster Mgmt": {
        "en": "Environment & Disaster Mgmt",
        "ml": "പരിസ്ഥിതിയും ദുരന്തനിവാരണവും",
        "kn": "ಪರಿಸರ ಮತ್ತು ವಿಪತ್ತು ನಿರ್ವಹಣೆ",
        "ta": "சுற்றுச்சூழல் மற்றும் பேரிடர் மேலாண்மை",
        "te": "పర్యావరణం మరియు విపత్తు నిర్వహణ",
        "mr": "पर्यावरण आणि आपत्ती व्यवस्थापन",
    },
    "Digital & E-Governance": {
        "en": "Digital & E-Governance",
        "ml": "ഡിജിറ്റൽ & ഇ-ഭരണം",
        "kn": "ಡಿಜಿಟಲ್ & ಇ-ಆಡಳಿತ",
        "ta": "டிஜிட்டல் மற்றும் மின்-ஆளுமை",
        "te": "డిజిటల్ మరియు ఇ-పరిపాలన",
        "mr": "डिजिटल आणि ई-प्रशासन",
    },
}

def get_localized_sector(sector_en, lang="en"):
    """Get localized sector name."""
    lang = lang or "en"
    if sector_en in SECTOR_NAMES_I18N:
        return SECTOR_NAMES_I18N[sector_en].get(lang, sector_en)
    return sector_en


SEVERITY_I18N = {
    "high": {
        "en": ("critically high", "CRITICAL (High Priority)"),
        "ml": ("ഗുരുതരമായ നിലയിൽ", "അതീവ ശ്രദ്ധ ആവശ്യമുള്ളത്"),
        "kn": ("ಅತ್ಯಂತ ಗಂಭೀರ ಮಟ್ಟದಲ್ಲಿದೆ", "ತುರ್ತು ಆದ್ಯತೆ"),
        "ta": ("மிகத் தீவிரமான நிலையில் உள்ளது", "அவசர முன்னுரிமை"),
        "te": ("అత్యంత తీవ్రమైన స్థాయిలో ఉంది", "అత్యవసర ప్రాధాన్యత"),
        "mr": ("अतिशय गंभीर पातळीवर", "तातडीचे प्राधान्य"),
    },
    "medium": {
        "en": ("moderately elevated", "MODERATE"),
        "ml": ("മിതമായ തോതിൽ", "ഇടത്തരം"),
        "kn": ("ಮಧ್ಯಮ ಮಟ್ಟದಲ್ಲಿದೆ", "ಮಧ್ಯಮ"),
        "ta": ("மிதமான அளவில் உள்ளது", "நடுத்தர"),
        "te": ("మధ్యస్థ స్థాయిలో ఉంది", "మధ్యస్థం"),
        "mr": ("मध्यम पातळीवर", "मध्यम"),
    },
    "low": {
        "en": ("within acceptable range", "LOW"),
        "ml": ("സ്വീകാര്യമായ പരിധിയിൽ", "കുറഞ്ഞ അപകടസാധ്യത"),
        "kn": ("ಸ್ವೀಕಾರಾರ್ಹ ವ್ಯಾಪ್ತಿಯಲ್ಲಿದೆ", "ಕಡಿಮೆ ಅಪಾಯ"),
        "ta": ("ஏற்றுக்கொள்ளக்கூடிய வரம்பில் உள்ளது", "குறைந்த ஆபத்து"),
        "te": ("ఆమోదయోగ్యమైన పరిధిలో ఉంది", "తక్కువ ప్రమాదం"),
        "mr": ("स्वीकार्य मर्यादेत", "कमी जोखीम"),
    },
}

LANGUAGE_NAMES = {
    "en": "English",
    "ml": "Malayalam",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
}


_explanation_cache = {}

def generate_openai_explanation(ward_name, sector_name, ward_data, vulnerability_score, lang="en"):
    """
    Generate an intelligent AI explanation using GPT-3.5-turbo in the requested language.
    Falls back to a structured, localized template if the API is unavailable.
    """
    lang = lang or "en"
    cache_key = (ward_name, sector_name, lang)
    if cache_key in _explanation_cache:
        return _explanation_cache[cache_key]

    # High-speed local ML intelligence engine (<0.1ms).
    # Remote OpenAI calls are only used if explicitly enabled in configuration.
    if not ENABLE_OPENAI_EXPLANATIONS:
        res = _fallback_explanation(ward_name, sector_name, ward_data, vulnerability_score, lang=lang)
        _explanation_cache[cache_key] = res
        return res

    client = _get_openai_client()
    if not client or not OPENAI_API_KEY:
        res = _fallback_explanation(ward_name, sector_name, ward_data, vulnerability_score, lang=lang)
        _explanation_cache[cache_key] = res
        return res

    # Build indicator context for the prompt
    sector_indicators = SECTOR_INDICATORS.get(sector_name, [])
    indicator_values = {}
    for ind in sector_indicators:
        if ind in ward_data:
            label = get_indicator_label(ind, lang=lang)
            indicator_values[label] = round(float(ward_data[ind]), 3)

    # Determine severity
    if vulnerability_score > 0.7:
        sev_key = "high"
        severity_emoji = "🔴"
    elif vulnerability_score > 0.4:
        sev_key = "medium"
        severity_emoji = "🟡"
    else:
        sev_key = "low"
        severity_emoji = "🟢"

    severity_label, severity_title = SEVERITY_I18N[sev_key].get(lang, SEVERITY_I18N[sev_key]["en"])
    lang_name = LANGUAGE_NAMES.get(lang, "English")
    state_name = ward_data.get("state", "Local State")
    panchayat_name = ward_data.get("panchayat_name", "Local Panchayat")
    district_name = ward_data.get("district", "Local District")
    localized_sector = get_localized_sector(sector_name, lang=lang)

    SECTION_HEADERS = {
        "key_indicators": {
            "en": "Key Indicators",
            "ml": "പ്രധാന സൂചകങ്ങൾ",
            "kn": "ಪ್ರಮುಖ ಸೂಚಕಗಳು",
            "ta": "முக்கிய குறிகாட்டிகள்",
            "te": "కీలక సూచికలు",
            "mr": "प्रमुख निर्देशक",
        },
        "recommended_action": {
            "en": "Recommended Action",
            "ml": "ശുപാർശ ചെയ്ത നടപടി",
            "kn": "ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮ",
            "ta": "பரிந்துரைக்கப்பட்ட நடவடிக்கை",
            "te": "సిఫార్సు చేసిన చర్య",
            "mr": "शिफारस केलेली कारवाई",
        },
        "funding_sources": {
            "en": "Funding Sources",
            "ml": "ധനസഹായ സ്രോതസ്സുകൾ",
            "kn": "ನಿಧಿ ಮೂಲಗಳು",
            "ta": "நிதி ஆதாரங்கள்",
            "te": "నిధుల వనరులు",
            "mr": "निधी स्रोत",
        },
    }

    hdr_ind = SECTION_HEADERS["key_indicators"].get(lang, "Key Indicators")
    hdr_act = SECTION_HEADERS["recommended_action"].get(lang, "Recommended Action")
    hdr_fnd = SECTION_HEADERS["funding_sources"].get(lang, "Funding Sources")

    prompt = f"""You are an expert AI assistant for the Smart Panchayat planning system.
Analyze the following ward data and generate a clear, structured, actionable report entirely in {lang_name}.
CRITICAL: Do NOT mix other languages. Write the entire response in {lang_name}.

Ward: {ward_name}
Panchayat: {panchayat_name}, {district_name}, {state_name}
Priority Sector: {localized_sector} ({sector_name})
Vulnerability Score: {vulnerability_score:.3f} — {severity_title} {severity_emoji}

Sector Indicator Values (normalized 0-1, where 1 = most vulnerable):
{json.dumps(indicator_values, indent=2, ensure_ascii=False)}

Generate a structured markdown report entirely in {lang_name} using these exact markdown headers:
### {severity_emoji} Analysis: {ward_name} — {localized_sector}

[One concise paragraph explaining why {localized_sector} is prioritized for {ward_name}]

#### 📊 {hdr_ind}
[Top 3 critical indicator issues and their numeric scores]

#### 🎯 {hdr_act}
[Specific, actionable local development projects and government interventions]

#### 💰 {hdr_fnd}
[Applicable Central and State schemes (e.g. MGNREGS, NHM, State rural development funds)]

Tone: Professional, direct, actionable. Everything in {lang_name}."""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert government AI planning assistant. Always respond with valid markdown entirely in {lang_name}."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7,
            timeout=2.5,
        )
        content = response.choices[0].message.content
        _explanation_cache[cache_key] = content
        return content

    except Exception as e:
        print(f"OpenAI API error: {e}")
        res = _fallback_explanation(ward_name, sector_name, ward_data, vulnerability_score, lang=lang)
        _explanation_cache[cache_key] = res
        return res


def _fallback_explanation(ward_name, sector_name, ward_data, vulnerability_score, lang="en"):
    """Template-based fallback explanation localized strictly to the chosen language."""
    lang = lang or "en"

    if vulnerability_score > 0.7:
        severity_emoji = "🔴"
        sev_key = "high"
    elif vulnerability_score > 0.4:
        severity_emoji = "🟡"
        sev_key = "medium"
    else:
        severity_emoji = "🟢"
        sev_key = "low"

    severity_label, _ = SEVERITY_I18N[sev_key].get(lang, SEVERITY_I18N[sev_key]["en"])
    localized_sector = get_localized_sector(sector_name, lang=lang)
    state_name = ward_data.get("state", "State")

    # Get sector indicators and their values
    sector_indicators = SECTOR_INDICATORS.get(sector_name, [])
    indicator_lines = []
    for ind in sector_indicators[:3]:
        if ind in ward_data:
            label = get_indicator_label(ind, lang=lang)
            val = float(ward_data[ind])
            indicator_lines.append(f"- **{label}**: {val:.3f}")

    indicator_text = "\n".join(indicator_lines) if indicator_lines else "- Data available in dashboard"

    # Multilingual templates
    if lang == "ml":
        return f"""### {severity_emoji} വിശകലനം: {ward_name} — {localized_sector}

{severity_emoji} AI **{localized_sector}** മേഖലയെ **{ward_name}** വാർഡിന്റെ മുൻഗണനയായി തിരിച്ചറിഞ്ഞു. ദുർബലത സ്കോർ: **{vulnerability_score:.3f}** — **{severity_label}**.

#### 📊 പ്രധാന സൂചകങ്ങൾ

{indicator_text}

#### 🎯 ശുപാർശ ചെയ്ത നടപടി

പഞ്ചായത്ത് **{ward_name}** വാർഡിലെ **{localized_sector}** മേഖലയിൽ അടിയന്തര നിക്ഷേപം നടത്തണം. ബന്ധപ്പെട്ട സർക്കാർ വകുപ്പുകളുമായി ഏകോപിപ്പിച്ച് വികസന പദ്ധതികൾ (തൊഴിലുറപ്പ്, എൻ.എച്ച്.എം, കുടുംബശ്രീ) നടപ്പിലാക്കുക.

#### 💰 ധനസഹായ സ്രോതസ്സുകൾ

{localized_sector} മേഖലയ്ക്കുള്ള സംസ്ഥാന, കേന്ദ്ര സർക്കാർ വികസന ഫണ്ടുകൾ.

⚡ *മൾട്ടി-സ്റ്റേറ്റ് ML എഞ്ചിൻ വഴി തത്സമയം തയ്യാറാക്കിയ AI ഡയഗ്നോസ്റ്റിക്.*
"""

    elif lang == "kn":
        return f"""### {severity_emoji} ವಿಶ್ಲೇಷಣೆ: {ward_name} — {localized_sector}

{severity_emoji} AI **{localized_sector}** ವಲಯವನ್ನು **{ward_name}** ವಾರ್ಡ್‌ನ ಪ್ರಮುಖ ಆದ್ಯತೆಯಾಗಿ ಗುರುತಿಸಿದೆ. ದುರ್ಬಲತೆ ಸ್ಕೋರ್: **{vulnerability_score:.3f}** — **{severity_label}**.

#### 📊 ಪ್ರಮುಖ ಸೂಚಕಗಳು

{indicator_text}

#### 🎯 ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮ

ಗ್ರಾಮ ಪಂಚಾಯತ್ **{ward_name}** ವಾರ್ಡ್‌ನಲ್ಲಿ **{localized_sector}** ವಲಯದಲ್ಲಿ ತುರ್ತು ಹೂಡಿಕೆಗೆ ಆದ್ಯತೆ ನೀಡಬೇಕು. ಸಂಬಂಧಿತ ಇಲಾಖೆಗಳೊಂದಿಗೆ ಸಮನ್ವಯ ಸಾಧಿಸಿ ಗ್ರಾಮೀಣ ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಳನ್ನು (ಮನರೇಗಾ, ಎನ್‌ಎಚ್‌ಎಂ ಮುಂತಾದವು) ಜಾರಿಗೊಳಿಸಿ.

#### 💰 ನಿಧಿ ಮೂಲಗಳು

{localized_sector} ವಲಯಕ್ಕಾಗಿ ಅನ್ವಯವಾಗುವ {state_name} ರಾಜ್ಯ ಮತ್ತು ಕೇಂದ್ರ ಸರ್ಕಾರದ ಅಭಿವೃದ್ಧಿ ಯೋಜನೆಗಳು.

⚡ *ಮಲ್ಟಿ-ಸ್ಟೇಟ್ ಎಂಎಲ್ ಎಂಜಿನ್ ಬಳಸಿ ರಚಿಸಲಾದ ತ್ವರಿತ AI ವಿಶ್ಲೇಷಣೆ.*
"""

    elif lang == "ta":
        return f"""### {severity_emoji} பகுப்பாய்வு: {ward_name} — {localized_sector}

{severity_emoji} AI **{localized_sector}** துறையை **{ward_name}** வார்டின் முதன்மை முன்னுரிமையாக அடையாளம் கண்டுள்ளது. பாதிப்பு மதிப்பெண்: **{vulnerability_score:.3f}** — **{severity_label}**.

#### 📊 முக்கிய குறிகாட்டிகள்

{indicator_text}

#### 🎯 பரிந்துரைக்கப்பட்ட நடவடிக்கை

பஞ்சாயத்து **{ward_name}** வார்டில் **{localized_sector}** துறைக்கு உடனடி முன்னுரிமை அளிக்க வேண்டும். அரசுத் துறைகளுடன் இணைந்து தேசிய மற்றும் மாநில நலத்திட்டங்களை (MGNREGS, NHM) செயல்படுத்தவும்.

#### 💰 நிதி ஆதாரங்கள்

{localized_sector} துறைக்கான {state_name} மாநில மற்றும் மத்திய அரசு வளர்ச்சி திட்டங்கள்.

⚡ *மல்டி-ஸ்டேட் எம்எல் எஞ்சின் மூலம் உருவாக்கப்பட்ட உடனடி AI பகுப்பாய்வு.*
"""

    elif lang == "te":
        return f"""### {severity_emoji} విశ్లేషణ: {ward_name} — {localized_sector}

{severity_emoji} AI **{localized_sector}** రంగాన్ని **{ward_name}** వార్డు యొక్క ప్రధాన ప్రాధాన్యతగా గుర్తించింది. హానికరత స్కోరు: **{vulnerability_score:.3f}** — **{severity_label}**.

#### 📊 కీలక సూచికలు

{indicator_text}

#### 🎯 సిఫార్సు చేసిన చర్య

గ్రామ పంచాయతీ **{ward_name}** వార్డులోని **{localized_sector}** రంగానికి తక్షణ ప్రాధాన్యత ఇవ్వాలి. సంబంధిత ప్రభుత్వ శాఖలతో సమన్వయం చేసుకుని గ్రామీణాభివృద్ధి పథకాలను (ఉపాధి హామీ, ఎన్‌హెచ్‌ఎం) అమలు చేయండి.

#### 💰 నిధుల వనరులు

{localized_sector} రంగానికి వర్తించే {state_name} రాష్ట్ర మరియు కేంద్ర ప్రభుత్వ పథకాలు.

⚡ *మల్టీ-స్టేట్ ఎంఎల్ ఇంజిన్ ద్వారా రూపొందించబడిన తక్షణ AI విశ్లేషణ.*
"""

    elif lang == "mr":
        return f"""### {severity_emoji} विश्लेषण: {ward_name} — {localized_sector}

{severity_emoji} AI ने **{localized_sector}** क्षेत्राला **{ward_name}** वॉर्डचे सर्वोच्च प्राधान्य म्हणून ओळखले आहे. संवेदनशीलता स्कोअर: **{vulnerability_score:.3f}** — **{severity_label}**.

#### 📊 प्रमुख निर्देशक

{indicator_text}

#### 🎯 शिफारस केलेली कारवाई

ग्रामपंचायतीने **{ward_name}** वॉर्डमधील **{localized_sector}** क्षेत्रासाठी त्वरित गुंतवणुकीला प्राधान्य दिले पाहिजे. संबंधित शासकीय विभागांशी समन्वय साधून विकास योजना (मनरेगा, एनएचएम) राबवा.

#### 💰 निधी स्रोत

{localized_sector} क्षेत्रासाठी लागू असलेल्या {state_name} राज्य आणि केंद्र शासकीय विकास योजना.

⚡ *मल्टी-स्टेट एमएल इंजिनद्वारे तयार केलेले त्वरित AI विश्लेषण.*
"""

    else:  # Default: English
        return f"""### {severity_emoji} Analysis for {ward_name} — {sector_name}

{severity_emoji} The AI has identified **{sector_name}** as a priority for **{ward_name}** ward.
Vulnerability score: **{vulnerability_score:.3f}** — **{severity_label}**.

#### 📊 Key Indicators

{indicator_text}

#### 🎯 Recommended Action

The Panchayat should prioritize immediate investment in **{sector_name}** for {ward_name} ward.
Coordinate with relevant state departments and explore development schemes (MGNREGS, NHM, and sector missions).

#### 💰 Funding Sources

Applicable {state_name} and Central Government development schemes for {sector_name}.

⚡ *Instant AI Diagnostic generated using Multi-State ML Engine.*
"""


def get_feature_importance_for_ward(ward_data, sector_name):
    """
    Get indicator values for a ward's priority sector,
    sorted by vulnerability contribution (highest first).
    Returns list of (feature_name, value) tuples.
    """
    sector_indicators = SECTOR_INDICATORS.get(sector_name, [])
    result = []
    for ind in sector_indicators:
        if ind in ward_data:
            result.append((ind, float(ward_data[ind])))
    # Sort by value descending (higher = more vulnerable)
    result.sort(key=lambda x: x[1], reverse=True)
    return result

