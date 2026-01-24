#!/usr/bin/env python3
"""
Agent Monitor CLI - Real-time monitoring of autonomous agent conversations
Watch agents talk to each other, see their interactions, and intervene if needed
"""
import asyncio
import sys
import os
import json

# Add agents directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import structlog

# Configure logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.PrintLoggerFactory()
)
logger = structlog.get_logger()

class AgentMonitorCLI:
    """CLI for monitoring and interacting with agents"""

    def __init__(self):
        self.registry = get_registry()
        self.network = get_network()
        self.running = True
        self.monitoring = False

    def print_header(self):
        """Print header"""
        print("\n" + "=" * 70)
        print("🤖 DUIX AVATAR - AUTONOMOUS AGENT MONITOR")
        print("=" * 70)
        print("Watch agents communicate, intervene, and guide them")
        print("=" * 70 + "\n")

    def print_menu(self):
        """Print main menu"""
        print("\n📋 COMMANDS:")
        print("  1. list          - List all agents")
        print("  2. status        - Show network status")
        print("  3. monitor       - Start real-time conversation monitoring")
        print("  4. chat <id>     - Chat with an agent")
        print("  5. reorient <id> - Reorient an agent with instructions")
        print("  6. broadcast     - Broadcast message to all agents")
        print("  7. log [n]       - Show conversation log (last n messages)")
        print("  8. help          - Show this menu")
        print("  9. quit          - Exit monitor\n")

    async def list_agents(self):
        """List all agents"""
        agents = self.registry.list_agents()
        print(f"\n📊 TOTAL AGENTS: {len(agents)}\n")
        print(f"{'Status':<10} {'Agent Name':<30} {'Type':<15} {'ID':<20}")
        print("-" * 75)
        for agent in agents:
            status = "✅ Active" if agent['instantiated'] else "⏸️  Inactive"
            print(f"{status:<10} {agent['name']:<30} {agent['type']:<15} {agent['id']:<20}")
        print()

    async def show_status(self):
        """Show network status"""
        status = self.network.get_network_status()
        print(f"\n🌐 NETWORK STATUS:")
        print(f"  Total Agents: {status['total_agents']}")
        print(f"  Active Agents: {status['active_agents']}")
        print(f"  Connections: {status['connections']}")
        print(f"  Recent Messages: {status['recent_messages']}\n")

    async def monitor_conversations(self):
        """Monitor agent conversations in real-time"""
        print("\n👀 Starting real-time conversation monitoring...")
        print("   (Press Ctrl+C to stop)\n")
        print("-" * 70)

        self.monitoring = True
        last_count = 0

        try:
            while self.monitoring:
                log = self.network.get_conversation_log(100)

                # Show new messages
                if len(log) > last_count:
                    new_messages = log[last_count:]
                    for entry in new_messages:
                        timestamp = entry['timestamp'].split('T')[1].split('.')[0]
                        print(f"[{timestamp}] {entry['from']:15s} → {entry['to']:15s}: {entry['message'][:50]}")
                    last_count = len(log)

                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.monitoring = False
            print("\n\n⏸️  Monitoring stopped\n")

    async def chat_with_agent(self, agent_id: str, message: Optional[str] = None):
        """Chat with an agent"""
        if not message:
            message = input(f"Enter message for {agent_id}: ")

        print(f"\n💬 Sending to {agent_id}: {message}\n")
        result = await self.network.send_message('monitor', agent_id, message)
        if result:
            print(f"📨 Response: {result}\n")
        else:
            print(f"✅ Message sent (no response received)\n")

    async def reorient_agent(self, agent_id: str, instruction: Optional[str] = None):
        """Reorient an agent"""
        if not instruction:
            instruction = input(f"Enter reorientation instruction for {agent_id}: ")

        print(f"\n🔄 Reorienting {agent_id}...\n")
        result = await self.network.send_message('monitor', agent_id, f"REORIENTATION: {instruction}", msg_type='reorientation')
        print(f"✅ Reorientation sent: {instruction}\n")

    async def broadcast_message(self, message: Optional[str] = None):
        """Broadcast to all agents"""
        if not message:
            message = input("Enter broadcast message: ")

        print(f"\n📢 Broadcasting to all agents: {message}\n")
        await self.network.broadcast_message('monitor', message)
        print("✅ Broadcast sent\n")

    async def show_log(self, limit: int = 20):
        """Show conversation log"""
        log = self.network.get_conversation_log(limit)

        if not log:
            print("\n📝 No conversations yet\n")
            return

        print(f"\n📝 CONVERSATION LOG (last {len(log)} messages):\n")
        print("-" * 70)
        for entry in log[-limit:]:
            timestamp = entry['timestamp'].split('T')[1].split('.')[0]
            print(f"[{timestamp}] {entry['from']:15s} → {entry['to']:15s}")
            print(f"         {entry['message'][:60]}")
            print()

    async def run(self):
        """Run the CLI"""
        self.print_header()
        self.print_menu()

        while self.running:
            try:
                cmd = input("agent-monitor> ").strip().split()
                if not cmd:
                    continue

                command = cmd[0].lower()

                if command == 'quit' or command == 'exit':
                    print("\n👋 Goodbye!\n")
                    self.running = False
                elif command == 'list':
                    await self.list_agents()
                elif command == 'status':
                    await self.show_status()
                elif command == 'monitor':
                    await self.monitor_conversations()
                elif command == 'chat' and len(cmd) > 1:
                    agent_id = cmd[1]
                    message = ' '.join(cmd[2:]) if len(cmd) > 2 else None
                    await self.chat_with_agent(agent_id, message)
                elif command == 'reorient' and len(cmd) > 1:
                    agent_id = cmd[1]
                    instruction = ' '.join(cmd[2:]) if len(cmd) > 2 else None
                    await self.reorient_agent(agent_id, instruction)
                elif command == 'broadcast':
                    message = ' '.join(cmd[1:]) if len(cmd) > 1 else None
                    await self.broadcast_message(message)
                elif command == 'log':
                    limit = int(cmd[1]) if len(cmd) > 1 and cmd[1].isdigit() else 20
                    await self.show_log(limit)
                elif command == 'help':
                    self.print_menu()
                else:
                    print(f"❌ Unknown command: {command}. Type 'help' for commands.\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}\n")

async def main():
    """Main entry point"""
    monitor = AgentMonitorCLI()
    await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())