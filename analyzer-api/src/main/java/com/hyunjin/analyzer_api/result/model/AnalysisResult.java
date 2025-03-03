package com.hyunjin.analyzer_api.result.model;

import com.hyunjin.analyzer_api.result.vo.AnalysisContent;
import com.hyunjin.analyzer_api.result.vo.SummaryContent;
import lombok.Builder;

import java.time.LocalDateTime;

/**
 * 분석 결과를 나타내는 레코드 클래스.
 *
 * @param projectId       프로젝트 ID
 * @param success         분석 성공 여부
 * @param error           실패 시 발생한 에러 메시지 (성공 시 null)
 * @param analysisContent 분석 내용
 * @param summaryContent  요약 내용
 * @param filesProcessed  처리된 파일 수
 * @param timestamp       결과 생성 시간
 */
@Builder
public record AnalysisResult(
        String projectId,
        boolean success,
        String error,
        AnalysisContent analysisContent,
        SummaryContent summaryContent,
        int filesProcessed,
        LocalDateTime timestamp) {
}
