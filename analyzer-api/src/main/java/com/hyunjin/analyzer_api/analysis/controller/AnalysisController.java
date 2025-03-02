package com.hyunjin.analyzer_api.analysis.controller;

import com.hyunjin.analyzer_api.analysis.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

// 메시지 발신
@RestController
@RequiredArgsConstructor
public class AnalysisController {
    private final AnalysisService analysisService;

    @PostMapping("/analyze/upload")
    public ResponseEntity<String> analyzeProject(@RequestParam("file") MultipartFile file) {
        String projectId = analysisService.uploadProject(file);
        return ResponseEntity.ok("프로젝트가 업로드되어 분석 대기열에 추가되었습니다. 프로젝트 ID: " + projectId);
    }
}