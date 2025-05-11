import requests
import pandas as pd


def search_medication_location(patient_location, GOOGLE_API_KEY):
    def _get_lat_lng(address):
        geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": GOOGLE_API_KEY}
        
        response = requests.get(geo_url, params=params).json()
        print(response)
        if response["status"] == "OK":
            location = response["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        return None, None

    def _search_nearby(lat, lng, keyword):
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": 3000,  # 半徑 3 公里內
            "keyword": keyword,
            "language": "zh-TW",
            "key": GOOGLE_API_KEY
        }
        response = requests.get(places_url, params=params).json()
        results = []
        for place in response.get("results", []):
            name = place.get("name")
            address = place.get("vicinity")
            if name and address:
                results.append({"name": name, "address": address})
        return results

    def _format_clinic_list(clinic_list):
        return "\n".join(f"{clinic['name']} - {clinic['address'].lstrip('·')}" for clinic in clinic_list)

    all_results = []
    for input_address in patient_location:
        lat, lng = _get_lat_lng(input_address)
        if lat is None:
            all_results.append({
                "診所": "找不到座標",
                "醫院": "找不到座標",
                "藥局": "找不到座標"
            })
            continue

        clinics = _search_nearby(lat, lng, "診所")
        hospitals = _search_nearby(lat, lng, "醫院")
        pharmacies = _search_nearby(lat, lng, "藥局")

        all_results.append({
            "診所": _format_clinic_list(clinics),
            "醫院": _format_clinic_list(hospitals),
            "藥局": _format_clinic_list(pharmacies)
        })

    result_df = pd.DataFrame(all_results)
    return result_df

# locations = ["台北市大安區敦化南路二段218號"]
# df = search_medication_location(locations)
# print(df)