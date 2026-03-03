import json
with open('logs/simulations/sim_20260303_092254.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        turn = data.get("world_state", {}).get("turn_number")
        if turn is None or turn > 8:
            continue
        us = data["world_state"]["countries"]["アメリカ"]
        factors = us.get("turn_domestic_factors", {})
        print(f"Turn {turn} USA:")
        print(f"  Old GDP: {factors.get('old_gdp', 0):.1f}")
        print(f"  T: {factors.get('T', 0):.1f}")
        print(f"  C: {factors.get('C', 0):.1f}")
        print(f"  I: {factors.get('I', 0):.1f}")
        print(f"  G: {factors.get('G', 0):.1f}")
        print(f"  NX: {factors.get('NX', 0):.1f}")
        print(f"  Growth: {factors.get('economic_growth', 0):.1f}")
        print(f"  New GDP: {us['economy']:.1f}")
        print("-" * 20)
