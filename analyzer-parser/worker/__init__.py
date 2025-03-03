from .worker_pool import WorkerPool
from config import Config

# 작업자 풀 인스턴스 생성
worker_pool = WorkerPool(max_workers=Config.WORKER_POOL_SIZE)

__all__ = ['worker_pool']