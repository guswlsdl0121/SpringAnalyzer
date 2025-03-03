package com.hyunjin.analyzer_api.result.repository;

import com.hyunjin.analyzer_api.result.model.AnalysisResult;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class InMemoryResultRepository implements ResultRepository {

    private final Map<String, AnalysisResult> resultStore = new ConcurrentHashMap<>();

    @Override
    public AnalysisResult save(AnalysisResult result) {
        resultStore.put(result.projectId(), result);
        return result;
    }

    @Override
    public Optional<AnalysisResult> findByProjectId(String projectId) {
        return Optional.ofNullable(resultStore.get(projectId));
    }

    @Override
    public void deleteByProjectId(String projectId) {
        resultStore.remove(projectId);
    }
}