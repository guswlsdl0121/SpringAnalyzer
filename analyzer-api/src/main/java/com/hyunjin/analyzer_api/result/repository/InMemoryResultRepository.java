package com.hyunjin.analyzer_api.result.repository;

import com.hyunjin.analyzer_api.result.model.AnalysisResult;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class InMemoryResultRepository implements ResultRepository {

    // 프로젝트 ID를 키로, AnalysisResult를 값으로 저장
    private final Map<String, AnalysisResult> resultStore = new ConcurrentHashMap<>();

    /**
     * 분석 결과를 저장합니다.
     */
    @Override
    public AnalysisResult save(AnalysisResult result) {
        resultStore.put(result.projectId(), result);
        return result;
    }

    /**
     * 프로젝트 ID로 분석 결과를 조회합니다.
     */
    @Override
    public Optional<AnalysisResult> findByProjectId(String projectId) {
        return Optional.ofNullable(resultStore.get(projectId));
    }

    /**
     * 프로젝트 ID에 해당하는 분석 결과를 삭제합니다.
     */
    @Override
    public void deleteByProjectId(String projectId) {
        resultStore.remove(projectId);
    }
}
