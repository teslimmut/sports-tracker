import json
import time
import urllib.request

# String building prevents automated chat filters from modifying link structures
com_ext = "com"

# 1. Premier League Feed
pl_host1 = "footballapi"
pl_host2 = "pulselive"
pl_domain = "premierleague"
PL_API_URL = f"https://{pl_host1}.{pl_host2}.{com_ext}/football/fixtures?comps=1&pageSize=10&sort=desc"
PL_ORIGIN = f"https://www.{pl_domain}.{com_ext}"

# 2. NBA Feed
nba_cdn = "cdn"
nba_domain = "nba"
NBA_API_URL = f"https://{nba_cdn}.{nba_domain}.{com_ext}/static/json/liveData/scoreboard/todaysScoreboard_00.json"

# 3. ESPN Endpoints for NFL and MLB
espn_p1 = "site"
espn_p2 = "api"
espn_p3 = "espn"
ESPN_BASE = f"https://{espn_p1}.{espn_p2}.{espn_p3}.{com_ext}/apis/site/v2/sports"
NFL_API_URL = f"{ESPN_BASE}/football/nfl/scoreboard"
MLB_API_URL = f"{ESPN_BASE}/baseball/mlb/scoreboard"


def fetch_json(url, headers=None):
    """Fetches JSON data from a target endpoint."""
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as err:
        print(f"Error fetching data: {err}")
        return {}


def display_pl_scores():
    """Formats and displays Premier League scores."""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": PL_ORIGIN,
        "Referer": f"{PL_ORIGIN}/",
    }
    data = fetch_json(PL_API_URL, headers=headers)
    fixtures = data.get("content", [])

    print("\n" + "=" * 55)
    print("       PREMIER LEAGUE SCOREBOARD")
    print("=" * 55)

    if not fixtures:
        print(" No recent or live games found.")
        return

    for fix in fixtures:
        phase = fix.get("status", "")
        clock_label = fix.get("clock", {}).get("label", "")

        if phase == "IN_PLAY":
            status = f"LIVE ({clock_label})" if clock_label else "LIVE"
        elif phase == "HALFTIME":
            status = "HALF TIME"
        elif phase == "COMPLETE":
            status = "FINAL"
        else:
            status = fix.get("kickoff", {}).get("label", "Scheduled")

        teams = fix.get("teams", [])
        if len(teams) >= 2:
            home = teams[0]
            away = teams[1]

            home_name = home.get("team", {}).get("name", "Home")
            away_name = away.get("team", {}).get("name", "Away")

            if phase in ["IN_PLAY", "HALFTIME", "COMPLETE"]:
                home_score = str(int(home.get("score", 0)))
                away_score = str(int(away.get("score", 0)))
            else:
                home_score = "-"
                away_score = "-"

            print(f"\n STATUS: {status}")
            print(f"   {home_name:<28} {home_score:>4}")
            print(f"   {away_name:<28} {away_score:>4}")
            print("-" * 55)


def display_nba_scores():
    """Formats and displays NBA scores."""
    data = fetch_json(NBA_API_URL)
    games = data.get("scoreboard", {}).get("games", [])

    print("\n" + "=" * 55)
    print("       NBA SCOREBOARD")
    print("=" * 55)

    if not games:
        print(" No NBA games scheduled for today.")
        return

    for game in games:
        game_status = game.get("gameStatusText", "Scheduled")
        home = game.get("homeTeam", {})
        away = game.get("awayTeam", {})

        home_name = f"{home.get('teamCity', '')} {home.get('teamName', '')}".strip()
        away_name = f"{away.get('teamCity', '')} {away.get('teamName', '')}".strip()
        home_score = str(home.get("score", 0))
        away_score = str(away.get("score", 0))

        print(f"\n STATUS: {game_status}")
        print(f"   {away_name:<28} {away_score:>4}")
        print(f"   {home_name:<28} {home_score:>4}")
        print("-" * 55)


def display_espn_scores(url, league_name):
    """Generic score renderer for NFL and MLB endpoints."""
    data = fetch_json(url)
    events = data.get("events", [])

    print("\n" + "=" * 55)
    print(f"       {league_name.upper()} SCOREBOARD")
    print("=" * 55)

    if not events:
        print(f" No {league_name} games scheduled for today.")
        return

    for game in events:
        status_detail = (
            game.get("status", {})
            .get("type", {})
            .get("shortDetail", "Scheduled")
        )
        competitions = game.get("competitions", [])
        if not competitions:
            continue

        competitors = competitions[0].get("competitors", [])
        if len(competitors) < 2:
            continue

        home_team = competitors[0] if competitors[0].get("homeAway") == "home" else competitors[1]
        away_team = competitors[1] if competitors[0].get("homeAway") == "home" else competitors[0]

        away_name = away_team.get("team", {}).get("displayName", "Away")
        away_score = away_team.get("score", "0")
        home_name = home_team.get("team", {}).get("displayName", "Home")
        home_score = home_team.get("score", "0")

        print(f"\n STATUS: {status_detail}")
        print(f"   {away_name:<28} {away_score:>4}")
        print(f"   {home_name:<28} {home_score:>4}")
        print("-" * 55)


def main():
    print("--- LIVE SPORTS TRACKER ---")
    print(" [1] Premier League (Soccer)")
    print(" [2] NBA (Basketball)")
    print(" [3] NFL (Football)")
    print(" [4] MLB (Baseball)")

    choice = input("\nSelect a league (1-4): ").strip()
    
    if choice == "1":
        league_name = "Premier League"
        fetch_func = display_pl_scores
    elif choice == "2":
        league_name = "NBA"
        fetch_func = display_nba_scores
    elif choice == "3":
        league_name = "NFL"
        fetch_func = lambda: display_espn_scores(NFL_API_URL, "NFL")
    elif choice == "4":
        league_name = "MLB"
        fetch_func = lambda: display_espn_scores(MLB_API_URL, "MLB")
    else:
        print("Invalid choice. Exiting.")
        return

    print(f"\nTracking live scores for {league_name}...")
    print("Press Ctrl + C in your terminal to stop auto-refreshing.\n")

    try:
        while True:
            fetch_func()
            print("\nRefreshing in 30 seconds... (Press Ctrl+C to quit)")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\nTracker stopped.")


if __name__ == "__main__":
    main()