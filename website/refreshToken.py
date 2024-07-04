# import json
# import requests
# from datetime import datetime

# def save_tokens_to_config(new_token, new_refresh_token):
#     config_data = {
#         "Token": f"Bearer {new_token}",
#         "refresh_token": new_refresh_token,
#         "data_token": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     }
#     with open('config_test.json', 'w') as config_file:
#         json.dump(config_data, config_file, indent=4)

# def refresh_token(client_id, client_secret, refresh_token):
#     token_url = 'https://logincert.anaf.ro/anaf-oauth2/v1/token'
#     payload = {
#         'grant_type': 'refresh_token',
#         'refresh_token': refresh_token,
#         'client_id': client_id,
#         'client_secret': client_secret
#     }
#     response = requests.post(token_url, data=payload)
    
#     if response.status_code == 200:
#         new_token_data = response.json()
#         new_token = new_token_data['access_token']
#         new_refresh_token = new_token_data['refresh_token']
#         save_tokens_to_config(new_token, new_refresh_token)
#         return new_token, new_refresh_token
#     else:
#         print("Nu s-a putut actualiza token-ul.")
#         return None, None

# # Exemplu de folosire:
# client_id = '6d066c73333236aad4b780b60fd07e8a7e3ee71def7b2e65'
# client_secret = '387b6fbac332048c656de9411c209f5c98cce3f059cc7e8a7e3ee71def7b2e65'
# refresh_token_value = 'kkV2aNJkGEdRw8E9aWSyfrRQ7Co19wnw8kbD9Rm3U6SPzZEhdnXlEvLoJyNoWukDH6QxJ_ERchjCJq6lDQlTjR5J-VC2gOFRES6FllzCU7HVpT9B5M3cKZtjclemg5N6Ok-HbGizNZ6ANq6yXV2vNDhC6nJ6mze4zH2aBiDcqSgWdf7QFckh1WSexS2X2GHCsPNFXeR3FrrGTVtlUpSeisYbexTe3wvwIAPzzLn3BOHg2BVB8o4cI3DG8chLYAR2KLrsSflF06lHn-aL5jH-iLhTFBDRd7jzbKxIWz9xoe-0M_MWIQU-xf8urokOY5_dDBUUbDo1zld4_tH0sYbVjg_cNPmdFlN6N8Snq5qgL5RqKMYqAFRECJH7G3JxkcVjrYftAJWE7IvywVti2kgq9j9zwPDV4wY2mjBrMmEupjbk4C8NsRvXZwQp60wiPSor514pGySm3at-7Bjyl0JuckcGCjgurxatfzwBwmj40wDUszO_tM__o3dHYWUxifliMrlyrfxFUJJwRfbk2P9-Sj4GSZd_p4-f6TVkPvZ2WisqQoC-C5s2XkpzWxtho-fbisTxr5gUVo4VA6bqYQSzDBDx2ykqJleSCID0vCoR8q4NT5HwRM1vI8RSNV7kclW6a9izPCwRW5N0d5eJNiu3gksS_GY4_Eemona_MzdsX03aZKC1h4Xwmdhf-i0U3TIHT19RzKg74IUYVixDsoRgqOPoXjrSOZRJ6BWcQUOYZ0LYGoo2OFnQmn9vPcYtug9ewBzcyaR7SfLKasJ06RWFe-vPGt30iBHhSuMvL_OkDeZ1RJkv5zCNFJjes0-gj-xkVFzAL6q-cn7cinfojOV5elAr7KlDXQLqVfZokHvO8arCnkc42az5M8gs_0VZgWvuuPBOqqRZAvwr7eSHM-F2Uj6UMf0dx6UtPd1GKRJ2Em31E4oDud0h3AvKDG2ffQI4aJzwJlZcDAKwXpkG4UzoKl-cYk-wwZdl8fik6YtDF-Vs3Ap7pRtXRVxFEkNCaxbwglLkFV_Gu47kvqKlecuI8jPFGV8HQUi15BGtiRu774Ex1ZCbqcgPZRaQvyOZWw1gfobAz9JG45K5_LIyqPOjw9aEwXnVThgOA3KF8Yxg6k23iAcews2b54-JP1ohvzhDZRp5B8d7JpNqnY6ViWCDOEMgl62-XeotI74ThBBwF3Jv0_rF9viwB_TzwwWxXbiIFZ5o-0axYWyYdBy56h__qh_iQp5K8oXUBnN0lcqcItNSr3klj3u1W2_3xJS2dRdyArrSDO1rQcUQbygWfURMprNPwT0GmbBPEtO8LKXBggJZn0R-dJMvMzVOl3l0lxLfXzckwNI2A3SbtEd2J6nlFv3a0Bj3tRV1iraAV_s_FzCruAH_PLxwl9kJnE-lxAEe1fr6g8F1PCWlBFb4rXlM7lgdnbXjgJDNX0EmD34wT40PEjtYggYcU1gFxyxKy7vDxXYEzT_uWdn8mK52qZvEzwKhWIcJg5Qnku-A50TVZnG7ViDRxQ'

# new_token, new_refresh_token = refresh_token(client_id, client_secret, refresh_token_value)
# if new_token:
#     print("Token-ul nou:", new_token)
#     print("Refresh token-ul nou:", new_refresh_token)

import json
import requests
from datetime import datetime

def refreshToken():
    def citeste_configurare(file_path):
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config

    config = citeste_configurare('config.json')
    appData = config['dateFirma']

    def refresh_token(client_id, client_secret, refresh_token, config_file_path):
        token_url = 'https://logincert.anaf.ro/anaf-oauth2/v1/token'
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(token_url, data=payload)
        
        if response.status_code == 200:
            new_token_data = response.json()
            new_token = new_token_data['access_token']
            new_refresh_token = new_token_data['refresh_token']
            save_tokens_to_config(new_token, new_refresh_token, config_file_path)
            return new_token, new_refresh_token
        else:
            print("Nu s-a putut actualiza token-ul.")
            return None, None

    def save_tokens_to_config(new_token, new_refresh_token, config_file_path):
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
        
        config_data["dateFirma"]["header"] = f"Bearer {new_token}"
        config_data["dateFirma"]["refresh_token"] = new_refresh_token
        config_data["dateFirma"]["data_token"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(config_file_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)

    # Exemplu de folosire:
    client_id = appData['client_id']
    client_secret = appData['client_secret']
    refresh_token_value = appData['refresh_token_value']

    config_file_path = 'config.json'

    new_token, new_refresh_token = refresh_token(client_id, client_secret, refresh_token_value, config_file_path)
    if new_token:
        print("Token-ul nou:", new_token)
        print("Refresh token-ul nou:", new_refresh_token)
    print("a rulat REFRESH TOKEN")
# refreshToken()