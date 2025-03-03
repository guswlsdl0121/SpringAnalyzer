package com.hyunjin.analyzer_api.result.controller;

import com.hyunjin.analyzer_api.result.dto.ResultDetailResponse;
import com.hyunjin.analyzer_api.result.service.ResultService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/results")
@RequiredArgsConstructor
public class ResultController {

    private final ResultService resultService;

    /**
     * 프로젝트 ID로 분석 결과를 조회합니다.
     *
     * @param projectId 조회할 프로젝트 ID
     * @return 분석 결과 상세 정보
     */
    @GetMapping("/{projectId}")
    public ResponseEntity<ResultDetailResponse> getResult(@PathVariable String projectId) {
        return ResponseEntity.ok(resultService.findResultByProjectId(projectId));
    }
}