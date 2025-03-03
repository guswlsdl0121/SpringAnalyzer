package com.hyunjin.analyzer_api.result.model;

import com.hyunjin.analyzer_api.result.vo.AnalysisContent;
import com.hyunjin.analyzer_api.result.vo.SummaryContent;
import lombok.Builder;

import java.time.LocalDateTime;

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