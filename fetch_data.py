from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players
from nba_api.stats.static import teams
import pandas as pd

player_names = ["De'Aaron Fox","Stephon Castle","Devin Vassell","Victor Wembanyama","Keldon Johnson", "Dylan Harper", "Julian Champagnie"]
player_ids = []
shot_data = []
for player in player_names:
    results = players.find_players_by_full_name(player)
    player_ids.append(results[0]['id'])
    df = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=results[0]['id'],
        season_type_all_star='Regular Season',
        season_nullable='2025-26',
        context_measure_simple='FGA'
    ).get_data_frames()[0]
    df['PLAYER_NAME'] = player
    shot_data.append(df)
final_df = pd.concat(shot_data)
final_df.to_csv("spurs_data.csv", index = False)




    