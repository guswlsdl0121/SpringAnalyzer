package com.hyunjin.analyzer_api.result.dto;

import lombok.Data;

@Data
public class ResultResponse {
    private String projectId;
    private boolean success;
    private String error;
    private String analysisContent;
    private String summaryContent;
    private int filesProcessed;
}