import soccerdata as sd
import pandas as pd

# Configurar pandas para visualización completa en terminal
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("=============================================================")
print(" PIPELINE PREMIER LEAGUE (2023-2024): TABLA, PARTIDOS Y GOLEADORES")
print("=============================================================\n")

league = "ENG-Premier League"
season = "2023"

# =============================================================
# 1. TABLA DE POSICIONES GENERAL (FBREF)
# =============================================================
print("--- 📊 1. TABLA DE POSICIONES COMPLETA ---")
fbref = sd.FBref(leagues=league, seasons=season)
schedule = fbref.read_schedule().reset_index()

# Filtrar partidos jugados y procesar marcadores
schedule_played = schedule.dropna(subset=['score']).copy()
scores = schedule_played['score'].str.extract(r'(\d+)[\r\n\t\s]*[–-][\r\n\t\s]*(\d+)')
schedule_played['home_score'] = pd.to_numeric(scores[0])
schedule_played['away_score'] = pd.to_numeric(scores[1])
schedule_played = schedule_played.dropna(subset=['home_score', 'away_score'])

# Armar estructura de la tabla
teams = pd.unique(schedule_played[['home_team', 'away_team']].values.ravel())
table = {team: {'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0} for team in teams}

for _, row in schedule_played.iterrows():
    h_team, a_team = row['home_team'], row['away_team']
    h_score, a_score = int(row['home_score']), int(row['away_score'])

    table[h_team]['PJ'] += 1
    table[h_team]['GF'] += h_score
    table[h_team]['GC'] += a_score

    table[a_team]['PJ'] += 1
    table[a_team]['GF'] += a_score
    table[a_team]['GC'] += h_score

    if h_score > a_score:
        table[h_team]['PG'] += 1
        table[h_team]['Pts'] += 3
        table[a_team]['PP'] += 1
    elif h_score < a_score:
        table[a_team]['PG'] += 1
        table[a_team]['Pts'] += 3
        table[h_team]['PP'] += 1
    else:
        table[h_team]['PE'] += 1
        table[h_team]['Pts'] += 1
        table[a_team]['PE'] += 1
        table[a_team]['Pts'] += 1

df_table = pd.DataFrame.from_dict(table, orient='index').reset_index()
df_table.rename(columns={'index': 'Equipo'}, inplace=True)
df_table['DG'] = df_table['GF'] - df_table['GC']
df_table = df_table.sort_values(by=['Pts', 'DG', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
df_table.index += 1

print(df_table.to_string())

# =============================================================
# 2. CONSULTA DE PARTIDOS (MANCHESTER CITY)
# =============================================================
equipo_consulta = "Manchester City"
print(f"\n--- 🗓️ 2. HISTORIAL DE PARTIDOS DEL {equipo_consulta.upper()} ---")

mcfc_matches = schedule[
    (schedule['home_team'] == equipo_consulta) | (schedule['away_team'] == equipo_consulta)
].copy()

cols_p = ['date', 'week', 'home_team', 'away_team', 'score']
cols_p_existentes = [c for c in cols_p if c in mcfc_matches.columns]
print(mcfc_matches[cols_p_existentes].head(10).to_string(index=False))

# =============================================================
# 3. TABLA DE GOLEADORES (UNDERSTAT - SIN CAPTCHA)
# =============================================================
print(f"\n--- ⚽ 3. TABLA DE GOLEADORES ---")
try:
    understat = sd.Understat(leagues=league, seasons=season)
    player_stats = understat.read_player_season_stats().reset_index()

    player_stats['goals'] = pd.to_numeric(player_stats['goals'], errors='coerce')
    top_goleadores = player_stats.sort_values(by='goals', ascending=False).reset_index(drop=True)
    top_goleadores.index += 1

    cols_g = ['player', 'team', 'goals', 'assists', 'xg', 'key_passes']
    cols_g_existentes = [c for c in cols_g if c in top_goleadores.columns]

    print("\nTop 15 Goleadores de la Liga:")
    print(top_goleadores[cols_g_existentes].head(15).to_string())

    print(f"\nTop Goleadores del {equipo_consulta}:")
    mcfc_goleadores = top_goleadores[top_goleadores['team'] == equipo_consulta]
    print(mcfc_goleadores[cols_g_existentes].head(5).to_string())

except Exception as e:
    print(f"❌ Error al consultar goleadores: {e}")

print("\n=============================================================")
print(" CONSULTA COMPLETADA")
print("=============================================================")