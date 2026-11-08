import random
def generate_pickleball_mixer(players, num_courts, num_rounds, seed=None):
  """Generates a rotating-doubles pickleball round-robin schedule.

    Parameters:
        players (list): List of player names.
        num_courts (int): Number of available courts.
        num_rounds (int): Total number of rounds to play.
        seed (int, optional): Random seed for reproducible schedules.

    Returns:
        list: A list of rounds, where each round contains a list of court assignments.
    """
  if seed is not None:
    random.seed(seed)

  player_pool = list(players)
  schedule = []
  sit_out_counts = {p: 0 for p in players}

  for r in range(1, num_rounds + 1):
    round_data = {"round": r, "matches": [], "sitting_out": []}

    # Determine how many players can play vs. need to sit out
    max_players_on_court = num_courts * 4
    shuffled_players = player_pool[:]

    # Players who have sat out the MOST get priority to play;
    # ties are broken randomly so byes are still random among equals
    shuffled_players.sort(key=lambda p: (-sit_out_counts[p], random.random()))

    active_players = shuffled_players[:max_players_on_court]
    sitting_out = shuffled_players[max_players_on_court:]

    for p in sitting_out:
      sit_out_counts[p] += 1
      round_data["sitting_out"].append(p)

    # Shuffle active players to randomize partnerships
    random.shuffle(active_players)

    matches = []
    for c in range(num_courts):
      court_idx = c * 4
      if court_idx + 4 <= len(active_players):
        court_group = active_players[court_idx : court_idx + 4]
        match = {
            "court": c + 1,
            "team_1": (court_group[0], court_group[1]),
            "team_2": (court_group[2], court_group[3]),
        }
        matches.append(match)

    round_data["matches"] = matches
    schedule.append(round_data)

  return schedule

# --- Example Usage ---
if __name__ == "__main__":
  players_list = [
      "Alex",
      "Jordan",
      "Taylor",
      "Morgan",
      "Casey",
      "Jamie",
      "Riley",
      "Cameron",
      "Sam"
  ]
  courts = 2
  rounds = 5

  schedule = generate_pickleball_mixer(
      players=players_list, num_courts=courts, num_rounds=rounds, seed=42
  )

  for r_info in schedule:
    print(f"\n--- Round {r_info['round']} ---")
    for m in r_info["matches"]:
      t1 = " & ".join(m["team_1"])
      t2 = " & ".join(m["team_2"])
      print(f"  Court {m['court']}: [{t1}] vs [{t2}]")
    if r_info["sitting_out"]:
      print(f"  Sitting out (Bye): {', '.join(r_info['sitting_out'])}")
