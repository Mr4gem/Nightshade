 import aiosqlite

  DB_PATH = "nightshade.db"

  async def init_db():
      async with aiosqlite.connect(DB_PATH) as db:
          await db.executescript("""
              CREATE TABLE IF NOT EXISTS warnings (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  guild_id INTEGER NOT NULL,
                  user_id INTEGER NOT NULL,
                  mod_id INTEGER NOT NULL,
                  reason TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
              );
              CREATE TABLE IF NOT EXISTS levels (
                  guild_id INTEGER NOT NULL,
                  user_id INTEGER NOT NULL,
                  xp INTEGER DEFAULT 0,
                  level INTEGER DEFAULT 0,
                  PRIMARY KEY (guild_id, user_id)
              );
              CREATE TABLE IF NOT EXISTS economy (
                  guild_id INTEGER NOT NULL,
                  user_id INTEGER NOT NULL,
                  coins INTEGER DEFAULT 0,
                  last_daily TEXT,
                  PRIMARY KEY (guild_id, user_id)
              );
              CREATE TABLE IF NOT EXISTS guild_settings (
                  guild_id INTEGER PRIMARY KEY,
                  log_channel INTEGER,
                  welcome_channel INTEGER,
                  goodbye_channel INTEGER,
                  welcome_message TEXT DEFAULT 'Welcome {user} to {server}!',
                  goodbye_message TEXT DEFAULT '{user} has left {server}.',
                  starboard_channel INTEGER,
                  starboard_threshold INTEGER DEFAULT 3,
                  automod_enabled INTEGER DEFAULT 1,
                  level_up_channel INTEGER
              );
              CREATE TABLE IF NOT EXISTS starboard_posts (
                  guild_id INTEGER NOT NULL,
                  message_id INTEGER NOT NULL,
                  star_message_id INTEGER NOT NULL,
                  PRIMARY KEY (guild_id, message_id)
              );
              CREATE TABLE IF NOT EXISTS reminders (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  channel_id INTEGER NOT NULL,
                  message TEXT NOT NULL,
                  remind_at TEXT NOT NULL
              );
          """)
          await db.commit()
