"""
Put here any Python code that must be run before application startup.
It is included in `init.sh` script.

By default, `main` create a superuser if not exists
"""

import asyncio

from sqlalchemy import select

from app.core import config, security
from app.core.session import async_session
from app.models import User


async def main() -> None:
    print("Start initial data")
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.mobile_number == config.settings.FIRST_SUPERUSER_MOBILE_NUMBER
            )
        )
        user = result.scalars().first()

        if user is None:
            new_superuser = User(
                email=config.settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=security.get_password_hash(
                    config.settings.FIRST_SUPERUSER_PASSWORD
                ),
                mobile_number=config.settings.FIRST_SUPERUSER_MOBILE_NUMBER,
                first_name=config.settings.FIRST_SUPERUSER_FIRST_NAME,
                last_name=config.settings.FIRST_SUPERUSER_LAST_NAME,
                postal_address=config.settings.FIRST_SUPERUSER_POSTAL_ADDRESS,
                active_plan_id=config.settings.FIRST_SUPERUSER_ACTIVE_PLAN_ID,
            )
            session.add(new_superuser)
            await session.commit()
            print("Superuser was created")
        else:
            print("Superuser already exists in database")

        print("Initial data created")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
