package com.hyunjin.analyzer_api.common.messaging.config;

import com.hyunjin.analyzer_api.common.messaging.constants.RabbitMQConstants;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    // 분석 요청 큐
    @Bean
    Queue analysisQueue() {
        return new Queue(RabbitMQConstants.ANALYSIS_QUEUE, true);
    }

    // 결과 응답 큐
    @Bean
    Queue resultQueue() {
        return new Queue(RabbitMQConstants.RESULT_QUEUE, true);
    }

    // 토픽 익스체인지
    @Bean
    TopicExchange exchange() {
        return new TopicExchange(RabbitMQConstants.ANALYZER_EXCHANGE);
    }

    // 큐-익스체인지 바인딩
    @Bean
    Binding analysisBinding(Queue analysisQueue, TopicExchange exchange) {
        return BindingBuilder.bind(analysisQueue)
                .to(exchange)
                .with("analysis.*");
    }

    @Bean
    Binding resultBinding(Queue resultQueue, TopicExchange exchange) {
        return BindingBuilder.bind(resultQueue)
                .to(exchange)
                .with("result.*");
    }
}