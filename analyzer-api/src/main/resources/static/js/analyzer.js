document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('uploadForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultContainer = document.getElementById('resultContainer');
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');

    // 결과 표시 요소
    const projectIdElement = document.getElementById('projectId');
    const filesProcessedElement = document.getElementById('filesProcessed');
    const summaryContentElement = document.getElementById('summaryContent');
    const timestampElement = document.getElementById('timestamp');

    // 모달 요소
    const analysisModal = new bootstrap.Modal(document.getElementById('analysisModal'));
    const analysisContentElement = document.getElementById('analysisContent');
    const viewFullAnalysisBtn = document.getElementById('viewFullAnalysisBtn');
    const copyAnalysisBtn = document.getElementById('copyAnalysisBtn');

    // 저장된 프로젝트 ID
    let currentProjectId = '';
    let analysisContent = '';

    // 폼 제출 이벤트 처리
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const fileInput = document.getElementById('projectFile');
        if (!fileInput.files[0]) {
            showError('업로드할 ZIP 파일을 선택해주세요.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        // UI 초기화
        hideResults();
        showLoading();

        // 파일 업로드 요청
        fetch('/analyze/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(text)
                    });
                }
                return response.text();
            })
            .then(data => {
                // 프로젝트 ID 추출
                const match = data.match(/프로젝트 ID: (.+)$/);
                if (match && match[1]) {
                    currentProjectId = match[1].trim();
                    // 2초 후 결과 조회
                    setTimeout(() => fetchResults(currentProjectId), 2000);
                } else {
                    throw new Error('프로젝트 ID를 찾을 수 없습니다.');
                }
            })
            .catch(error => {
                hideLoading();
                showError(error.message);
            });
    });

    // 결과 조회 함수
    function fetchResults(projectId) {
        fetch(`/results/${projectId}`)
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        // 결과가 아직 준비되지 않았으면 2초 후 다시 시도
                        setTimeout(() => fetchResults(projectId), 2000);
                        return null;
                    }
                    return response.text().then(text => {
                        throw new Error(text)
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    displayResults(data);
                }
            })
            .catch(error => {
                hideLoading();
                showError(`결과 조회 중 오류가 발생했습니다: ${error.message}`);
            });
    }

    // 결과 표시 함수
    function displayResults(data) {
        hideLoading();

        if (!data.success) {
            showError(data.error || '알 수 없는 오류가 발생했습니다.');
            return;
        }

        // 데이터 설정
        projectIdElement.textContent = data.projectId;
        filesProcessedElement.textContent = `${data.filesProcessed}개 파일 처리됨`;
        summaryContentElement.innerHTML = formatSummary(data.summaryContent);
        timestampElement.textContent = data.timestamp;

        // 전체 분석 내용 저장
        analysisContent = data.analysisContent;

        // 결과 컨테이너 표시
        resultContainer.classList.remove('hidden');
    }

    // 요약 내용 포맷팅
    function formatSummary(summaryText) {
        if (!summaryText) return '<p>요약 정보가 없습니다.</p>';

        // Markdown 스타일 변환 (간단한 처리)
        let formatted = summaryText
            // 헤딩 처리
            .replace(/^#\s+(.+)$/gm, '<h4>$1</h4>')
            .replace(/^##\s+(.+)$/gm, '<h5>$1</h5>')
            .replace(/^###\s+(.+)$/gm, '<h6>$1</h6>')
            // 리스트 처리
            .replace(/^-\s+(.+)$/gm, '<li>$1</li>')
            // 단락 처리
            .replace(/\n\n/g, '</p><p>')
            // 강조 처리
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // 리스트 항목 묶기
        formatted = formatted.replace(/<li>(.+?)<\/li>/g, function (match) {
            if (formatted.indexOf('<ul>') === -1) {
                return '<ul>' + match + '</ul>';
            }
            return match;
        });

        return '<p>' + formatted + '</p>';
    }

    // 전체 분석 내용 보기 버튼 이벤트
    viewFullAnalysisBtn.addEventListener('click', function () {
        analysisContentElement.textContent = analysisContent;
        analysisModal.show();
    });

    // 클립보드 복사 버튼 이벤트
    copyAnalysisBtn.addEventListener('click', function () {
        navigator.clipboard.writeText(analysisContent)
            .then(() => {
                // 복사 성공 표시
                const originalText = copyAnalysisBtn.innerHTML;
                copyAnalysisBtn.innerHTML = '<i class="bi bi-check"></i> 복사됨';
                copyAnalysisBtn.classList.add('btn-success');
                copyAnalysisBtn.classList.remove('btn-outline-secondary');

                // 2초 후 원래 상태로 복구
                setTimeout(() => {
                    copyAnalysisBtn.innerHTML = originalText;
                    copyAnalysisBtn.classList.remove('btn-success');
                    copyAnalysisBtn.classList.add('btn-outline-secondary');
                }, 2000);
            })
            .catch(err => {
                alert('클립보드 복사에 실패했습니다: ' + err);
            });
    });

    // 헬퍼 함수들
    function showLoading() {
        loadingIndicator.classList.remove('hidden');
    }

    function hideLoading() {
        loadingIndicator.classList.add('hidden');
    }

    function hideResults() {
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('hidden');
    }
});