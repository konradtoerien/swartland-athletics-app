# Primary School Age Groups
AGE_GROUPS = ["u/6", "u/7", "u/8", "u/9", "u/10", "u/11", "u/12", "u/13"]

# Primary School Disciplines mapped by Age Group and Gender
def get_events_for_age_and_gender(age_group: str, gender: str) -> list[str]:
    is_girls = gender.lower().startswith("d") or gender.lower().startswith("g")  # Dogters / Girls
    
    if age_group == "u/6":
        return ["50m"]
    
    elif age_group in ["u/7", "u/8"]:
        return ["60m", "80m"]
    
    elif age_group == "u/9":
        return ["60m", "80m", "100m", "1200m", "Long Jump", "High Jump", "Shot Put"]
    
    elif age_group in ["u/10", "u/11"]:
        return ["60m", "80m", "100m", "1200m", "70m Hurdles", "Long Jump", "High Jump", "Shot Put"]
    
    elif age_group == "u/12":
        return [
            "60m", "80m", "100m", "150m", "1200m", 
            "75m Hurdles", "150m Hurdles", 
            "Long Jump", "High Jump", "Shot Put", "Discus", "Javelin", "1500m Walk"
        ]
    
    elif age_group == "u/13":
        hurdle_event = "75m Hurdles" if is_girls else "80m Hurdles"
        return [
            "80m", "100m", "200m", "1500m", 
            hurdle_event, "200m Hurdles", 
            "Long Jump", "High Jump", "Shot Put", "Discus", "Javelin", "1500m Walk"
        ]
    
    return []

# Master list of all unique disciplines
ALL_DISCIPLINES = [
    "50m", "60m", "80m", "100m", "150m", "200m", 
    "1200m", "1500m", "1500m Walk", 
    "70m Hurdles", "75m Hurdles", "80m Hurdles", "150m Hurdles", "200m Hurdles", 
    "Long Jump", "High Jump", "Shot Put", "Discus", "Javelin"
]