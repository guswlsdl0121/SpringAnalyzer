package com.hyunjin.analyzer_api.common.messaging.constants;

public final class RabbitMQConstants {
    // Exchange
    public static final String ANALYZER_EXCHANGE = "analyzer.exchange";
    // Routing Keys
    public static final String ROUTING_ANALYSIS_REQUEST = "analysis.request";
    public static final String ROUTING_ANALYSIS_UPLOAD = "analysis.upload";
    public static final String ROUTING_RESULT_COMPLETED = "result.completed";
    public static final String ROUTING_RESULT_ERROR = "result.error";
    // Queue Names
    public static final String ANALYSIS_QUEUE = "analysis.queue";
    public static final String RESULT_QUEUE = "result.queue";

    private RabbitMQConstants() {
    }
}