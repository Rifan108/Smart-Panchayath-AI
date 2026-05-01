# -*- coding: utf-8 -*-
"""
Plain-language problem/solution descriptions for indicators.
Each entry: (simple English problem, Malayalam translation, what to do)
"""

INDICATOR_PROBLEMS = {
    "disease_incidence_rate": (
        "Many people in this ward are falling sick frequently.",
        "ഈ വാർഡിൽ പലരും ഇടയ്ക്കിടെ രോഗികളാകുന്നു.",
        "Set up weekly health camps and improve sanitation."
    ),
    "hospital_beds_per_1000": (
        "There are not enough hospital beds for the people living here.",
        "ഇവിടെ താമസിക്കുന്ന ആളുകൾക്ക് ആവശ്യത്തിന് ആശുപത്രി കിടക്കകൾ ഇല്ല.",
        "Build a Primary Health Sub-Centre or expand the existing one."
    ),
    "doctor_patient_ratio": (
        "There are too few doctors for the number of patients.",
        "രോഗികളുടെ എണ്ണത്തിന് അനുസരിച്ച് ഡോക്ടർമാർ വളരെ കുറവാണ്.",
        "Recruit more doctors and organize visiting specialist camps."
    ),
    "infant_mortality_rate": (
        "Too many newborn babies are not surviving in this ward.",
        "ഈ വാർഡിൽ ഒരുപാട് നവജാത ശിശുക്കൾ മരിക്കുന്നു.",
        "Strengthen ASHA worker network and prenatal care services."
    ),
    "vaccination_coverage_pct": (
        "Many children are not getting their vaccinations on time.",
        "പല കുട്ടികൾക്കും സമയത്ത് വാക്സിനേഷൻ ലഭിക്കുന്നില്ല.",
        "Run door-to-door vaccination drives through anganwadis."
    ),
    "literacy_rate": (
        "Many adults in this ward cannot read or write properly.",
        "ഈ വാർഡിലെ പല മുതിർന്നവർക്കും ശരിയായി വായിക്കാനോ എഴുതാനോ കഴിയില്ല.",
        "Start adult literacy classes through Kudumbashree units."
    ),
    "school_enrollment_ratio": (
        "Some children in this area are not enrolled in school.",
        "ഈ പ്രദേശത്തെ ചില കുട്ടികൾ സ്കൂളിൽ ചേർന്നിട്ടില്ല.",
        "Identify out-of-school children and provide free enrollment support."
    ),
    "dropout_rate": (
        "Many students are dropping out of school before finishing.",
        "പല വിദ്യാർത്ഥികളും പഠനം പൂർത്തിയാക്കാതെ സ്കൂൾ വിടുന്നു.",
        "Provide free meals, books, and transport for BPL students."
    ),
    "student_teacher_ratio": (
        "There are too many students per teacher in schools here.",
        "ഇവിടുത്തെ സ്കൂളുകളിൽ ഓരോ അധ്യാപകനും വളരെയധികം വിദ്യാർത്ഥികളുണ്ട്.",
        "Deploy additional guest teachers through the District Education Office."
    ),
    "digital_classroom_pct": (
        "Most classrooms do not have computers or smart boards.",
        "മിക്ക ക്ലാസ്‌റൂമുകളിലും കമ്പ്യൂട്ടറോ സ്മാർട്ട് ബോർഡോ ഇല്ല.",
        "Install KITE Kerala digital classrooms in government schools."
    ),
    "road_connectivity_index": (
        "Roads in this ward are in poor condition or not properly connected.",
        "ഈ വാർഡിലെ റോഡുകൾ മോശം അവസ്ഥയിലാണ് അല്ലെങ്കിൽ ശരിയായി ബന്ധിപ്പിച്ചിട്ടില്ല.",
        "Resurface damaged roads using PMGSY/NABARD funding."
    ),
    "safe_drinking_water_pct": (
        "Many families here do not have access to clean drinking water.",
        "ഇവിടെ പല കുടുംബങ്ങൾക്കും ശുദ്ധമായ കുടിവെള്ളം ലഭിക്കുന്നില്ല.",
        "Extend Jal Jeevan Mission water pipelines to this ward."
    ),
    "electrification_pct": (
        "Some households still do not have proper electricity connection.",
        "ചില വീടുകളിൽ ഇപ്പോഴും ശരിയായ വൈദ്യുതി കണക്ഷൻ ഇല്ല.",
        "Coordinate with KSEB for full electrification."
    ),
    "housing_adequacy_pct": (
        "Many families are living in houses that are unsafe or too small.",
        "പല കുടുംബങ്ങളും സുരക്ഷിതമല്ലാത്ത അല്ലെങ്കിൽ ചെറിയ വീടുകളിൽ താമസിക്കുന്നു.",
        "Apply for LIFE Mission housing for eligible families."
    ),
    "public_transport_access": (
        "People find it hard to reach bus stops or get public transport.",
        "ആളുകൾക്ക് ബസ് സ്റ്റോപ്പിലെത്താനോ പൊതുഗതാഗതം ലഭിക്കാനോ ബുദ്ധിമുട്ടാണ്.",
        "Build bus waiting sheds and improve interior road access."
    ),
    "cultivable_land_pct": (
        "There is not enough farming land being used for growing food.",
        "ഭക്ഷണം വളർത്താൻ ആവശ്യത്തിന് കൃഷിഭൂമി ഉപയോഗിക്കുന്നില്ല.",
        "Promote Subhiksha Keralam to cultivate fallow land."
    ),
    "irrigation_coverage_pct": (
        "Most farms do not have proper water supply for crops.",
        "മിക്ക കൃഷിയിടങ്ങൾക്കും വിളകൾക്ക് ശരിയായ ജലവിതരണം ഇല്ല.",
        "Distribute micro-irrigation kits through Krishi Bhavan."
    ),
    "crop_yield_index": (
        "Farmers here are getting less harvest compared to other areas.",
        "ഇവിടുത്തെ കർഷകർക്ക് മറ്റ് പ്രദേശങ്ങളെ അപേക്ഷിച്ച് വിളവ് കുറവാണ്.",
        "Organize soil testing and provide better seeds and techniques."
    ),
    "farmer_income_level": (
        "Farming families in this ward earn very low income.",
        "ഈ വാർഡിലെ കർഷക കുടുംബങ്ങൾക്ക് വളരെ കുറഞ്ഞ വരുമാനമാണ്.",
        "Set up farmer markets and value-addition units."
    ),
    "food_security_score": (
        "Some families struggle to get enough food regularly.",
        "ചില കുടുംബങ്ങൾക്ക് പതിവായി ആവശ്യത്തിന് ഭക്ഷണം ലഭിക്കാൻ ബുദ്ധിമുട്ടാണ്.",
        "Start community vegetable gardens (Pachakkari Thottam)."
    ),
    "poverty_rate_bpl_pct": (
        "A large number of families here live below the poverty line.",
        "ഇവിടെ ധാരാളം കുടുംബങ്ങൾ ദാരിദ്ര്യരേഖയ്ക്ക് താഴെ ജീവിക്കുന്നു.",
        "Enroll all eligible families in BPL welfare schemes."
    ),
    "sc_st_population_pct": (
        "This ward has a large SC/ST population needing special support.",
        "ഈ വാർഡിൽ പ്രത്യേക പിന്തുണ ആവശ്യമുള്ള വലിയ SC/ST ജനസംഖ്യയുണ്ട്.",
        "Ensure SC/ST welfare schemes and scholarships reach everyone."
    ),
    "women_empowerment_index": (
        "Women in this ward have fewer opportunities for work and participation.",
        "ഈ വാർഡിലെ സ്ത്രീകൾക്ക് ജോലിക്കും പങ്കാളിത്തത്തിനും അവസരങ്ങൾ കുറവാണ്.",
        "Strengthen Kudumbashree self-help groups and women's enterprises."
    ),
    "disability_support_coverage": (
        "People with disabilities are not getting enough government help.",
        "ഭിന്നശേഷിയുള്ളവർക്ക് ആവശ്യത്തിന് സർക്കാർ സഹായം ലഭിക്കുന്നില്ല.",
        "Conduct a survey and enroll all disabled persons in pension schemes."
    ),
    "pension_coverage_pct": (
        "Many eligible elderly and widows are not receiving their pension.",
        "അർഹരായ പല വയോധികർക്കും വിധവകൾക്കും പെൻഷൻ ലഭിക്കുന്നില്ല.",
        "Set up a help desk to process pending pension applications."
    ),
    "employment_rate": (
        "Many working-age people in this ward do not have jobs.",
        "ഈ വാർഡിലെ ജോലി ചെയ്യാവുന്ന പ്രായത്തിലുള്ള പലർക്കും ജോലിയില്ല.",
        "Organize job fairs and skill training through DDU-GKY."
    ),
    "msme_density": (
        "There are very few small businesses or shops in this area.",
        "ഈ പ്രദേശത്ത് ചെറുകിട ബിസിനസുകളോ കടകളോ വളരെ കുറവാണ്.",
        "Help residents start micro-enterprises through PMEGP loans."
    ),
    "per_capita_income": (
        "People in this ward earn much less compared to other wards.",
        "ഈ വാർഡിലെ ആളുകൾ മറ്റ് വാർഡുകളെ അപേക്ഷിച്ച് വളരെ കുറവ് സമ്പാദിക്കുന്നു.",
        "Promote skill development and entrepreneurship programs."
    ),
    "skill_training_coverage_pct": (
        "Most young people have not received any job skill training.",
        "മിക്ക യുവാക്കൾക്കും ജോലി നൈപുണ്യ പരിശീലനം ലഭിച്ചിട്ടില്ല.",
        "Set up ASAP Kerala skill training centre in the ward."
    ),
    "tourism_potential_index": (
        "The tourism opportunities in this area are not being used.",
        "ഈ പ്രദേശത്തെ ടൂറിസം അവസരങ്ങൾ ഉപയോഗപ്പെടുത്തുന്നില്ല.",
        "Promote homestays and local tourism through Responsible Tourism."
    ),
    "flood_risk_score": (
        "This ward is at high risk of flooding during monsoon season.",
        "മൺസൂൺ സീസണിൽ ഈ വാർഡിന് വെള്ളപ്പൊക്ക ഭീഷണി കൂടുതലാണ്.",
        "Build flood protection bunds and prepare emergency shelters."
    ),
    "waste_management_coverage_pct": (
        "Garbage is not being collected and disposed of properly.",
        "മാലിന്യം ശരിയായി ശേഖരിക്കുകയോ നീക്കം ചെയ്യുകയോ ചെയ്യുന്നില്ല.",
        "Set up ward-level waste collection through Haritha Karma Sena."
    ),
    "green_cover_pct": (
        "Too many trees have been cut down — green cover is very low.",
        "ഒരുപാട് മരങ്ങൾ മുറിച്ചു — ഹരിത ഭൂമി വളരെ കുറവാണ്.",
        "Organize tree planting drives (Pachathuruthu program)."
    ),
    "water_body_health_index": (
        "Ponds and rivers in this area are polluted or drying up.",
        "ഈ പ്രദേശത്തെ കുളങ്ങളും നദികളും മലിനമാണ് അല്ലെങ്കിൽ വറ്റിവരണ്ടിരിക്കുന്നു.",
        "Clean water bodies and prevent waste dumping under MGNREGS."
    ),
    "disaster_preparedness_score": (
        "The ward is not prepared for emergencies like floods or landslides.",
        "വെള്ളപ്പൊക്കം അല്ലെങ്കിൽ ഉരുൾപൊട്ടൽ പോലുള്ള അടിയന്തരാവസ്ഥകൾക്ക് വാർഡ് തയ്യാറല്ല.",
        "Create a ward disaster response plan with shelters and contacts."
    ),
    "internet_penetration_pct": (
        "Most homes do not have internet connection.",
        "മിക്ക വീടുകളിലും ഇൻ്റർനെറ്റ് കണക്ഷൻ ഇല്ല.",
        "Work with KFON/BSNL to extend broadband to this ward."
    ),
    "digital_literacy_pct": (
        "Most people do not know how to use smartphones or computers.",
        "മിക്ക ആളുകൾക്കും സ്മാർട്ട്‌ഫോണോ കമ്പ്യൂട്ടറോ ഉപയോഗിക്കാൻ അറിയില്ല.",
        "Run digital literacy classes for women and senior citizens."
    ),
    "e_service_adoption_rate": (
        "People are not using online government services for certificates etc.",
        "ആളുകൾ സർട്ടിഫിക്കറ്റ് തുടങ്ങിയവയ്ക്ക് ഓൺലൈൻ സർക്കാർ സേവനങ്ങൾ ഉപയോഗിക്കുന്നില്ല.",
        "Set up an Akshaya e-Centre help desk in the ward."
    ),
    "aadhaar_enrollment_pct": (
        "Some residents have not enrolled for Aadhaar yet.",
        "ചില നിവാസികൾ ഇതുവരെ ആധാർ എടുത്തിട്ടില്ല.",
        "Organize an Aadhaar enrollment camp in the ward."
    ),
    "mobile_connectivity_index": (
        "Mobile phone network signal is weak in this area.",
        "ഈ പ്രദേശത്ത് മൊബൈൽ ഫോൺ നെറ്റ്‌വർക്ക് സിഗ്നൽ ദുർബലമാണ്.",
        "Request BSNL/Jio to install a new mobile tower."
    ),
    "population": (
        "This ward has a large population that needs more services.",
        "ഈ വാർഡിൽ കൂടുതൽ സേവനങ്ങൾ ആവശ്യമുള്ള വലിയ ജനസംഖ്യയുണ്ട്.",
        "Scale up all public services proportionally."
    ),
    "population_density": (
        "Too many people live in a small area — services are overcrowded.",
        "ചെറിയ പ്രദേശത്ത് ഒരുപാട് ആളുകൾ താമസിക്കുന്നു — സേവനങ്ങൾ തിങ്ങിനിറഞ്ഞിരിക്കുന്നു.",
        "Expand infrastructure and public services for the density."
    ),
}

SECTOR_NAMES_ML = {
    "Health & Sanitation": "ആരോഗ്യവും ശുചിത്വവും",
    "Education": "വിദ്യാഭ്യാസം",
    "Infrastructure": "അടിസ്ഥാന സൗകര്യം",
    "Agriculture & Food Security": "കൃഷിയും ഭക്ഷ്യ സുരക്ഷയും",
    "Social Welfare": "സാമൂഹ്യ ക്ഷേമം",
    "Economic Development": "സാമ്പത്തിക വികസനം",
    "Environment & Disaster Mgmt": "പരിസ്ഥിതിയും ദുരന്ത നിവാരണവും",
    "Digital & E-Governance": "ഡിജിറ്റൽ & ഇ-ഗവേണൻസ്",
}

SEVERITY_ML = {
    "high": "ഗുരുതരമായ നിലയിൽ",
    "medium": "മിതമായ തോതിൽ",
    "low": "സ്വീകാര്യമായ പരിധിയിൽ",
}
