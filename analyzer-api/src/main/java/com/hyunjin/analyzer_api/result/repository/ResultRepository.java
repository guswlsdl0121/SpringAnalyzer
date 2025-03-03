package com.hyunjin.analyzer_api.result.repository;

import com.hyunjin.analyzer_api.result.model.AnalysisResult;

import java.util.Optional;

/**
 * 분석 결과 저장소 인터페이스
 */
public interface ResultRepository {

    /**
     * 분석 결과를 저장합니다.
     *
     * @param result 저장할 분석 결과
     * @return 저장된 분석 결과
     */
    AnalysisResult save(AnalysisResult result);

    /**
     * 프로젝트 ID로 분석 결과를 조회합니다.
     *
     * @param projectId 프로젝트 ID
     * @return 분석 결과 (없는 경우 빈 Optional)
     */
    Optional<AnalysisResult> findByProjectId(String projectId);

    /**
     * 프로젝트 ID의 분석 결과를 삭제합니다.
     *
     * @param projectId 프로젝트 ID
     */
    void deleteByProjectId(String projectId);
}