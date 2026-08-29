# Nightshade

  A feature-rich Discord bot built for community servers. Nightshade handles moderation, server utilities, leveling, economy, and fun commands — all with a dark, mysterious personality.

  ---

  ## Setup

  After inviting Nightshade to your server, run `/setup` to configure your channels:

  | Option | Description |
  |--------|-------------|
  | `log_channel` | Where mod actions are logged |
  | `welcome_channel` | Where new member messages appear |
  | `goodbye_channel` | Where leave messages appear |
  | `starboard_channel` | Where starred messages are pinned |
  | `level_up_channel` | Where level-up announcements appear |

  ---

  ## Commands

  ### Moderation
  | Command | Description | Permission Required |
  |---------|-------------|---------------------|
  | `/kick <member> [reason]` | Kick a member from the server | Kick Members |
  | `/ban <member> [reason] [delete_days]` | Ban a member | Ban Members |
  | `/unban <user_id>` | Unban a user by their ID | Ban Members |
  | `/timeout <member> <minutes> [reason]` | Temporarily mute a member | Moderate Members |
  | `/warn <member> <reason>` | Warn a member (auto-timeout at 3, auto-ban at 5) | Kick Members |
  | `/warnings <member>` | View a member's warning history | Kick Members |
  | `/clearwarns <member>` | Clear all warnings for a member | Administrator |
  | `/purge <amount>` | Delete 1–100 messages at once | Manage Messages |

  ### Fun
  | Command | Description |
  |---------|-------------|
  | `/8ball <question>` | Ask the magic 8 ball a question |
  | `/rps <rock/paper/scissors>` | Play rock, paper, scissors against Nightshade |
  | `/slots` | Spin the slot machine |
  | `/trivia` | Answer a random trivia question in chat |
  | `/poll <question> <options>` | Create a reaction poll (comma-separated options) |
  | `/coinflip` | Flip a coin |

  ### Leveling
  | Command | Description |
  |---------|-------------|
  | `/rank [member]` | View your XP, level, and progress bar |
  | `/leaderboard` | View the top 10 members by XP |

  > XP is earned by chatting (15–25 XP per message, once per minute). Level-up announcements post in your configured channel.

  ### Economy
  | Command | Description |
  |---------|-------------|
  | `/balance [member]` | Check your coin balance |
  | `/daily` | Claim 500–1000 coins once per day |
  | `/gamble <amount>` | Gamble coins for a chance to win 1.8x |
  | `/give <member> <amount>` | Give coins to another member |
  | `/richlist` | View the top 10 richest members |

  ### Utility
  | Command | Description |
  |---------|-------------|
  | `/serverinfo` | View server details |
  | `/userinfo [member]` | View a member's profile info |
  | `/remind <time> <message>` | Set a reminder (e.g. `10m`, `2h`, `1d`) |
  | `/ticket [reason]` | Open a private support thread |
  | `/setup` | Configure Nightshade for this server (Administrator only) |

  ### Personality
  | Command | Description |
  |---------|-------------|
  | `/nightshade` | Receive a cryptic message from Nightshade |
  | `/about` | Learn about Nightshade |

  ---

  ## Auto-Moderation

  Nightshade automatically monitors messages for:

  - **Spam** — Deletes messages if a user sends 5+ in 5 seconds
  - **Invite links** — Removes Discord invite links posted in chat
  - **Bad words** — Filters a configurable list of banned words

  All actions are logged to your configured log channel.

  ---

  ## Starboard

  React to any message with ⭐ — once it hits the threshold (default: 3 stars), it gets pinned to your starboard channel automatically.

  ---

  ## Keyword Triggers

  Nightshade listens for certain phrases and responds automatically:

  | Phrase | Response |
  |--------|----------|
  | `good bot` | *Your praise fuels me. Don't make it a habit.* |
  | `bad bot` | *Bold words for someone within banning range.* |
  | `hello nightshade` | *Hello. I see you.* |
  | `good morning` | *The darkness fades... for now. Good morning.* |
  | `good night` | *Sleep well. I'll be here when you return.* |

  ---

  ## Hosting

  Nightshade is hosted on [Railway](https://railway.app). Data is stored in a local SQLite database (`nightshade.db`).

  ---

  *The night is long. Nightshade is longer.*
