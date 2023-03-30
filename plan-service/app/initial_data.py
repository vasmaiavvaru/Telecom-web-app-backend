"""
Put here any Python code that must be run before application startup.
It is included in `init.sh` script.

By default, `main` create a superuser if not exists
"""

import asyncio
import json

from sqlalchemy import select

from app.core.session import async_session
from app.models import Plans


async def main() -> None:
    print("Start initial data")
    with open("../all_plans.json", "r") as f:
        all_data = json.load(f)
    async with async_session() as session:
        for item in all_data:
            result = await session.execute(
                select(Plans).where(Plans.name == item["name"])
            )
            plan = result.scalars().first()

            if plan is None:
                new_plan = Plans(**item)
                session.add(new_plan)
                await session.commit()
                print(f"Plan {item['name']} was created")
            else:
                print(f"Plan {item['name']} already exists in database")
        print("Initial data created")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
