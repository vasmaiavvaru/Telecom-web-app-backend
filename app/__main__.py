import multiprocessing

import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    if settings.ENVIRONMENT.lower() == "dev":
        workers_count = 1
        host = "127.0.0.1"
        reload = True
    else:
        workers_count = multiprocessing.cpu_count()
        host = "0.0.0.0"
        reload = False
    uvicorn.run(
        app="main:app",
        port=settings.BACKEND_PORT,
        host=host,
        workers=workers_count,
        reload=reload,
    )
