import asyncio
from models import WorldState, CountryState, GovernmentType
from agent import AgentSystem
from logger import SimulationLogger

async def main():
    world = WorldState(turn=1, year=2025, countries={})
    
    usa = CountryState(
        name="アメリカ", economy=100.0, military=10.0,
        approval_rating=50.0, government_type=GovernmentType.DEMOCRACY,
        ideology="Test", press_freedom=0.8, area=1000.0
    )
    
    world.countries = {"アメリカ": usa}
    
    logger = SimulationLogger("TEST_UUID")
    agent_system = AgentSystem(logger=logger)
    
    prompt = agent_system._build_prompt("アメリカ", usa, world, {})
    
    if "他国はすべて滅亡または自国に併合され、世界はあなたの国によって完全に統一されました" in prompt:
        print("Success: Unified message found in prompt.")
    else:
        print("Failure: Unified message NOT found.")
        print("---Prompt Below---")
        print(prompt)

if __name__ == "__main__":
    asyncio.run(main())
