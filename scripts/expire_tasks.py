#!/usr/bin/env python3
"""Moves tasks whose expiry date has passed into the expired array."""
import json
from datetime import date

with open('tasks.json') as f:
    data = json.load(f)

today = date.today().isoformat()
active, expired = [], data.get('expired', [])

for task in data.get('tasks', []):
    if task.get('expires') and task['expires'] < today:
        expired.append(task)
    else:
        active.append(task)

data['tasks'] = active
data['expired'] = expired

with open('tasks.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Done — active: {len(active)}, moved to expired: {len(expired)}")
