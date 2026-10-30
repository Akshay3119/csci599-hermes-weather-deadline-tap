# Weather/deadline Hermes skill tap

An original, credential-free skill for planning fictional work around live public weather and
calendar conflicts. Initially drafted with OpenAI Codex for an individual coursework project.

The public repository contains only this tap directory. No mailbox data, cloud project settings,
tailnet policy, tokens, logs, or private assignment infrastructure belongs here.

Prerequisites: Hermes Agent and Python 3.12+.

```sh
hermes skills tap add Akshay3119/csci599-hermes-weather-deadline-tap
hermes skills search weather-deadline
```

Inspect the returned identifier with `hermes skills inspect IDENTIFIER`, then install it with
`hermes skills install IDENTIFIER`. Use the search result's identifier in those commands.
The assignment's evidence records the public URL, immutable commit, and an actual fresh installation
and run when verification is complete.

Invoke `/weather-deadline` in Hermes. A standalone helper demonstration is also available:

```sh
cd skills/weather-deadline
python3 scripts/forecast_plan.py --demo
```

The helper calls only Open-Meteo's public HTTPS forecast endpoint for Los Angeles city centre.
It does not use Google, Telegram, local LLM credentials, shell interpolation, or package installation.
Forecast availability and accuracy are outside this skill's control; failures are explicit.

License: MIT. The weather service's terms and attribution requirements continue to apply:
[Open-Meteo](https://open-meteo.com/).
