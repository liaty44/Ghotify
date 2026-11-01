class Command {
  constructor(client, options) {
    this.client = client;
    this.name = options.name;
    this.description = options.description || "No description provided.";
    this.category = options.category || "General";
    this.botPermissions = options.botPermissions || [];
    this.userPermissions = options.userPermissions || [];
    this.command = options.command || {};
  }
}

module.exports = Command;
