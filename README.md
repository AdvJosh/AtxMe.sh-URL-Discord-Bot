# ATxMe.sh URL Discord Bot

A Discord bot that allows managing short links created by the [Sink](https://github.com/emersion/sink) project. This bot enables Discord users to create, manage, and track URL shortlinks through simple commands.

## Setup Instructions

### Prerequisites
- Python 3.x
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Access to a Sink API instance
- Discord Server with appropriate roles configured

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AtxMe.sh-URL-Discord-Bot.git
cd AtxMe.sh-URL-Discord-Bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration

1. Copy the example environment file to create your own:
```bash
cp .env.example .env
```

2. Edit the `.env` file and fill in your configuration:
- `TOKEN`: Your Discord bot token from the Discord Developer Portal
- `SINK_TOKEN`: Your Sink API authentication token
- `SINK_API_URL`: The base URL of your Sink API instance (e.g., https://atxme.sh/api/v1/)
- `URL_ADMIN_ROLES`: A list of Discord role IDs that will have admin access (e.g., [123456789, 987654321]). Get this by right clicking the role name in Discord and selecting "Copy ID"
- `DEV_GUILD_ID`: Your development Discord server ID. Get this by right clicking the server name in Discord and selecting "Copy ID"

Example `.env` file:
```env
TOKEN=your_discord_bot_token_here
SINK_TOKEN=your_sink_api_token_here
SINK_API_URL=https://atxme.sh/api/v1/
URL_ADMIN_ROLES=[123456789, 987654321]
DEV_GUILD_ID=123456789
```

### Running the Bot

1. Start the bot:
```bash
python main.py
```

2. The bot should now be online in your Discord server and ready to accept commands.

## Usage

[Usage instructions to be added]

## Contributing

[Contributing guidelines to be added]

## License

[License information to be added]
