package com.hyunjin.analyzer_api.result.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ResultDetailResponse {
    private String projectId;
    private boolean success;
    private String error;
    private String analysisContent;
    private String summaryContent;
    private int filesProcessed;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime timestamp;
}
