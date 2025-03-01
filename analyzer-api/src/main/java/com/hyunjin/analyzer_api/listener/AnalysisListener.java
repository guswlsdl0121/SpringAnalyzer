package com.hyunjin.analyzer_api.listener;

import lombok.RequiredArgsConstructor;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class AnalysisListener {

    private final RabbitTemplate rabbitTemplate;

    @RabbitListener(queues = "analysis.queue")
    public void handleAnalysis(String message) {
        System.out.println("### Received Message: " + message);

        // 결과 메시지 응답
        String response = message + " - PROCESSED";
        rabbitTemplate.convertAndSend(
                "analyzer.exchange",
                "result.completed",
                response
        );
    }
}
