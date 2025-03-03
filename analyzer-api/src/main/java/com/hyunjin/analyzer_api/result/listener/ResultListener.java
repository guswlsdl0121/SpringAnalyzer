package com.hyunjin.analyzer_api.result.listener;

import com.hyunjin.analyzer_api.common.messaging.constants.RabbitMQConstants;
import com.hyunjin.analyzer_api.common.util.MessageSerializer;
import com.hyunjin.analyzer_api.result.dto.ResultResponse;
import com.hyunjin.analyzer_api.result.service.ResultService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class ResultListener {

    private final MessageSerializer messageSerializer;
    private final ResultService resultService;

    @RabbitListener(queues = RabbitMQConstants.RESULT_QUEUE)
    public void handleResultMessage(String message) {
        ResultResponse resultResponse = messageSerializer.deserializeResultResponse(message);
        resultService.saveResult(resultResponse);
    }
}