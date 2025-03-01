package com.hyunjin.analyzer_api.listener;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class ResultListener {

    @RabbitListener(queues = "result.queue")
    public void handleResult(String result) {
        System.out.println("### Final Result: " + result);
    }
}
