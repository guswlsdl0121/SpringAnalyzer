package com.hyunjin.analyzer_api.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

// 메시지 발신
@RestController
@RequiredArgsConstructor
public class AnalysisController {

    private final RabbitTemplate rabbitTemplate;

    @PostMapping("/analyze")
    public String sendAnalysisRequest(@RequestParam String projectId) {
        // 분석 요청 메시지 발신
        rabbitTemplate.convertAndSend(
                "analyzer.exchange",
                "analysis.request",
                "Analysis Request for: " + projectId
        );
        return "Analysis request sent! ID: " + projectId;
    }
}