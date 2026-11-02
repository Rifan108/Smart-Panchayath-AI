"""
Kerala Geography and Administrative Hierarchy
Contains all 14 Districts of Kerala and representative Grama Panchayats
with geographic profiles and ward counts.
"""

KERALA_DISTRICTS_DATA = {
    "Kasaragod": {
        "panchayats": {
            "Manjeshwar": {"profile": "coastal_border", "wards": 24, "pop": 41515},
            "Kumbla": {"profile": "coastal", "wards": 23, "pop": 35964},
            "Madhur": {"profile": "semi_urban", "wards": 20, "pop": 37842},
            "Nileshwaram": {"profile": "riverine", "wards": 24, "pop": 54789},
            "Trikaripur": {"profile": "coastal_estuary", "wards": 17, "pop": 34500},
        }
    },
    "Kannur": {
        "panchayats": {
            "Payyanur": {"profile": "semi_urban", "wards": 24, "pop": 72111},
            "Thalassery": {"profile": "coastal_urban", "wards": 24, "pop": 92558},
            "Dharmadam": {"profile": "coastal", "wards": 19, "pop": 30804},
            "Mattannur": {"profile": "semi_urban", "wards": 22, "pop": 47078},
        }
    },
    "Wayanad": {
        "panchayats": {
            "Kalpetta": {"profile": "highland", "wards": 20, "pop": 31561},
            "Sultan Bathery": {"profile": "highland_border", "wards": 23, "pop": 45417},
            "Meenangadi": {"profile": "highland_carbon_neutral", "wards": 19, "pop": 33450},
            "Mananthavady": {"profile": "highland_tribal", "wards": 22, "pop": 45077},
        }
    },
    "Kozhikode": {
        "panchayats": {
            "Beypore": {"profile": "coastal_port", "wards": 23, "pop": 69773},
            "Kunnamangalam": {"profile": "semi_urban_edu", "wards": 23, "pop": 53392},
            "Balussery": {"profile": "rural_valley", "wards": 19, "pop": 35528},
            "Vadakara": {"profile": "coastal_urban", "wards": 24, "pop": 75295},
        }
    },
    "Malappuram": {
        "panchayats": {
            "Nilambur": {"profile": "forest_fringe", "wards": 22, "pop": 46366},
            "Tirur": {"profile": "coastal_semi_urban", "wards": 24, "pop": 56058},
            "Perinthalmanna": {"profile": "semi_urban_health", "wards": 23, "pop": 49723},
            "Kondotty": {"profile": "semi_urban_airport", "wards": 22, "pop": 59256},
        }
    },
    "Palakkad": {
        "panchayats": {
            "Chittur": {"profile": "agricultural_plain", "wards": 22, "pop": 31884},
            "Mannarkkad": {"profile": "valley_tribal", "wards": 21, "pop": 45098},
            "Alathur": {"profile": "agricultural_paddy", "wards": 16, "pop": 26720},
            "Ottapalam": {"profile": "riverine_semi_urban", "wards": 23, "pop": 53792},
        }
    },
    "Thrissur": {
        "panchayats": {
            "Wadakkanchery": {"profile": "semi_urban", "wards": 23, "pop": 61341},
            "Chalakudy": {"profile": "riverine_tourist", "wards": 23, "pop": 49525},
            "Ollur": {"profile": "industrial_suburb", "wards": 20, "pop": 33880},
            "Kodungallur": {"profile": "coastal_heritage", "wards": 22, "pop": 33543},
        }
    },
    "Ernakulam": {
        "panchayats": {
            "Aluva": {"profile": "urban_industrial", "wards": 22, "pop": 22428},
            "Kalamassery": {"profile": "urban_industrial", "wards": 24, "pop": 71038},
            "Kothamangalam": {"profile": "foothill_edu", "wards": 21, "pop": 38837},
            "Kumbalangi": {"profile": "coastal_eco_tourism", "wards": 17, "pop": 28487},
        }
    },
    "Idukki": {
        "panchayats": {
            "Munnar": {"profile": "highland_plantation", "wards": 21, "pop": 32029},
            "Nedumkandam": {"profile": "highland_spices", "wards": 22, "pop": 37970},
            "Thodupuzha": {"profile": "foothill_edu", "wards": 23, "pop": 52045},
            "Adimali": {"profile": "highland_tribal", "wards": 21, "pop": 32866},
            "Vazhathope": {"profile": "highland_dam_hq", "wards": 14, "pop": 24200},
        }
    },
    "Kottayam": {
        "panchayats": {
            "Kumarakom": {"profile": "backwater_tourism", "wards": 16, "pop": 23003},
            "Pala": {"profile": "rubber_commercial", "wards": 22, "pop": 22056},
            "Changanassery": {"profile": "semi_urban_paddy", "wards": 23, "pop": 47691},
            "Vaikom": {"profile": "backwater_cultural", "wards": 20, "pop": 23234},
            "Kottayam Rural": {"profile": "semi_urban_rubber", "wards": 22, "pop": 38000},
        }
    },
    "Alappuzha": {
        "panchayats": {
            "Kuttanad": {"profile": "wetland_below_sea", "wards": 18, "pop": 24105},
            "Ambalappuzha": {"profile": "coastal_heritage", "wards": 19, "pop": 29088},
            "Cherthala": {"profile": "coastal_industrial", "wards": 23, "pop": 45827},
            "Mavelikkara": {"profile": "cultural_semi_urban", "wards": 21, "pop": 26441},
        }
    },
    "Pathanamthitta": {
        "panchayats": {
            "Ranni": {"profile": "riverine_hilly", "wards": 13, "pop": 13880},
            "Konni": {"profile": "forest_eco_tourism", "wards": 18, "pop": 31100},
            "Adoor": {"profile": "semi_urban_transit", "wards": 22, "pop": 28943},
            "Thiruvalla": {"profile": "semi_urban_paddy", "wards": 23, "pop": 52883},
        }
    },
    "Kollam": {
        "panchayats": {
            "Sasthamkotta": {"profile": "freshwater_lake", "wards": 19, "pop": 33285},
            "Kundara": {"profile": "industrial_suburb", "wards": 20, "pop": 33934},
            "Karunagappally": {"profile": "coastal_industrial", "wards": 24, "pop": 45336},
            "Chathannoor": {"profile": "suburban_foothill", "wards": 18, "pop": 35419},
        }
    },
    "Thiruvananthapuram": {
        "panchayats": {
            "Kazhakkoottam": {"profile": "tech_hub_urban", "wards": 24, "pop": 54200},
            "Varkala": {"profile": "coastal_tourism", "wards": 22, "pop": 40048},
            "Neyyattinkara": {"profile": "southern_border", "wards": 24, "pop": 70850},
            "Nedumangad": {"profile": "suburban_foothill", "wards": 23, "pop": 60161},
        }
    },
}

# Terrain profile modifiers
PROFILE_TERRAIN_MODIFIERS = {
    "coastal": {"flood_risk": 1.45, "water_body": 1.30, "cultivable": 0.70, "tourism": 1.40, "digital": 1.05},
    "coastal_border": {"flood_risk": 1.35, "water_body": 1.20, "cultivable": 0.85, "tourism": 1.20, "digital": 0.95},
    "coastal_port": {"flood_risk": 1.40, "msme": 1.35, "employment": 1.15, "digital": 1.15, "waste": 1.25},
    "coastal_urban": {"flood_risk": 1.30, "msme": 1.30, "doctor": 1.25, "digital": 1.25, "poverty": 0.85},
    "coastal_tourism": {"flood_risk": 1.35, "tourism": 1.70, "per_capita": 1.20, "waste": 1.35, "digital": 1.20},
    "coastal_industrial": {"flood_risk": 1.25, "msme": 1.40, "disease": 1.15, "water_body": 0.85, "digital": 1.10},
    "coastal_heritage": {"flood_risk": 1.30, "tourism": 1.35, "pension": 1.15, "digital": 1.05},
    "highland": {"green_cover": 1.45, "flood_risk": 0.70, "road_access": 0.75, "farmer_income": 1.20, "digital": 0.85},
    "highland_border": {"green_cover": 1.35, "road_access": 0.80, "poverty": 1.15, "sc_st": 1.35, "digital": 0.80},
    "highland_carbon_neutral": {"green_cover": 1.50, "waste": 1.40, "water_body": 1.35, "digital": 1.10},
    "highland_tribal": {"sc_st": 1.80, "literacy": 0.90, "poverty": 1.30, "green_cover": 1.45, "doctor": 0.75},
    "highland_plantation": {"farmer_income": 1.25, "green_cover": 1.40, "tourism": 1.60, "road_access": 0.75},
    "highland_tourist": {"tourism": 1.75, "green_cover": 1.40, "waste": 1.20, "road_access": 0.80},
    "highland_spices": {"farmer_income": 1.30, "cultivable": 1.25, "green_cover": 1.35, "msme": 1.10},
    "highland_commercial": {"per_capita": 1.15, "msme": 1.25, "doctor": 1.10, "digital": 1.10},
    "wetland_below_sea": {"flood_risk": 1.80, "water_body": 1.50, "cultivable": 1.30, "road_access": 0.70, "safe_water": 0.85},
    "paddy_wetland": {"flood_risk": 1.50, "cultivable": 1.35, "irrigation": 1.40, "water_body": 1.30},
    "riverine": {"flood_risk": 1.30, "water_body": 1.40, "irrigation": 1.25, "cultivable": 1.15},
    "riverine_semi_urban": {"water_body": 1.25, "msme": 1.15, "literacy": 1.05, "digital": 1.10},
    "riverine_tourist": {"tourism": 1.45, "water_body": 1.35, "green_cover": 1.20, "digital": 1.10},
    "riverine_agricultural": {"cultivable": 1.25, "irrigation": 1.30, "water_body": 1.30},
    "riverine_hilly": {"flood_risk": 1.25, "green_cover": 1.30, "water_body": 1.25, "road_access": 0.85},
    "agricultural_plain": {"cultivable": 1.45, "irrigation": 1.35, "crop_yield": 1.25, "farmer_income": 1.15},
    "agricultural_paddy": {"cultivable": 1.40, "irrigation": 1.40, "crop_yield": 1.30, "food_security": 1.20},
    "forest_fringe": {"green_cover": 1.60, "sc_st": 1.40, "road_access": 0.75, "disaster": 1.20, "digital": 0.75},
    "forest_eco_tourism": {"green_cover": 1.55, "tourism": 1.40, "water_body": 1.25, "digital": 0.90},
    "foothill_edu": {"literacy": 1.08, "digital_classroom": 1.30, "student_teacher": 0.85, "digital": 1.15},
    "foothill_riverine": {"water_body": 1.30, "green_cover": 1.25, "flood_risk": 1.15},
    "urban_industrial": {"per_capita": 1.35, "msme": 1.50, "employment": 1.25, "digital": 1.35, "green_cover": 0.65},
    "tech_hub_urban": {"digital": 1.60, "internet": 1.50, "e_service": 1.55, "per_capita": 1.40, "literacy": 1.08},
    "semi_urban": {"development": 1.08, "digital": 1.12, "vulnerability": 0.95},
    "semi_urban_edu": {"literacy": 1.06, "digital": 1.20, "digital_classroom": 1.25},
    "semi_urban_health": {"hospital_beds": 1.40, "doctor": 1.35, "vaccination": 1.08},
    "semi_urban_airport": {"msme": 1.25, "per_capita": 1.20, "digital": 1.20},
    "semi_urban_transit": {"road_connectivity": 1.20, "public_transport": 1.25, "msme": 1.15},
    "semi_urban_paddy": {"cultivable": 1.15, "literacy": 1.05, "digital": 1.10},
    "suburban_foothill": {"road_connectivity": 1.10, "digital": 1.15, "msme": 1.15},
    "southern_border": {"sc_st": 1.15, "poverty": 1.10, "digital": 1.05},
    "rubber_commercial": {"farmer_income": 1.35, "per_capita": 1.25, "literacy": 1.06},
    "temple_town_urban": {"tourism": 1.30, "msme": 1.20, "digital": 1.15},
    "backwater_cultural": {"water_body": 1.40, "tourism": 1.35, "flood_risk": 1.30},
    "cultural_semi_urban": {"literacy": 1.06, "women_empowerment": 1.15, "digital": 1.12},
    "cultural_riverine": {"water_body": 1.30, "literacy": 1.06, "pension": 1.15},
    "industrial_suburb": {"msme": 1.40, "employment": 1.20, "per_capita": 1.20},
    "rock_tourism_rural": {"tourism": 1.35, "cultivable": 0.90, "rural": 1.10},
    "rural_valley": {"cultivable": 1.20, "green_cover": 1.25, "digital": 0.85},
    "valley_tribal": {"sc_st": 1.50, "poverty": 1.25, "green_cover": 1.35, "doctor": 0.80},
}
