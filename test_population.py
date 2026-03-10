import asyncio
from main import initialize_world
from engine import WorldEngine
from logger import SimulationLogger
from agent import AgentSystem
import os

async def main():
    world = initialize_world()
    logger = SimulationLogger("TEST_POP_UUID")
    agent = AgentSystem(logger=logger)
    engine = WorldEngine(initial_state=world, analyzer=agent.sentiment_analyzer)
    
    print("=== 人口動態・軍事限界テスト (3ターン) ===")
    
    for _ in range(3):
        engine.process_pre_turn()
        print("\n⏳ 首脳AIが状況を分析し、行動を決定しています...")
        actions = agent.generate_actions(world)
        world = engine.process_turn(actions)
        print(f"\n--- Turn {world.turn-1} 完了 ---")
        for name, country in world.countries.items():
            gdp_per_capita = country.economy / max(0.1, country.population)
            print(f"[{name}] 人口: {country.population:.2f}M | 1人当GDP: {gdp_per_capita:.2f} | 経済: {country.economy:.1f} | 軍事: {country.military:.1f} | 支持率: {country.approval_rating:.1f}%")
        
        # 10%限界を超えるかチェック
        for name, country in world.countries.items():
            MOBILIZATION_CONSTANT = 3.4
            current_gdp_per_capita = country.economy / max(0.1, country.population)
            estimated_personnel = country.military / max(0.1, current_gdp_per_capita * MOBILIZATION_CONSTANT)
            mobilization_rate = estimated_personnel / max(0.1, country.population)
            if mobilization_rate > 0.1:
                print(f"🚨 {name} は動員限界10%を突破しています: 動員率 {mobilization_rate:.2%}")

if __name__ == "__main__":
    asyncio.run(main())
