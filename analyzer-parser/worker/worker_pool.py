import logging
import concurrent.futures
import queue
import threading
import time

logger = logging.getLogger("worker.pool")

class Task:
    """작업 정보를 담는 클래스"""
    def __init__(self, task_id, func, args=None, kwargs=None):
        self.task_id = task_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.result = None
        self.error = None
        self.status = "pending"  # pending, running, completed, failed
        self.start_time = None
        self.end_time = None

class WorkerPool:
    """스레드 기반 작업자 풀 구현"""
    def __init__(self, max_workers=4, queue_size=100):
        self.max_workers = max_workers
        self.task_queue = queue.Queue(maxsize=queue_size)
        self.tasks = {}  # task_id -> Task
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = False
        self.worker_thread = None
        
        # 통계 정보
        self.stats = {
            "submitted": 0,
            "completed": 0,
            "failed": 0,
            "avg_processing_time": 0,
            "total_processing_time": 0
        }
        self.stats_lock = threading.Lock()
    
    def start(self):
        """작업자 풀 시작"""
        if self.is_running:
            logger.warning("작업자 풀이 이미 실행 중입니다")
            return
            
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.worker_thread.start()
        logger.info(f"작업자 풀 시작됨 (max_workers={self.max_workers})")
    
    def _process_tasks(self):
        """작업 대기열에서 작업을 가져와 실행"""
        futures = {}  # future -> task_id
        
        while self.is_running:
            try:
                # 처리 완료된 Future 확인 및 정리
                done_futures = [f for f in futures.keys() if f.done()]
                for future in done_futures:
                    task_id = futures.pop(future)
                    task = self.tasks.get(task_id)
                    
                    if task:
                        task.end_time = time.time()
                        try:
                            task.result = future.result()
                            task.status = "completed"
                            
                            # 통계 업데이트
                            with self.stats_lock:
                                self.stats["completed"] += 1
                                processing_time = task.end_time - task.start_time
                                self.stats["total_processing_time"] += processing_time
                                self.stats["avg_processing_time"] = (
                                    self.stats["total_processing_time"] / self.stats["completed"]
                                )
                                
                            logger.info(f"Task {task_id} 완료: {processing_time:.2f}초 소요")
                        except Exception as e:
                            task.error = str(e)
                            task.status = "failed"
                            
                            # 통계 업데이트
                            with self.stats_lock:
                                self.stats["failed"] += 1
                                
                            logger.error(f"Task {task_id} 실패: {str(e)}")
                
                # 작업자 여유 공간 확인
                available_workers = self.max_workers - len(futures)
                
                # 새 작업 제출 (가능한 만큼)
                for _ in range(min(available_workers, self.task_queue.qsize())):
                    task = self.task_queue.get_nowait()
                    
                    task.start_time = time.time()
                    task.status = "running"
                    
                    # 작업 제출
                    future = self.executor.submit(
                        task.func, *task.args, **task.kwargs
                    )
                    futures[future] = task.task_id
                    
                    logger.debug(f"Task {task.task_id} 실행 시작")
                    
                # 잠시 대기
                time.sleep(0.1)
                    
            except queue.Empty:
                # 대기열이 비어있으면 잠시 대기
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"작업 처리 중 오류 발생: {str(e)}", exc_info=True)
                time.sleep(1)
    
    def submit(self, task_id, func, *args, **kwargs):
        """새 작업 제출"""
        if not self.is_running:
            raise RuntimeError("작업자 풀이 실행 중이 아닙니다")
            
        task = Task(task_id, func, args, kwargs)
        self.tasks[task_id] = task
        
        # 통계 업데이트
        with self.stats_lock:
            self.stats["submitted"] += 1
        
        try:
            self.task_queue.put(task, block=False)
            logger.info(f"Task {task_id} 대기열에 추가됨")
            return task_id
        except queue.Full:
            logger.error(f"작업 대기열이 가득 찼습니다. Task {task_id} 거부됨")
            self.tasks.pop(task_id)
            raise RuntimeError("작업 대기열이 가득 찼습니다")
    
    def get_task_status(self, task_id):
        """특정 작업의 상태 확인"""
        task = self.tasks.get(task_id)
        if not task:
            return None
            
        return {
            "id": task.task_id,
            "status": task.status,
            "start_time": task.start_time,
            "end_time": task.end_time,
            "duration": (task.end_time - task.start_time) if task.end_time else None,
            "error": task.error
        }
    
    def get_stats(self):
        """작업자 풀 통계 반환"""
        with self.stats_lock:
            return dict(self.stats)
    
    def stop(self):
        """작업자 풀 중지"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # 스레드 종료 대기
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        
        # 작업자 풀 종료
        self.executor.shutdown(wait=False)
        
        logger.info("작업자 풀이 종료되었습니다")