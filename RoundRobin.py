import random

import PySimpleGUI as sg


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_players(raw_text):
  """Accepts one name per line and/or comma-separated names.

  Blank entries are dropped and duplicates are removed (order preserved).
  """
  names = []
  for line in raw_text.splitlines():
    for part in line.split(","):
      name = part.strip()
      if name and name not in names:
        names.append(name)
  return names


def format_schedule(schedule):
  """Formats the schedule the same way as the original console output."""
  lines = []
  for r_info in schedule:
    lines.append(f"\n--- Round {r_info['round']} ---")
    for m in r_info["matches"]:
      t1 = " & ".join(m["team_1"])
      t2 = " & ".join(m["team_2"])
      lines.append(f"  Court {m['court']}: [{t1}] vs [{t2}]")
    if r_info["sitting_out"]:
      lines.append(f"  Sitting out (Bye): {', '.join(r_info['sitting_out'])}")
  return "\n".join(lines).lstrip("\n")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
def main():
  sg.theme("LightGreen6")

  default_players = "Alex\nJordan\nTaylor\nMorgan\nCasey\nJamie\nRiley\nCameron\nSam"

  input_column = [
      [sg.Text("Players (one per line, or comma-separated)")],
      [sg.Multiline(default_text=default_players, key="-PLAYERS-",
                    size=(30, 14), no_scrollbar=False)],
      [sg.Text("Rounds"),
       sg.Spin(list(range(1, 51)), initial_value=5, key="-ROUNDS-",
               size=(5, 1), readonly=False)],
      [sg.Text("Courts"),
       sg.Spin(list(range(1, 21)), initial_value=2, key="-COURTS-",
               size=(5, 1), readonly=False)],
      [sg.Text("Seed (optional)"),
       sg.Input(key="-SEED-", size=(10, 1))],
      [sg.Button("Shuffle", key="-SHUFFLE-", size=(10, 1)),
       sg.Button("Copy", key="-COPY-", size=(8, 1)),
       sg.Button("Exit", size=(8, 1))],
      [sg.Text("", key="-STATUS-", size=(30, 2), text_color="firebrick")],
  ]

  output_column = [
      [sg.Text("Schedule")],
      [sg.Multiline(key="-OUTPUT-", size=(60, 24), disabled=True,
                    font=("Courier New", 10), autoscroll=False)],
  ]

  layout = [[sg.Column(input_column, vertical_alignment="top"),
             sg.VSeparator(),
             sg.Column(output_column, vertical_alignment="top")]]

  window = sg.Window("Pickleball Mixer", layout, finalize=True)

  while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
      break

    if event == "-SHUFFLE-":
      window["-STATUS-"].update("")

      players_list = parse_players(values["-PLAYERS-"])

      try:
        rounds = int(values["-ROUNDS-"])
        courts = int(values["-COURTS-"])
      except (TypeError, ValueError):
        window["-STATUS-"].update("Rounds and courts must be whole numbers.")
        continue

      seed_text = (values["-SEED-"] or "").strip()
      try:
        seed = int(seed_text) if seed_text else None
      except ValueError:
        window["-STATUS-"].update("Seed must be a whole number (or blank).")
        continue

      if len(players_list) < 4:
        window["-STATUS-"].update("Enter at least 4 players.")
        continue
      if rounds < 1 or courts < 1:
        window["-STATUS-"].update("Rounds and courts must be at least 1.")
        continue

      schedule = generate_pickleball_mixer(
          players=players_list, num_courts=courts, num_rounds=rounds, seed=seed
      )
      window["-OUTPUT-"].update(format_schedule(schedule))

    elif event == "-COPY-":
      sg.clipboard_set(values["-OUTPUT-"])
      window["-STATUS-"].update("Schedule copied to clipboard.")

  window.close()


if __name__ == "__main__":
  main()
