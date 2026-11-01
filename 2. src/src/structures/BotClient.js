const { Client, GatewayIntentBits, Collection } = require('discord.js');

class BotClient extends Client {
  constructor() {
    super({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
      ]
    });
    this.commands = new Collection();
  }
}

module.exports = BotClient;
        
